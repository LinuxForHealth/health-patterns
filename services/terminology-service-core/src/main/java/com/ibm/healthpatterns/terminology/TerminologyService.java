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
package com.ibm.healthpatterns.terminology;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.StringWriter;
import java.io.Writer;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
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
import org.hl7.fhir.instance.model.api.IBaseResource;
import org.hl7.fhir.instance.model.api.IIdType;
import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.Coding;
import org.hl7.fhir.r4.model.ConceptMap;
import org.hl7.fhir.r4.model.Parameters;
import org.hl7.fhir.r4.model.Parameters.ParametersParameterComponent;
import org.hl7.fhir.r4.model.Resource;
import org.hl7.fhir.r4.model.ValueSet;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.api.MethodOutcome;
import ca.uhn.fhir.rest.client.api.IClientInterceptor;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.rest.client.interceptor.BasicAuthInterceptor;

/**
 * A {@link TerminologyService} translates FHIR resource extension codes using the IBM FHIR Terminology Service.
 * <p>
 * A translation consists of finding <code>valueCode</code> extensions in a FHIR resource (Bundle or individual 
 * resource) that belong to a StructureDefinition whose ValueSet is registered in a ConceptMap with a mapping to 
 * a different StructureDefinition's ValueSet.
 * <p>
 * The mentioned ValueSet and ConceptMap resources need to exist in the FHIR server, and this class exposes a method
 * {@link #addStructureDefinitionToValueSetMapping(String, String)} to add the corresponding URI mappings from a
 * StructuredDefinition to a ValueSet.
 * <p>
 * By default the {@link TerminologyService} includes a sample translation, or mapping, from US Core BirthSex to
 * IBM CDM Sex Assigned At Birth.
 * <p>
 * This class requires the connection information for the FHIR server.
 * 
 * @author Luis A. García
 */
public class TerminologyService {

	/**
	 * Directory in the classpath that has the default mappings FHIR resources
	 */
	private static final String MAPPINGS_DIRECTORY = "/mappings/";

	/**
	 * File that has the default StructureDefinition to ValueSet mappings
	 */
	private static final String SD_TO_VS_MAPPINGS_FILE = "/mappings/structureDefinition.mappings";

	/**
	 * The FHIR Resources used for the default terminology mapping from US Core Birth Sex to IBM CDM Sex Assigned at Birth
	 */
	private static final String[] SAMPLE_MAPPING_RESOURCES = new String[] {"cdm-sex-assigned-at-birth-vs.json", "uscore-birthsex-vs.json", "uscore-to-cdm-cm.json"};
	
	/**
	 * The path to check the FHIR server health.
	 */
	private static final String FHIR_HEALTHCHECK_PATH = "/$healthcheck";

	/**
	 * A FHIR resource's Bundle resource type
	 */
	private static final String BUNDLE_TYPE = "Bundle";

	/**
	 * 
	 */
	private static final String CONCEPT_MAP_TYPE = "ConceptMap";

	/**
	 * 
	 */
	private static final String VALUE_SET_TYPE = "ValueSet";

	/**
	 * A FHIR resource's 'resource' field 
	 */
	private static final String RESOURCE_OBJECT = "resource";

	/**
	 * A FHIR resource's 'entry' field
	 */
	private static final String ENTRY_OBJECT = "entry";

	/**
	 * A FHIR resource's 'resourceType' field
	 */
	private static final String RESOURCE_TYPE_OBJECT = "resourceType";

	/**
	 * A FHIR resource's 'valueCode' field
	 */
	private static final String VALUE_CODE_OBJECT = "valueCode";

	/**
	 * A FHIR resource's 'url' field
	 */
	private static final String URL_OBJECT = "url";

	/**
	 * A FHIR resource's 'extension' field
	 */
	private static final String EXTENSION_OBJECT = "extension";

	/**
	 * A FHIR resource's 'id' field
	 */
	private static final String ID_OBJECT = "id";

	/**
	 * A FHIR resource's response 'concept' value field
	 */
	private static final String CONCEPT_VALUE = "concept";

