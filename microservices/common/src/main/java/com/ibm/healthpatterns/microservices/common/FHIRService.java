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
package com.ibm.healthpatterns.microservices.common;

import java.io.IOException;

import java.io.StringWriter;
import java.io.Writer;
import java.net.MalformedURLException;
import java.net.URL;

import org.apache.http.HttpEntity;
import org.apache.http.HttpStatus;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.client.api.IClientInterceptor;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.rest.client.interceptor.BasicAuthInterceptor;

/**
 * A {@link FHIRService} is a class that provides some functionality using a FHIR Server.
 * <p>
 * It provides an implementation of a {@link #healthCheck(StringWriter)} that allows consumers 
 * to know whether the FHIR Server is available, and extenders can extend the method to complement
 * additional health checks to other services that may be used.
 *  
 * @author Luis A. García
 */
public class FHIRService {

	/**
	 * The path to check the FHIR server health.
	 */
	private static final String FHIR_HEALTHCHECK_PATH = "/$healthcheck";
	
	/**
	 * A FHIR resource's Bundle resource type
	 */
	private static final String BUNDLE_RESOURCE_TYPE = "Bundle";
	
	/**
	 * A FHIR resource's 'resource' field 
	 */
	protected static final String RESOURCE_OBJECT = "resource";

	/**
	 * A FHIR resource's 'resourceType' field 
	 */
	protected static final String RESOURCE_TYPE_OBJECT = "resourceType";

	/**
	 * A FHIR resource's 'entry' field
	 */
	protected static final String ENTRY_OBJECT = "entry";

	protected ObjectMapper jsonDeserializer;
	
	protected IGenericClient fhirClient;
	private CloseableHttpClient rawFhirClient;

	/**
	 * Creates a FHIR Service backed by the given FHIR server.
	 * 
	 * @param fhirServerURL the full FHIR server base URL, e.g. http://fhir-us-south.lb.appdomain.cloud:8080/fhir-server/api/v4
	 * @param fhirServerUsername the FHIR server username
	 * @param fhirServerPassword the FHIR server password
	 */
	public FHIRService(String fhirServerURL, String fhirServerUsername, String fhirServerPassword) {
		jsonDeserializer = new ObjectMapper();
		initializeFhirClients(fhirServerURL, fhirServerUsername, fhirServerPassword);
	}
	
	/**
	 * Initializes the FHIR Clients. There is an official Hapi FHIR Client and a plain Apache HttpClient that
	 * get initialized to connect to the FHIR Server.
	 *  
	 * @param fhirServerURL the FHIR server URL
	 * @param fhirServerUsername the FHIR server username
	 * @param fhirServerPassword the FHIR server password
	 */
	private void initializeFhirClients(String fhirServerURL, String fhirServerUsername, String fhirServerPassword) {
		// Initialize the Hapi FHIR client to perform all general FHIR operations
		FhirContext context = FhirContext.forR4();
		// Large synthea Bundles need a longer timeout than the default
		context.getRestfulClientFactory().setSocketTimeout(200 * 1000);
		fhirClient = context.newRestfulGenericClient(fhirServerURL);
		// https://hapifhir.io/hapi-fhir/docs/interceptors/built_in_client_interceptors.html#section2
		IClientInterceptor authInterceptor = new BasicAuthInterceptor(fhirServerUsername, fhirServerPassword);
		fhirClient.registerInterceptor(authInterceptor);
		
		// Initialize the raw FHIR client to perform IBM specific FHIR operations, e.g. $healthcheck
		if (fhirServerUsername == null) {
			rawFhirClient = HttpClients.createDefault();
		} else {
			CredentialsProvider credentialsPovider = new BasicCredentialsProvider();
			URL url;
			try {
				url = new URL(fhirClient.getServerBase());
			} catch (MalformedURLException e) {
				System.err.println("Incorrect FHIR server URL provided: " + e.getMessage());
				return;
			}
			credentialsPovider.setCredentials(new AuthScope(url.getHost(), url.getPort()), new UsernamePasswordCredentials(fhirServerUsername, fhirServerPassword));
			rawFhirClient = HttpClients.custom()
					.setDefaultCredentialsProvider(credentialsPovider)
					.build();
		}
	}

