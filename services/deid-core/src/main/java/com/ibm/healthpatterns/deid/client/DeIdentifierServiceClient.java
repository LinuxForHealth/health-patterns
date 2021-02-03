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
package com.ibm.healthpatterns.deid.client;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.util.regex.Pattern;

import org.apache.commons.io.IOUtils;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
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

	private CloseableHttpClient httpclient;
	private String requestTemplate;
	
	/**
	 * 
	 */
	public DeIdentifierServiceClient() {
		httpclient = HttpClients.createDefault();
		try {
			requestTemplate = IOUtils.toString(this.getClass().getResourceAsStream("/de-id-request.json"), Charset.defaultCharset());
		} catch (IOException e) {
			System.err.println("Could not read de-identify service request. The de-id client won't work: " + e.getMessage());
		}
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
		HttpPost postRequest = new HttpPost("http://13c5f68f-us-south.lb.appdomain.cloud:8080/api/v1/deidentification");
        config = prepareRequestBodyElements(config);
        data = prepareRequestBodyElements(data);
        String requestBody = requestTemplate.replace("#CONFIG", config).replace("#DATA", data);
        StringEntity entity = new StringEntity(requestBody, "UTF-8");
        entity.setContentType("application/json");
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

	/**
	 * 
	 * @param args
	 * @throws DeIdentifierClientException
	 */
	public static void main(String[] args) throws DeIdentifierClientException {
		InputStream configInputStream = DeIdentifierServiceClient.class.getResourceAsStream("/de-id-config.json");
		String configJson = null;
		try {
			configJson = IOUtils.toString(configInputStream, Charset.defaultCharset());
		} catch (IOException e) {
			System.err.println("Could not read de-identifier service configuration");
			e.printStackTrace();
		}
		System.out.println(configJson);
		DeIdentifierServiceClient client = new DeIdentifierServiceClient();
		client.deIdentify("{\"id\":\"1234\", \"resourceType\": \"Device\", \"patient\":{ \"display\":\"Patient Zero\", \"reference\":\"1234\"}}", configJson);
	}
}