	/**
	 * A FHIR resource's response 'match' value field
	 */
	private static final String MATCH_VALUE = "match";

	/**
	 * The types for which there is masking configuration ion this {@link DeIdentifier}s masking config.
	 */
	private static final String[] TRANSLATABLE_FHIR_TYPES = new String[] {"Patient"};

	private ObjectMapper jsonDeserializer;

	private IGenericClient fhirClient;
	private CloseableHttpClient rawFhirClient;

	private Map<String, String> valueSetForStructureDefinition;

	private boolean fhirResourcesInstalled;
	private List<String> installedResources;

	/**
	 * Create a {@link TerminologyService} that uses the given FHIR connection information.
	 * 
	 * @param fhirServerURL the full FHIR server base URL, e.g. http://fhir-us-south.lb.appdomain.cloud:8080/fhir-server/api/v4
	 * @param fhirServerUsername the FHIR server username
	 * @param fhirServerPassword the FHIR server password
	 */
	public TerminologyService(String fhirServerURL, String fhirServerUsername, String fhirServerPassword) {
		jsonDeserializer = new ObjectMapper();
		installedResources = new ArrayList<>();
		initializeFhirClients(fhirServerURL, fhirServerUsername, fhirServerPassword);
		loadValueSetsForStructureDefinitions();
	}

