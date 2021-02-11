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

import org.apache.nifi.util.MockFlowFile;
import org.apache.nifi.util.TestRunner;
import org.apache.nifi.util.TestRunners;
import org.junit.Before;
import org.junit.Test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.healthpatterns.processors.common.FHIRCustomProcessorTest;
import com.ibm.healthpatterns.processors.common.FHIRServiceCustomProcessor;

/**
 * This test runs the custom process against a real FHIR server dedicated to ensure the functionality here works.
 * <p>
 * The corresponding services are running in the IBM Cloud in the Integration Squad's Kubernetes 
 * Cluster under a namespace called <code>custom-processors</code>.
 * 
 * @author Luis A. García
 */
public class FHIRTranslationTest extends FHIRCustomProcessorTest {

	private TestRunner testRunner;

	private FHIRTranslation customProcessor;

	/**
	 * @throws IOException 
	 * 
	 */
	@Before
	public void init() throws IOException {
		customProcessor = new FHIRTranslation();
		testRunner = TestRunners.newTestRunner(customProcessor);
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunBundle() throws IOException {
		testRunner.setProperty(FHIRTranslation.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRTranslation.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRTranslation.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Bundle.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRTranslation.SUCCESS);

		// We check that the contents of the flow file are not empty 
		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(FHIRTranslation.SUCCESS).get(0);
		String flowFileContent = successFlowFile.getContent();
		assertFalse(flowFileContent.isEmpty());
		successFlowFile.assertAttributeEquals(FHIRTranslation.TRANSLATED_ATTRIBUTE, "true");
		
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
		testRunner.setProperty(FHIRTranslation.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRTranslation.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRTranslation.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Patient.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRTranslation.SUCCESS);

		// We check that the contents of the flow file are not empty 
		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(FHIRTranslation.SUCCESS).get(0);
		String flowFileContent = successFlowFile.getContent();
		assertFalse(flowFileContent.isEmpty());
		successFlowFile.assertAttributeEquals(FHIRTranslation.TRANSLATED_ATTRIBUTE, "true");

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
		testRunner.setProperty(FHIRTranslation.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRTranslation.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRTranslation.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Nothing_To_Translate_Patient.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRTranslation.SUCCESS);

		// The flow file must be identical to the input flow file and there should be no provenance events
		assertTrue(testRunner.getProvenanceEvents().isEmpty());
		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(FHIRTranslation.SUCCESS).get(0);
		successFlowFile.assertContentEquals(input);
		successFlowFile.assertAttributeEquals(FHIRTranslation.TRANSLATED_ATTRIBUTE, "false");

		// Save the resource locations so we can clean up the FHIR server
		createdResources.addAll(customProcessor.getTerminologyService().getInstalledResources());
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunBadInput() throws IOException {
		testRunner.setProperty(FHIRTranslation.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRTranslation.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRTranslation.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		testRunner.enqueue("a bad file that isn't JSON");
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(FHIRTranslation.FAILURE);
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testValidate() throws IOException {
		testRunner.setProperty(FHIRTranslation.FHIR_URL, fhirURL);
		testRunner.setProperty(FHIRTranslation.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(FHIRTranslation.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();
	}

	/* (non-Javadoc)
	 * @see com.ibm.healthpatterns.processors.common.FHIRCustomProcessorTest#getCustomProcessor()
	 */
	@Override
	public FHIRServiceCustomProcessor getCustomProcessor() {
		return customProcessor;
	}

}
