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
package com.ibm.healthpatterns.deid;

import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.nio.charset.Charset;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.Resource;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.ibm.healthpatterns.core.FHIRService;
import com.ibm.healthpatterns.deid.client.DeIdentifierClientException;
import com.ibm.healthpatterns.deid.client.DeIdentifierServiceClient;

import ca.uhn.fhir.parser.IParser;
import ca.uhn.fhir.rest.api.MethodOutcome;
import ca.uhn.fhir.rest.server.exceptions.BaseServerResponseException;

/**
 * A {@link DeIdentifier} de-identifies JSON FHIR resources using the Alvearie de-identification service, 
 * and subsequently pushes the de-identified resources to a designated FHIR server.
 * <p>
 * The de-identification results in a new {@link DeIdentification} object which contains the elements that 
 * may be important to a requester of a de-identify operation such as
 * the initial resource, the de-identified resource, and any FHIR server responses.  
 * <p>
 * This class requires the connection information for the Alvearie deid service and to the FHIR server.
 * 
 * @author Luis A. García
 */
public class DeIdentifier extends FHIRService {

	/**
	 * The file that contains the masking config that will be used to configure the de-id service.
	 */
	private static final String DEID_CONFIG_JSON = "/de-id-config.json";

	/**
	 * The types for which there is masking configuration ion this {@link DeIdentifier}s masking config.
	 */
	private static final String[] DEIDENTIFIABLE_FHIR_TYPES = new String[] {"Patient", "Procedure", "Condition", "Observation", "MedicationRequest", "Encounter"};
	
	/**
	 * The de-id service response data field.
	 */
	private static final String DATA_OBJECT = "data";

	/**
	 * A FHIR resource's 'text' field
	 */
	private static final String TEXT_OBJECT = "text";

	DeIdentifierServiceClient deidClient;
	String configJson;
	
	/**
	 * Create a {@link DeIdentifier} that uses the given de-id and FHIR connection information.
	 * 
	 * @param deidServiceURL the full de-id service base URL, e.g. http://deid-us-south.lb.appdomain.cloud:8080/api/v1 
	 * @param fhirServerURL the full FHIR server base URL, e.g. http://fhir-us-south.lb.appdomain.cloud:8080/fhir-server/api/v4
	 * @param fhirServerUsername the FHIR server username
	 * @param fhirServerPassword the FHIR server password
	 */
	public DeIdentifier(String deidServiceURL, String fhirServerURL, String fhirServerUsername, String fhirServerPassword) {
		super(fhirServerURL, fhirServerUsername, fhirServerPassword);
		deidClient = new DeIdentifierServiceClient(deidServiceURL);
		InputStream configInputStream = this.getClass().getResourceAsStream(DEID_CONFIG_JSON);
		try {
			configJson = IOUtils.toString(configInputStream, Charset.defaultCharset());
		} catch (IOException e) {
			System.err.println("Could not read de-identifier service configuration, the DeIdentifier won't be functional");
		}
	}

	public DeIdentifier(String deidServiceURL, String fhirServerURL, String fhirServerUsername, String fhirServerPassword, InputStream configInputStream) {
		super(fhirServerURL, fhirServerUsername, fhirServerPassword);
		deidClient = new DeIdentifierServiceClient(deidServiceURL);
		try {
			configJson = IOUtils.toString(configInputStream, Charset.defaultCharset());
		} catch (IOException e) {
			System.err.println("Could not read de-identifier service configuration, the DeIdentifier won't be functional");
		}
	}

	/* (non-Javadoc)
	 * @see com.ibm.healthpatterns.core.FHIRService#healthCheck(java.io.StringWriter)
	 */
	@Override
	public boolean healthCheck(StringWriter status) {
		boolean errors = !super.healthCheck(status);
		if (configJson == null) {
			status.write("It wasn't possible to load the default de-id configuraiton. Likely this is a problem with the de-id JAR.\n");
			errors = true;
		}
		if (!deidClient.healthCheck(status)) {
			errors = true;
		}
		return !errors;
	}
	