	/**
	 * Loads the mappings configuration file that contains the ValueSet that will be used in the valueCode element of a known StructureDefinition.
	 */
	private void loadValueSetsForStructureDefinitions() {
		valueSetForStructureDefinition = new HashMap<>();
		String fileName = SD_TO_VS_MAPPINGS_FILE;
		InputStream inputStream = this.getClass().getResourceAsStream(fileName);
	    try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8))) {
	    	reader.lines().forEach(line -> {
	    		line = line.trim();
	    		if (line.isEmpty() || line.startsWith("#")) {
	    			return;
	    		}
	    		String[] structureDefinitionToValueSet = line.split("<=>");
	    		if (structureDefinitionToValueSet.length != 2) {
	    			System.err.println("Incorrect mapping found in " + fileName + " needs to be {structure definition url} <=> {value set url}, but was " + line);
	    			return;
	    		}
	    		addStructureDefinitionToValueSetMapping(structureDefinitionToValueSet[0].trim(), structureDefinitionToValueSet[1].trim());
	    	});
	    } catch (IOException e) {
	    	System.err.println("Could not read StructuredDefinition to ValueSet configuration mapping file: " + fileName + ", the Terminology Service won't be functional: " + e.getMessage());
		}
	}

	/**
	 * Adds a bi-directional relationship between a StructureDefinition and its corresponding ValueSet.
	 * <p>
	 * A bi-directional relationship is needed because this class will need to know the VS for an incoming 
	 * codeValue given its StructuredDefinition url, and after translating it to its corresponding VS it 
	 * will need to get the corresponding SD and set it as the new url.  
	 * 
	 * @param sdUri the URI for the StructureDefinition
	 * @param vsUri the URI for the ValueSet
	 */
	public void addStructureDefinitionToValueSetMapping(String sdUri, String vsUri) {
		valueSetForStructureDefinition.put(sdUri, vsUri);
		valueSetForStructureDefinition.put(vsUri, sdUri);
	}

	private void installTranslationResources(String... fileNames) {
		boolean errors = false;
		for (String fileName : fileNames) {
			InputStream configInputStream = this.getClass().getResourceAsStream(MAPPINGS_DIRECTORY + fileName);
			String mappingResource;
			try {
				mappingResource = IOUtils.toString(configInputStream, Charset.defaultCharset());
			} catch (IOException e) {
				System.err.println("Could not read default FHIR mapping resource: " + fileName + ", the Terminology Service won't be functional: " + e.getMessage());
				errors = true;
				continue;
			}
			JsonNode mappingResourceJson;
			try {
				mappingResourceJson = jsonDeserializer.readTree(mappingResource);
			} catch (JsonProcessingException e) {
				System.err.println("The default FHIR resource JSON file " + fileName + " is not valid JSON , the Terminology Service may not be functional: " + e.getMessage());
				errors = true;
				continue;
			} 
			String resourceType = getResourceType(mappingResourceJson);
			String id = mappingResourceJson.get(ID_OBJECT).asText();
			Class<? extends IBaseResource> type = null;
			if (resourceType.equals(VALUE_SET_TYPE)) {
				type = ValueSet.class;
			} else if (resourceType.equals(CONCEPT_MAP_TYPE)) {
				type = ConceptMap.class;
			} else {
				System.err.println("Unknown resource type " + type + " for mapping FHIR resource JSON file " + fileName + ", the Terminology Service may not be functional.");
				errors = true;
				continue;
			}
			Bundle bundle = fhirClient
					.search()
					.forResource(type)
					.withIdAndCompartment(id, null)
					.returnBundle(Bundle.class)
					.execute();
			// We save the URI of the resources that this Terminology Service uses, that either are already there or were installed
			// in case a consumer needs access to them, such as a test case to clean up 
			installedResources.add(fhirClient.getServerBase() + "/" + type.getSimpleName() + "/" + id);
			if (bundle.getEntry().isEmpty()) {
				System.out.println("Did not find Terminology Service FHIR mapping resource '" + type.getCanonicalName() + "' with ID '" + id + "' in the FHIR server, installing...");
				MethodOutcome outcome = fhirClient.update()
						   .resource(mappingResource)
						   .encodedJson()
						   .execute();
				IIdType newId = outcome.getId();
				System.out.println("Installed Terminology Service FHIR mapping resource in the FHIR server: " + newId.getValue());
			} else {
				System.out.println("Terminology Service FHIR mapping resource '" + type.getCanonicalName() + "' with ID '" + id + "' is already intalled in the FHIR server.");
			}
		}
		fhirResourcesInstalled = !errors;
	}

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
	 * If the services are healthy the service returns true, otherwise the services return false.
	 * In either case the given {@link Writer} will be used by the method to populate more information about
	 * what exactly is went wrong.
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
				String responseString = EntityUtils.toString(entity, StandardCharsets.UTF_8);
				status.write("< " + response.getStatusLine().toString() + "\n");
				status.write(responseString + "\n");
				errors = true;
			} else {
				status.write("There is an unknown problem in the FHIR Server:\n");
				status.write("> " + getRequest.getRequestLine() + "\n");
				HttpEntity entity = response.getEntity();
				String responseString = EntityUtils.toString(entity, StandardCharsets.UTF_8);
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
	 * Translates the codes in the given FHIR resource using the FHIR Terminology Service which was configured
	 * using pre-determined translation mappings loaded by this service.
	 * <p>
	 * The given FHIR resource to translate can be a single resource or a Bundle.
	 * 
	 * @param fhirResource the fhir resource to transate
	 * @return a {@link Translation} with the original resource, and the translated resource which will be null if there was nothing to translate
	 * @throws TerminologyServiceException 
	 * @throws IOException 
	 */
	public Translation translate(InputStream fhirResource) throws TerminologyServiceException, IOException {
		if (!fhirResourcesInstalled) {
			installTranslationResources(SAMPLE_MAPPING_RESOURCES);
		}
		JsonNode jsonNode;
		try {
			jsonNode = jsonDeserializer.readTree(fhirResource);
		} catch (JsonParseException e) {
			throw new TerminologyServiceException("The given input stream did not contain valid JSON.", e);
		}
		if (!(jsonNode instanceof ObjectNode)) {
			throw new TerminologyServiceException("The FHIR resource did not contain a valid JSON object, likely it was a JSON array. Currently only proper FHIR resources are supported");
		}
		JsonNode resourceToTranslate = jsonNode.deepCopy();
		boolean translatedSomething = false;
		if (isBundle(resourceToTranslate)) {
			System.out.println("Translating bundle...");
			translatedSomething = translateBundle(resourceToTranslate);
			System.out.println("Translating bundle done!");
		} else {
			System.out.println("Translating single resource...");
			translatedSomething = translateResource(resourceToTranslate);
			System.out.println("Translating single resource done!");
		}
		return new Translation(jsonNode, translatedSomething ? resourceToTranslate : null);
		
	}
	
	/**
	 * This method translates the resources in the given Bundle.
	 * 
	 * @param json with the FHIR Bundle to translate
	 * @return true if some contents of the Bundle were translated, false otherwise
	 */
	private boolean translateBundle(JsonNode jsonNode) {
		ArrayNode resources = (ArrayNode) jsonNode.findValue(ENTRY_OBJECT);
		boolean translatedSomething = false;
		for (int i = 0; i < resources.size(); i++) {
			ObjectNode resourceEntry = (ObjectNode) resources.get(i);
			JsonNode resource = resourceEntry.get(RESOURCE_OBJECT);
			if (resource == null) {
				throw new IllegalArgumentException("It is expected that a resource entry within a Bundle be rooted at 'resource'.");
			}
			translatedSomething |= translateResource(resource);
		}
		return translatedSomething;
	}

	/**
	 * Translates the given single FHIR resource represented as a {@link JsonNode}.
	 *  
	 * @param resource the FHIR resource to translate
	 * @returns true if there was something to translate, false otherwise
	 * @throws DeIdentifierException if there is an error in the de-identification REST API or parsing the JSON
	 * @throws IllegalArgumentException if the given JSON does not have a 'resource' object
	 */
	private boolean translateResource(JsonNode resource) {
		boolean translatedSomething = false;
		String resourceType = getResourceType(resource);
		boolean isTranslatable = StringUtils.equalsAny(resourceType, TRANSLATABLE_FHIR_TYPES);
		if (!isTranslatable) {
			return translatedSomething;
		}
		ArrayNode extensions = (ArrayNode) resource.get(EXTENSION_OBJECT);
		if (extensions == null) {
			return translatedSomething;
		}
		for (int i = 0; i < extensions.size(); i++) {
			JsonNode extension = extensions.get(i);
			JsonNode urlJson = extension.get(URL_OBJECT);
			JsonNode valueCodeJson = extension.get(VALUE_CODE_OBJECT);
			if (urlJson == null || valueCodeJson == null) {
				// In order to do a translation we need both the url and the valueCode
				continue;
			}
			// The resource's extension URL is the URL for the StructureDefinition, so we resolve a ValueSet if known
			String structureDefinitionURL = urlJson.asText();
			String valueSetURL = valueSetForStructureDefinition.get(structureDefinitionURL);
			// and if known we check the FHIR Server's known ConceptMaps to see if there is a corresponding one
			// http://4603f72b-us-south.lb.appdomain.cloud/fhir-server/api/v4/ConceptMap?_format=json&source-uri=http://hl7.org/fhir/us/core/ValueSet/birthsex
			Bundle bundle = fhirClient
					.search()
					.forResource(ConceptMap.class)
					.where(ConceptMap.SOURCE_URI.hasId(valueSetURL))
					.returnBundle(Bundle.class)
					.execute();
			String conceptMapId;
			if (!bundle.getEntry().isEmpty()) {
				Resource conceptMap = bundle.getEntry().get(0).getResource();
				if (bundle.getEntry().size() > 1) {
					System.err.println("Found multiple ConceptMaps that will map " + valueSetURL + " for this StructureDefinition, will use the first one " + conceptMap.getId());	
				} else {
					System.out.println("Found ConceptMap for " + valueSetURL + ": " + conceptMap.getId() + " !!");					
				}
				conceptMapId = conceptMap.getIdElement().getIdPart();
			} else {
				System.out.println("Did not find ConceptMap for " + valueSetURL + "!!");
				continue;
			}

			// "POST ${FHIR_URL}/${conceptMapID}/$translate?code=${code}&system=${valueSet}&_format=json
			String valueCode = valueCodeJson.asText();
			String url = String.format("%s/ConceptMap/%s/$translate?code=%s&system=%s&_format=json", fhirClient.getServerBase(), conceptMapId, valueCode, valueSetURL); 
			Parameters translationResponse = fhirClient.fetchResourceFromUrl(Parameters.class, url);
			// This is what comes back from the server
			//			{
			//				"resourceType": "Parameters",
			//				"parameter": [
			//					{
			//						"name": "result",
			//						"valueBoolean": true
			//					},
			//					{
			//						"name": "match",
			//						"part": [
			//							{
			//								"name": "equivalence",
			//								"valueCode": "equivalent"
			//							},
			//							{
			//								"name": "concept",
			//								"valueCoding": {
			//									"system": "http://ibm.com/fhir/cdm/ValueSet/sex-assigned-at-birth",
			//									"code": "male",
			//									"display": "Male"
			//								}
			//							}
			//						]
			//					}
			//				]
			//			}
			Coding translatedCode = null;
			List<ParametersParameterComponent> parameters = translationResponse.getParameter();
			for (ParametersParameterComponent parameter : parameters) {
				if (parameter.getName().equals(MATCH_VALUE)) {
					List<ParametersParameterComponent> parts = parameter.getPart();
					for (ParametersParameterComponent part : parts) {
						if (part.getName().equals(CONCEPT_VALUE)) {
							try {
								translatedCode = (Coding) part.getValue();
							} catch (ClassCastException e) {
								String jsonResponse = fhirClient.getFhirContext().newJsonParser().encodeResourceToString(translationResponse);
								System.err.println("Found a ConceptMap that will map " + valueSetURL + " for this StructureDefinition, but the FHIR server returned an unknown $translate response (expected a 'valueCoding' part): " + jsonResponse);
							}
						}
					}
				}
			}
			if (translatedCode == null) {
				String jsonResponse = fhirClient.getFhirContext().newJsonParser().encodeResourceToString(translationResponse);
				System.err.println("Found a ConceptMap that will map " + valueSetURL + " for this StructureDefinition, but the FHIR server returned an unknown $translate response: " + jsonResponse);
				continue;
			}
			System.out.printf("Found ConceptMap %s which translates (valueCode, system) = (%s, %s) for StructureDefinition %s to (valueCode, system) = (%s, %s) %n", conceptMapId, valueCode, valueSetURL, structureDefinitionURL, translatedCode.getCode(),  translatedCode.getSystem());
			String translatedStructuredData = valueSetForStructureDefinition.get(translatedCode.getSystem());
			if (translatedStructuredData == null) {
				System.err.printf("Cannot find the mapping from ValueSet '%s' to its corresponding StructureData for this translation, make sure the corresponding mappings configuration file has it.%n", translatedCode.getSystem());
				continue;
			}
			((ObjectNode) extension).set(URL_OBJECT, JsonNodeFactory.instance.textNode(translatedStructuredData));
			((ObjectNode) extension).set(VALUE_CODE_OBJECT, JsonNodeFactory.instance.textNode(translatedCode.getCode()));
			translatedSomething = true;
		}
		return translatedSomething;
	}

	/**
	 * Extract the resource type from the given JSON object.
	 * 
	 * @param json the json resource
	 * @return the resource type or null if not found
	 */
	private String getResourceType(JsonNode json) {
		JsonNode resourceType = json.findValue(RESOURCE_TYPE_OBJECT);
		if (resourceType == null) {
			return null;
		}
		return resourceType.asText();
	}

	/**
	 * Determines whether the given {@link JsonNode} represents a FHIR Bundle
	 *  
	 * @param jsonNode the json to check
	 * @return true if the 'resourceType' of the given FHIR resource is Bundle, false otherwise
	 * @throws DeIdentifierException if the given JSON is not a valid FHIR resource 
	 */
	private boolean isBundle(JsonNode jsonNode) throws TerminologyServiceException {
		return getResourceType(jsonNode).equals(BUNDLE_TYPE);
	}
	
	/**
	 * @return the fhirClient used by this {@link TerminologyService}
	 */
	public IGenericClient getFhirClient() {
		return fhirClient;
	}

	/**
	 * @return the the FHIR Terminology Service resources used by this Terminology Service, which may or may not have been installed by this TS 
	 */
	public List<String> getInstalledResources() {
		return Collections.unmodifiableList(installedResources);
	}
}
