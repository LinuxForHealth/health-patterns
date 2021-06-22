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

import java.io.*;
import java.util.*;

import org.apache.commons.lang3.StringUtils;
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
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.ibm.healthpatterns.core.FHIRService;


import ca.uhn.fhir.rest.api.MethodOutcome;

/**
 * A {@link TerminologyService} translates FHIR resource extension codes using the IBM FHIR Terminology Service.
 * <p>
 * A translation consists of finding <code>valueCode</code> extensions in a FHIR resource (Bundle or individual 
 * resource) that belong to a StructureDefinition whose ValueSet is registered in a ConceptMap with a mapping to 
 * a different StructureDefinition's ValueSet.
 * <p>
 * The mentioned ValueSet and ConceptMap resources need to exist in the FHIR server, and this class exposes a method
 * {@link #(String, String)} to add the corresponding URI mappings from a
 * StructuredDefinition to a ValueSet.
 * <p>
 * By default the {@link TerminologyService} includes a sample translation, or mapping, from US Core BirthSex to
 * IBM CDM Sex Assigned At Birth.
 * <p>
 * This class requires the connection information for the FHIR server.
 * 
 * @author Luis A. García
 */
public class TerminologyService extends FHIRService {

	/**
	 * The ConceptMap FHIR resource type
	 */
	private static final String CONCEPT_MAP_TYPE = "ConceptMap";

	/**
	 * The ValueSet FHIR resource type
	 */
	private static final String VALUE_SET_TYPE = "ValueSet";

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


	private static final String[] TRANSLATABLE_FHIR_TYPES = new String[] {"Patient"};

	private boolean fhirResourcesInstalled;
	private List<String> installedResources;
	private MappingStore mappingStore;

	/**
	 * Create a {@link TerminologyService} that uses the given FHIR connection information.
	 * 
	 * @param fhirServerURL the full FHIR server base URL, e.g. http://fhir-us-south.lb.appdomain.cloud:8080/fhir-server/api/v4
	 * @param fhirServerUsername the FHIR server username
	 * @param fhirServerPassword the FHIR server password
	 */
	public TerminologyService(String fhirServerURL, String fhirServerUsername, String fhirServerPassword, MappingStore mappings) {
		super(fhirServerURL, fhirServerUsername, fhirServerPassword);
		installedResources = new ArrayList<>();
		this.mappingStore = mappings;
	}

	/**
	 * Install the default translation FHIR resources on the FHIR server.
	 *
	 */
	public boolean installTranslationResource(String resourceName, String mappingResource) {
		JsonNode mappingResourceJson;
		try {
			mappingResourceJson = jsonDeserializer.readTree(mappingResource);
		} catch (JsonProcessingException e) {
			System.err.println("The FHIR resource JSON file " + resourceName + " is not valid JSON , the Terminology Service may not be functional: " + e.getMessage());
			return false;
		}
		String resourceType = getResourceType(mappingResourceJson);
		String id = mappingResourceJson.get(ID_OBJECT).asText();
		Class<? extends IBaseResource> type = null;
		if (resourceType.equals(VALUE_SET_TYPE)) {
			type = ValueSet.class;
		} else if (resourceType.equals(CONCEPT_MAP_TYPE)) {
			type = ConceptMap.class;
		} else {
			System.err.println("Unknown resource type " + type + " for mapping FHIR resource JSON file " + resourceName + ", the Terminology Service may not be functional.");
			return false;
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
		return true;
	}

	private void installSavedTranslationResources() {
		Map<String, String> mappingResources = mappingStore.getSavedMappings();
		Set<String> resourceNames = mappingResources.keySet();
		boolean errors = false;
		for (String resourceName : resourceNames) {
			String mappingResource = mappingResources.get(resourceName);
			if (!installTranslationResource(resourceName, mappingResource)) errors = true;
		}
		fhirResourcesInstalled = !errors;
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
			installSavedTranslationResources();
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
	 * @param jsonNode with the FHIR Bundle to translate
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
			String valueSetURL = mappingStore.getStructureDefinitions().get(structureDefinitionURL);
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
			String translatedStructuredData = mappingStore.getStructureDefinitions().inverse().get(translatedCode.getSystem());
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
	 * @return the the FHIR Terminology Service resources used by this Terminology Service, which may or may not have been installed by this TS 
	 */
	public List<String> getInstalledResources() {
		return Collections.unmodifiableList(installedResources);
	}
}
