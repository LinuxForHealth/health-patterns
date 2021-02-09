/*
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
package com.ibm.healthpatterns.processors.terminology;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import org.apache.nifi.util.MockFlowFile;
import org.apache.nifi.util.TestRunner;
import org.apache.nifi.util.TestRunners;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * This test runs the custom process against a real FHIR server dedicated to ensure the functionality here works.
 * <p>
 * The corresponding services are running in the IBM Cloud in the Integration Squad's Kubernetes 
 * Cluster under a namespace called <code>custom-processors</code>.
 * 
 * @author Luis A. García
 */
public class FHIRConceptMapTranslateTest {

	private TestRunner testRunner;

	private String fhirURL;
	private String fhirUsername;
	private String fhirPassword;

	private List<String> createdResources;

	private FHIRConceptMapTranslate customProcessor;

	/**
	 * 
	 */
	public FHIRConceptMapTranslateTest() {
		// These URLs are for two IBM Cloud services that we setup specifically to run these tests 
		fhirURL = "http://4603f72b-us-south.lb.appdomain.cloud/fhir-server/api/v4";
		fhirUsername = "fhiruser";
		fhirPassword = "integrati0n";
		createdResources = new ArrayList<String>();
	}

	/**
	 * @throws IOException 
	 * 
	 */
	@Before
	public void init() throws IOException {
		customProcessor = new FHIRConceptMapTranslate();
		testRunner = TestRunners.newTestRunner(customProcessor);
	}

	/**
	 * @throws IOException 
	 * 
	 */
	@After
	public void cleanUpFHIR() throws IOException {
		for (String uri : createdResources) {
			String[] uriElements = uri.split("/");
			String id = uriElements[uriElements.length - 1];
			String type = uriElements[uriElements.length - 2];
			System.out.println("Deleting " + type + " resource " + id);
			customProcessor.getTerminologyService()
				.getFhirClient()
				.delete()
				.resourceById(type, id)
				.execute();
		}
		System.out.println("------------------");
		System.out.println();    	
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunBundle() throws IOException {
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Bundle.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRConceptMapTranslate.SUCCESS);

		// We check that the contents of the flow file are not empty 
		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(FHIRConceptMapTranslate.SUCCESS).get(0);
		String flowFileContent = successFlowFile.getContent();
		assertFalse(flowFileContent.isEmpty());
		successFlowFile.assertAttributeEquals(FHIRConceptMapTranslate.TRANSLATED_ATTRIBUTE, "true");
		
		// We check that there are some provenance events because the contents of the flow file were modified
		assertFalse(testRunner.getProvenanceEvents().isEmpty());

		// The original file had code "F" we check its translated to "female"
		ObjectMapper jsonDeserializer = new ObjectMapper();
		JsonNode flowFileJson = jsonDeserializer.readTree(flowFileContent);
		JsonNode valueCodeExtension = flowFileJson.findParent("valueCode");
		assertEquals("female", valueCodeExtension.get("valueCode").asText());
		assertEquals("http://ibm.com/fhir/cdm/StructureDefinition/sex-assigned-at-birth", valueCodeExtension.get("url").asText());

		// Save the resource locations so we can clean up the FHIR server
		createdResources.addAll(customProcessor.getTerminologyService().getInstalledResources());
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunResource() throws IOException {
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Patient.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRConceptMapTranslate.SUCCESS);

		// We check that the contents of the flow file are not empty 
		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(FHIRConceptMapTranslate.SUCCESS).get(0);
		String flowFileContent = successFlowFile.getContent();
		assertFalse(flowFileContent.isEmpty());
		successFlowFile.assertAttributeEquals(FHIRConceptMapTranslate.TRANSLATED_ATTRIBUTE, "true");

		// We check that there are some provenance events because the contents of the flow file were modified
		assertFalse(testRunner.getProvenanceEvents().isEmpty());

		// The original file had code "F" we check its translated to "female"
		ObjectMapper jsonDeserializer = new ObjectMapper();
		JsonNode flowFileJson = jsonDeserializer.readTree(flowFileContent);
		JsonNode valueCodeExtension = flowFileJson.findParent("valueCode");
		assertEquals("female", valueCodeExtension.get("valueCode").asText());
		assertEquals("http://ibm.com/fhir/cdm/StructureDefinition/sex-assigned-at-birth", valueCodeExtension.get("url").asText());

		// Save the resource locations so we can clean up the FHIR server
		createdResources.addAll(customProcessor.getTerminologyService().getInstalledResources());
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunNothingToTranslate() throws IOException {
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Nothing_To_Translate_Patient.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRConceptMapTranslate.SUCCESS);

		// The flow file must be identical to the input flow file and there should be no provenance events
		assertTrue(testRunner.getProvenanceEvents().isEmpty());
		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(FHIRConceptMapTranslate.SUCCESS).get(0);
		successFlowFile.assertContentEquals(input);
		successFlowFile.assertAttributeEquals(FHIRConceptMapTranslate.TRANSLATED_ATTRIBUTE, "false");

		// Save the resource locations so we can clean up the FHIR server
		createdResources.addAll(customProcessor.getTerminologyService().getInstalledResources());
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunBadInput() throws IOException {
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		testRunner.enqueue("a bad file that isn't JSON");
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRConceptMapTranslate.FAILURE);
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testValidate() throws IOException {
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRConceptMapTranslate.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();
	}

}