	/**
	 * De-identifies the FHIR resource represented in the given JSON input stream, and subsequently pushes the de-identified
	 * resources to a FHIR server.
	 * 
	 * @param resourceInputStream the input stream to the FHIR resource JSON
	 *                            representation
	 * @return the result of the de-identification operation 
	 * @throws DeIdentifierException if there is a problem parsing the given JSON,
	 *                               de-identification operation or saving the resulting resource to FHIR
	 * @throws IOException if there is an IO problem reading the input stream 
	 */
	public DeIdentification deIdentify(InputStream resourceInputStream) throws DeIdentifierException, IOException {
		JsonNode jsonNode;
		try {
			jsonNode = jsonDeserializer.readTree(resourceInputStream);
		} catch (JsonParseException e) {
			throw new DeIdentifierException("The given input stream did not contain valid JSON.", e);
		}
		if (!(jsonNode instanceof ObjectNode)) {
			throw new DeIdentifierException("The FHIR resource did not contain a valid JSON object, likely it was a JSON array. Currently only proper FHIR resources are supported");
		}
		DeIdentification deidentification = new DeIdentification();
		deidentification.setOriginalResource(jsonNode);
		JsonNode deIdentifiedJson = deIdentify(jsonNode);
		deidentification.setDeIdentifiedResource(deIdentifiedJson);
		pushToFHIR(deIdentifiedJson, deidentification);
		return deidentification;
	}	
	
	/**
	 * De-identifies the FHIR resource represented in the given JSON object.
	 * 
	 * @param fhirResource the FHIR resource JSON representation
	 * @return the de-dentified FHIR resource
	 * @throws DeIdentifierException if there is a problem with the
	 *                               de-identification operation
	 */
	private JsonNode deIdentify(JsonNode fhirResource) throws DeIdentifierException {
		JsonNode deIdentifiedFhirResource = fhirResource.deepCopy();
		if (isBundle(deIdentifiedFhirResource)) {
			System.out.println("De-identifying bundle...");
			deIdentifyBundle(deIdentifiedFhirResource);
			System.out.println("De-identifying bundle done!");
		} else {
			System.out.println("De-identifying single resource...");
			deIdentifiedFhirResource = deIdentifyResource(deIdentifiedFhirResource);
			System.out.println("De-identifying single resource done!");
		}
		return deIdentifiedFhirResource;
	}

	/**
	 * This method de-identifies the resources in the given Bundle, and pushes them to a FHIR server.
	 * 
	 * @param jsonNode with the FHIR Bundle to de-identify
	 * @throws DeIdentifierException if the given bundle does not contain proper FHIR resources
	 */
	private void deIdentifyBundle(JsonNode jsonNode) throws DeIdentifierException {
		ArrayNode resources = (ArrayNode) jsonNode.findValue(ENTRY_OBJECT);
		for (int i = 0; i < resources.size(); i++) {
			ObjectNode resourceEntry = (ObjectNode) resources.get(i);
			JsonNode resource = resourceEntry.get(RESOURCE_OBJECT);
			if (resource == null) {
				throw new IllegalArgumentException("It is expected that a resource entry within a Bundle be rooted at 'resource'.");
			}
			JsonNode deIdentifiedResource = deIdentifyResource(resource);
			if (deIdentifiedResource == null) {
				continue;
			}
			// Replace the resource object with the de-identified JSON
			((ObjectNode) resourceEntry).set(RESOURCE_OBJECT, deIdentifiedResource);
		}
	}

	/**
	 * De-identifies the given single FHIR resource represented as a {@link JsonNode}.
	 *  
	 * @param resource the FHIR resource to de-identify
	 * @return the de-identified resource, or null if this resource is not of a type that can be de-identified
	 * @throws DeIdentifierException if there is an error in the de-identification REST API or parsing the JSON
	 * @throws IllegalArgumentException if the given JSON does not have a 'resource' object
	 */
	private JsonNode deIdentifyResource(JsonNode resource) throws DeIdentifierException {
		String resourceType = getResourceType(resource);
		if (resourceType == null) {
			throw new DeIdentifierException("The FHIR resource did not contain a 'resourceType' field. Currently only proper FHIR resources are supported");
		}
		boolean isDeidentifiable = StringUtils.equalsAny(resourceType, DEIDENTIFIABLE_FHIR_TYPES);
		if (!isDeidentifiable) {
			return null;
		}
		// The text field may contain HTLM content that causes problems in the de-id service
		((ObjectNode) resource).set(TEXT_OBJECT, JsonNodeFactory.instance.textNode(""));
		String deIdentifiedResource;
		try {
			deIdentifiedResource = deidClient.deIdentify(resource.toString(), configJson);
		} catch (DeIdentifierClientException e) {
			throw new DeIdentifierException("Error invoking the de-identification REST API", e);
		}
		JsonNode deidentifiedResourceResponse;
		try {
			deidentifiedResourceResponse = jsonDeserializer.readTree(deIdentifiedResource);
		} catch (JsonProcessingException e) {
			throw new DeIdentifierException("Error generating JSON from the de-identified resource returned by the de-id service", e);
		}
		// The de-id service returns the given resource in a JSON array called "data", we obtain it from there and return it
		ArrayNode arrayNode = (ArrayNode) deidentifiedResourceResponse.get(DATA_OBJECT);
		return arrayNode.get(0);
	}