	/**
	 * Checks the health of the underlying services using the services' corresponding health check APIs.
	 * <p>
	 * If the services are healthy the service returns true, otherwise the services return false.
	 * In either case the given {@link Writer} will be used by the method to populate more information about
	 * what exactly is went wrong.
	 * <p>
	 * It is possible for subclasses to call this method and pick up on their specific health check as needed
	 * if other services other than a FHIR server is used. 
	 *  
	 * @param status an optional {@link StringWriter} where status will be logged 
	 * @return true if the service is healthy, false otherwise
	 */
	public boolean healthCheck(StringWriter status) {
		boolean errors = false;
		if (status == null) {
			status = new StringWriter();
		}
		if (!checkFHIRHealth(status)) {
			errors = true;
		}
		return !errors;
	}

	/**
	 * Check the health of the FHIR server.
	 * 
	 * @param status the status to write to
	 * @return true if FHIR server is OK, false otherwise
	 */
	private boolean checkFHIRHealth(StringWriter status) {
		boolean errors = false;
		HttpGet getRequest = new HttpGet(fhirClient.getServerBase() + FHIR_HEALTHCHECK_PATH);
		try (CloseableHttpResponse response = rawFhirClient.execute(getRequest)) {
	    	EntityUtils.consume(response.getEntity());
	        if (response.getStatusLine().getStatusCode() == HttpStatus.SC_OK) {
	        	status.write("FHIR Server OK!\n");
	        } else if (response.getStatusLine().getStatusCode() == HttpStatus.SC_UNAUTHORIZED) {
	        	status.write("The FHIR Server credentials are incorrect, please verify:\n");
	        	status.write("> " + getRequest.getRequestLine() + "\n");
	        	HttpEntity entity = response.getEntity();
	        	String responseString = EntityUtils.toString(entity, "UTF-8");
	        	status.write("< " + response.getStatusLine().toString() + "\n");
	        	status.write(responseString + "\n");
	        	errors = true;
	        } else {
	        	status.write("There is an unknown problem in the FHIR Server:\n");
	        	status.write("> " + getRequest.getRequestLine() + "\n");
	        	HttpEntity entity = response.getEntity();
	        	String responseString = EntityUtils.toString(entity, "UTF-8");
	        	status.write("< " + response.getStatusLine().toString() + "\n");
	        	status.write(responseString + "\n");
	        	errors = true;
	        }
	    } catch (ClientProtocolException e) {
	    	status.write("There is a problem in the FHIR Server.\n");
	    	status.write("HTTP protocol error executing request: " + getRequest.getRequestLine() + " - " + e.getMessage() + "\n");
	    	errors = true;
		} catch (IOException e) {
			status.write("There is a problem in the FHIR Server.\n");
			status.write("HTTP I/O connection error executing request: " + getRequest.getRequestLine() + " - " + e.getMessage() + "\n");
			errors = true;
		}
		return !errors;
	}

	/**
	 * Determines whether the given {@link JsonNode} represents a FHIR Bundle
	 *  
	 * @param jsonNode the json to check
	 * @return true if the 'resourceType' of the given FHIR resource is Bundle, false otherwise
	 */
	protected boolean isBundle(JsonNode jsonNode) {
		return BUNDLE_RESOURCE_TYPE.equals(getResourceType(jsonNode));
	}

	/**
	 * Extract the resource type from the given JSON object.
	 * 
	 * @param json the json resource
	 * @return the resource type, or null if no resource type is included in this JSON
	 */
	protected String getResourceType(JsonNode json) {
		JsonNode resourceType = json.findValue(RESOURCE_TYPE_OBJECT);
		if (resourceType == null) {
			return null;
		}
		return resourceType.asText();
	}

	/**
	 * @return the fhirClient used by this {@link FHIRService}
	 */
	public IGenericClient getFhirClient() {
		return fhirClient;
	}
}