/*
 * (C) Copyright IBM Corp. 2021
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.ibm.healthpatterns.microservices.deid.client;

import java.io.IOException;
import java.io.StringWriter;
import java.io.Writer;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.regex.Pattern;

import org.apache.commons.io.IOUtils;
import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

/**
 * A {@link DeIdentifierServiceClient} is a wrapper for the de-identification REST API.
 * <p>
 * It works at the same level of abstraction as the REST API in that it uses a de-id configuration and it sends in
 * the JSON to de-identify, but it abstracts away the lower level HTTP connection and escaping of the masking and
 * body that working directly with the REST API requires.  
 * 
 * @author Luis A. García
 */
public class DeIdentifierServiceClient {

	/**
	 * The URI path for the de-id service
	 */
	private static final String DEIDENTIFICATION_PATH = "/deidentification";

	/**
	 * The URI path for the health check service
	 */
	private static final String HEALTH_PATH = "/health";

	/**
	 * The file that contains a template for the de-id JSON request
	 */
	private static final String DEID_REQUEST_JSON_TEMPLATE = "/de-id-request.json";

	/**
	 * The marker in the de-id JSON request that will have the data to process.
	 */
	private static final String DATA_MARKER = "#DATA";

	/**
	 * The marker in the de-id JSON request that will have the de-id masking config.  
	 */
	private static final String CONFIG_MARKER = "#CONFIG";

	private CloseableHttpClient httpclient;
	private String requestTemplate;
	private String url;

	/**
	 * Create a new {@link DeIdentifierServiceClient} talking to the de-id service on the given URL.
	 * 
	 * @param url the full url of the de-id service, e.g. http://13c5f68f-us-south.lb.appdomain.cloud:8080
	 */
	public DeIdentifierServiceClient(String url) {
		httpclient = HttpClients.createDefault();
		try {
			requestTemplate = IOUtils.toString(this.getClass().getResourceAsStream(DEID_REQUEST_JSON_TEMPLATE), Charset.defaultCharset());
		} catch (IOException e) {
			System.err.println("Could not read de-identify service request. The de-id client won't work: " + e.getMessage());
		}
		this.url = url;
	}

	/**
	 * Checks the health of the deid service using the corresponding health check API.
	 * If the services are healthy the service returns true, otherwise the services return false.
	 * In either case the given {@link Writer} will be used by the method to populate more information about
	 * what exactly is went wrong.
	 *  
	 * @param status an optional {@link StringWriter} where status will be logged 
	 * @return true if the service is healthy, false otherwise
	 */
	public boolean healthCheck(StringWriter status) {
		HttpGet getRequest = new HttpGet(url + HEALTH_PATH);
		try (CloseableHttpResponse response = httpclient.execute(getRequest)) {
			EntityUtils.consume(response.getEntity());
			if (response.getStatusLine().getStatusCode() == 200) {
				status.write("De-id service OK!\n");
				return true;
			} else {
				status.write("There is an unknown problem in the de-id service.\n");
				status.write("> " + getRequest.getRequestLine() + "\n");
				HttpEntity entity = response.getEntity();
				String responseString = EntityUtils.toString(entity, "UTF-8");
				status.write("< " + response.getStatusLine().toString() + "\n");
				status.write(responseString + "\n");
			}
		} catch (ClientProtocolException e) {
			status.write("There is a problem in the de-id service.\n");
			status.write("HTTP protocol error executing request: " + getRequest.getRequestLine() + " - " + e.getMessage() + "\n");
		} catch (IOException e) {
			status.write("There is a problem in the de-id service.\n");
			status.write("HTTP I/O connection error executing request: " + getRequest.getRequestLine() + " - " + e.getMessage() + "\n");
		}		
		return false;
	}

	/**
	 * De-identifies the given data with the given de-identification configuration.
	 * 
	 * @param data the data to de-identify
	 * @param config the masking configuration for the de-id service
	 * @return the de-identified data
	 * @throws DeIdentifierClientException if there is an error executing the HTTP request
	 */
	public String deIdentify(String data, String config) throws DeIdentifierClientException {
		HttpPost postRequest = new HttpPost(url + DEIDENTIFICATION_PATH);
		config = prepareRequestBodyElements(config);
		data = prepareRequestBodyElements(data);
		String requestBody = requestTemplate.replace(CONFIG_MARKER, config).replace(DATA_MARKER, data);
		StringEntity entity = new StringEntity(requestBody, StandardCharsets.UTF_8.name());
		entity.setContentType(ContentType.APPLICATION_JSON.getMimeType());
		postRequest.setEntity(entity);
		//        System.out.println("> " + postRequest.getRequestLine());
		try (CloseableHttpResponse response = httpclient.execute(postRequest)) {
			String responseBody = IOUtils.toString(response.getEntity().getContent(), Charset.defaultCharset());
			//            System.out.println("< " + response.getStatusLine() + ": " + responseBody);
			EntityUtils.consume(response.getEntity());
			return responseBody;
		} catch (ClientProtocolException e) {
			throw new DeIdentifierClientException("HTTP protocol error executing request " + postRequest.getRequestLine(), e);
		} catch (IOException e) {
			throw new DeIdentifierClientException("HTTP I/O connection error executing request " + postRequest.getRequestLine(), e);
		}
	}

	/**
	 * The De-ID REST API expects the FHIR resource to de-identify and the masking configuration 
	 * in the request to be a string containing JSON, instead of an actual JSON object. 
	 * 
	 * <p>
	 * In other words the service expects:
	 * <code>
	 * {
	 *   "data": "{\"some\":\"json\"}"
	 * }
	 * </code>
	 * <p>
	 * Instead of:
	 * <code>
	 * {
	 *  "data": { "some": "json"}
	 * }
	 * </code>
	 * <p>
	 * That is why we need to escape the quotes here.
	 * <p>
	 * Additionally, the service expects that there will be no new-line characters in the json.
	 * 
	 * @param json the json to escape into text
	 * @return the escaped json
	 */
	private String prepareRequestBodyElements(String json) {
		return json.replaceAll("(\r|\n)", "").replaceAll("(?s)" + Pattern.quote("\""), "\\\\\"");
	}
}