	/**
	 * Posts the FHIR resource represented by the given {@link JsonNode} to the FHIR server.
	 * <p>
	 * The method can be used to post a FHIR transaction Bundle or individual FHIR resources. When executing
	 * a FHIR transaction Bundle the FHIR server returns the result of executing the transaction in the response. 
	 * When adding a resource FHIR does not return anything in the response body but it returns the Location header with 
	 * the URI of the new resource. In either case the result of the create operation will be added in place to the
	 * given {@link DeIdentification} object.
	 * 
	 * @param deidJson the FHIR resource to post
	 * @param deidentification the results of the FHIR create operations are saved here
	 * @throws DeIdentifierException if there is an error posting the resource to FHIR
	 */
	private void pushToFHIR(JsonNode deidJson, DeIdentification deidentification) throws DeIdentifierException {
		if (isBundle(deidJson)) {
			JsonNode fhirResponse = postBundle(deidJson);
			deidentification.setFhirResponse(fhirResponse);
		} else {
			String fhirResource = postResource(deidJson);
			deidentification.setFhirLocationHeader(fhirResource);
		}
	}

	/**
	 * Posts the given Bundle to the FHIR server
	 * 
	 * @param fhirBundle the bundle to post
	 * @return the FHIR response of executing the transaction Bundle
	 * @throws DeIdentifierException if there is a problem posting the bundle or parsing the response
	 */
	private JsonNode postBundle(JsonNode fhirBundle) throws DeIdentifierException {
		System.out.println("Initializing FHIR transacton with Bundle...");
		IParser parser = fhirClient.getFhirContext().newJsonParser();
		Bundle bundle = parser.parseResource(Bundle.class, fhirBundle.toString());
		Bundle resp;
		try {
			resp = fhirClient.transaction()
					.withBundle(bundle)
					.execute();
		} catch (BaseServerResponseException e) {
			throw new DeIdentifierException("The FHIR transaction could not be executed: " + e.getMessage(), e);	
		}
		String jsonResponseString = parser.setPrettyPrint(true).encodeResourceToString(resp);
		JsonNode jsonResponse;
		try {
			jsonResponse = jsonDeserializer.readTree(jsonResponseString);
		} catch (JsonProcessingException e) {
			throw new DeIdentifierException("The FHIR response JSON could not be parsed: " + e.getMessage(), e);
		}
		System.out.println("FHIR transacton with Bundle done!");
		return jsonResponse;
	}
	
	/**
	 * Posts the given Resource to the FHIR server
	 * 
	 * @param fhirResource the resource to post
	 * @return the FHIR response of executing the POST operation
	 * @throws DeIdentifierException if there is a problem posting the resource
	 */
	@SuppressWarnings("unchecked")
	private String postResource(JsonNode fhirResource) throws DeIdentifierException {
		System.out.println("Initializing FHIR create resource...");
		IParser parser = fhirClient.getFhirContext().newJsonParser();

		// We don't know exactly what type of Resource we are going to POST to FHiR and the FHIR requires
		// that when parsing a Resource a concrete class is used, so we load the concrete type reflexively 
	    ClassLoader classLoader = this.getClass().getClassLoader();
	    Class<? extends Resource> aClass = null;
	    String resourceType = getResourceType(fhirResource);
		try {
			aClass = (Class<? extends Resource>) classLoader.loadClass("org.hl7.fhir.r4.model." + resourceType);
	    } catch (ClassNotFoundException e) {
	    	throw new DeIdentifierException("A Resource of type '" + resourceType + "' could not be found in the current HAPI FHIR JAR: " + e.getMessage(), e);
	    }
		
	    Resource resource = parser.parseResource(aClass, fhirResource.toString());
		MethodOutcome outcome;
		try {
			outcome = fhirClient.create()
					   .resource(resource)
					   .encodedJson()
					   .execute();
		} catch (BaseServerResponseException e) {
			throw new DeIdentifierException("The FHIR transaction could not be executed: " + e.getMessage(), e);	
		}
		System.out.println("FHIR create resource done!");
		return outcome.getId().toString();
	}

	public void setConfigJson(String string) {
		configJson = string;
	}
	
}
