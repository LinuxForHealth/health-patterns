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
package com.ibm.healthpatterns.processors.deid;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

import org.apache.nifi.util.MockFlowFile;
import org.apache.nifi.util.TestRunners;
import org.junit.Before;
import org.junit.Test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.healthpatterns.processors.common.FHIRCustomProcessorTest;
import com.ibm.healthpatterns.processors.common.FHIRServiceCustomProcessor;

/**
 * This test runs the custom process against a real de-id service and FHIR server dedicated 
 * to ensure the functionality here works.
 * <p>
 * The corresponding services are running in the IBM Cloud in the Integration Squad's Kubernetes 
 * Cluster under a namespace called <code>custom-processors</code>.
 * 
 * @author Luis A. García
 */
public class DeIdentifyTest extends FHIRCustomProcessorTest {

	private String deidURL;
	private DeIdentify customProcessor;
	
	/**
	 * 
	 */
	public DeIdentifyTest() {
		// This URL is for IBM Cloud services that we setup specifically to run these tests 
		deidURL = "http://git-test.deid.wh-health-patterns.dev.watson-health.ibm.com/api/v1";
	}

	/**
	 * @throws IOException 
	 * 
	 */
	@Before
	public void init() throws IOException {
		customProcessor = new DeIdentify();
		testRunner = TestRunners.newTestRunner(customProcessor);
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunBundle() throws IOException {
		testRunner.setProperty(DeIdentify.DEID_URL, deidURL);
		testRunner.setProperty(DeIdentify.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentify.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentify.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Bundle.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertTransferCount(DeIdentify.SUCCESS, 1);
		testRunner.assertTransferCount(DeIdentify.DEIDENTIFIED, 1);
		testRunner.assertTransferCount(DeIdentify.ORIGINAL, 1);

		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(DeIdentify.SUCCESS).get(0);
		successFlowFile.assertAttributeExists(DeIdentify.DEID_TRANSACTION_ID_ATTRIBUTE);
		successFlowFile.assertAttributeNotExists(DeIdentify.LOCATION_ATTRIBUTE);
		String fhirResponse = successFlowFile.getContent();
		assertFalse(fhirResponse.isEmpty());

		MockFlowFile deidFlowFile = testRunner.getFlowFilesForRelationship(DeIdentify.DEIDENTIFIED).get(0);
		deidFlowFile.assertAttributeExists(DeIdentify.DEID_TRANSACTION_ID_ATTRIBUTE);
		assertFalse(deidFlowFile.getContent().isEmpty());

		MockFlowFile originalFlowFile = testRunner.getFlowFilesForRelationship(DeIdentify.ORIGINAL).get(0);
		originalFlowFile.assertAttributeExists(DeIdentify.DEID_TRANSACTION_ID_ATTRIBUTE);
		originalFlowFile.assertContentEquals(input);

		// Save the resource locations so we can clean up the FHIR server
		ObjectMapper jsonDeserializer = new ObjectMapper();
		JsonNode fhirResponseJson = jsonDeserializer.readTree(fhirResponse);
		List<JsonNode> locations = fhirResponseJson.findValues(DeIdentify.LOCATION_ATTRIBUTE.toLowerCase());
		for (JsonNode jsonNode : locations) {
			createdResources.add(jsonNode.asText());
		}
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunResource() throws IOException {
		testRunner.setProperty(DeIdentify.DEID_URL, deidURL);
		testRunner.setProperty(DeIdentify.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentify.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentify.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Patient.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertTransferCount(DeIdentify.SUCCESS, 1);
		testRunner.assertTransferCount(DeIdentify.DEIDENTIFIED, 1);
		testRunner.assertTransferCount(DeIdentify.ORIGINAL, 1);

		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(DeIdentify.SUCCESS).get(0);
		successFlowFile.assertAttributeExists(DeIdentify.DEID_TRANSACTION_ID_ATTRIBUTE);
		successFlowFile.assertAttributeExists(DeIdentify.LOCATION_ATTRIBUTE);
		assertTrue(successFlowFile.getContent().isEmpty());

		MockFlowFile deidFlowFile = testRunner.getFlowFilesForRelationship(DeIdentify.DEIDENTIFIED).get(0);
		deidFlowFile.assertAttributeExists(DeIdentify.DEID_TRANSACTION_ID_ATTRIBUTE);
		assertFalse(deidFlowFile.getContent().isEmpty());

		MockFlowFile originalFlowFile = testRunner.getFlowFilesForRelationship(DeIdentify.ORIGINAL).get(0);
		originalFlowFile.assertAttributeExists(DeIdentify.DEID_TRANSACTION_ID_ATTRIBUTE);
		originalFlowFile.assertContentEquals(input);

		// Save the resource locations so we can clean up the FHIR server
		createdResources.add(successFlowFile.getAttribute(DeIdentify.LOCATION_ATTRIBUTE));
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunBadInput() throws IOException {
		testRunner.setProperty(DeIdentify.DEID_URL, deidURL);
		testRunner.setProperty(DeIdentify.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentify.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentify.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		testRunner.enqueue("a bad file that isn't JSON");
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(DeIdentify.FAILURE);
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testValidate() throws IOException {
		testRunner.setProperty(DeIdentify.DEID_URL, "http://badurl");
		testRunner.setProperty(DeIdentify.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentify.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentify.FHIR_PASSWORD, fhirPassword);
		testRunner.assertNotValid();
	}

	/* (non-Javadoc)
	 * @see com.ibm.healthpatterns.processors.deid.FHIRCustomProcessorTest#getCustomProcessor()
	 */
	@Override
	public FHIRServiceCustomProcessor getCustomProcessor() {
		return customProcessor;
	}
}
