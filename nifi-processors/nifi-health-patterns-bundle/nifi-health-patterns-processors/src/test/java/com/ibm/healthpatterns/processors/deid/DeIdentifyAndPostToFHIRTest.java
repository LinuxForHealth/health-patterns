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
 * This test runs the custom process against a real de-id service and FHIR server dedicated 
 * to ensure the functionality here works.
 * <p>
 * The corresponding services are running in the IBM Cloud in the Integration Squad's Kubernetes 
 * Cluster under a namespace called <code>custom-processors</code>.
 * 
 * @author Luis A. García
 */
public class DeIdentifyAndPostToFHIRTest {

	private TestRunner testRunner;

	private String deidURL;
	private String fhirURL;
	private String fhirUsername;
	private String fhirPassword;

	private List<String> createdResources;

	private DeIdentifyAndPostToFHIR customProcessor;

	/**
	 * 
	 */
	public DeIdentifyAndPostToFHIRTest() {
		// These URLs are for two IBM Cloud services that we setup specifically to run these tests 
		deidURL = "http://3a5d0fa4-us-south.lb.appdomain.cloud:8080/api/v1";
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
		customProcessor = new DeIdentifyAndPostToFHIR();
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
			String id = uriElements[uriElements.length - 3];
			String type = uriElements[uriElements.length - 4];
			System.out.println("Deleting " + type + " resource " + id);
			customProcessor.getDeidentifier()
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
		testRunner.setProperty(DeIdentifyAndPostToFHIR.DEID_URL, deidURL);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Bundle.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertTransferCount(DeIdentifyAndPostToFHIR.SUCCESS, 1);
		testRunner.assertTransferCount(DeIdentifyAndPostToFHIR.DEIDENTIFIED, 1);
		testRunner.assertTransferCount(DeIdentifyAndPostToFHIR.ORIGINAL, 1);

		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(DeIdentifyAndPostToFHIR.SUCCESS).get(0);
		successFlowFile.assertAttributeExists(DeIdentifyAndPostToFHIR.DEID_TRANSACTION_ID_ATTRIBUTE);
		successFlowFile.assertAttributeNotExists(DeIdentifyAndPostToFHIR.LOCATION);
		String fhirResponse = successFlowFile.getContent();
		assertFalse(fhirResponse.isEmpty());

		MockFlowFile deidFlowFile = testRunner.getFlowFilesForRelationship(DeIdentifyAndPostToFHIR.DEIDENTIFIED).get(0);
		deidFlowFile.assertAttributeExists(DeIdentifyAndPostToFHIR.DEID_TRANSACTION_ID_ATTRIBUTE);
		assertFalse(deidFlowFile.getContent().isEmpty());

		MockFlowFile originalFlowFile = testRunner.getFlowFilesForRelationship(DeIdentifyAndPostToFHIR.ORIGINAL).get(0);
		originalFlowFile.assertAttributeExists(DeIdentifyAndPostToFHIR.DEID_TRANSACTION_ID_ATTRIBUTE);
		originalFlowFile.assertContentEquals(input);

		// Save the resource locations so we can clean up the FHIR server
		ObjectMapper jsonDeserializer = new ObjectMapper();
		JsonNode fhirResponseJson = jsonDeserializer.readTree(fhirResponse);
		List<JsonNode> locations = fhirResponseJson.findValues(DeIdentifyAndPostToFHIR.LOCATION.toLowerCase());
		for (JsonNode jsonNode : locations) {
			createdResources.add(jsonNode.asText());
		}
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunResource() throws IOException {
		testRunner.setProperty(DeIdentifyAndPostToFHIR.DEID_URL, deidURL);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		Path input = Paths.get("src/test/resources/Antonia30_Acosta403_Patient.json");
		testRunner.enqueue(input);
		testRunner.run();
		testRunner.assertTransferCount(DeIdentifyAndPostToFHIR.SUCCESS, 1);
		testRunner.assertTransferCount(DeIdentifyAndPostToFHIR.DEIDENTIFIED, 1);
		testRunner.assertTransferCount(DeIdentifyAndPostToFHIR.ORIGINAL, 1);

		MockFlowFile successFlowFile = testRunner.getFlowFilesForRelationship(DeIdentifyAndPostToFHIR.SUCCESS).get(0);
		successFlowFile.assertAttributeExists(DeIdentifyAndPostToFHIR.DEID_TRANSACTION_ID_ATTRIBUTE);
		successFlowFile.assertAttributeExists(DeIdentifyAndPostToFHIR.LOCATION);
		assertTrue(successFlowFile.getContent().isEmpty());

		MockFlowFile deidFlowFile = testRunner.getFlowFilesForRelationship(DeIdentifyAndPostToFHIR.DEIDENTIFIED).get(0);
		deidFlowFile.assertAttributeExists(DeIdentifyAndPostToFHIR.DEID_TRANSACTION_ID_ATTRIBUTE);
		assertFalse(deidFlowFile.getContent().isEmpty());

		MockFlowFile originalFlowFile = testRunner.getFlowFilesForRelationship(DeIdentifyAndPostToFHIR.ORIGINAL).get(0);
		originalFlowFile.assertAttributeExists(DeIdentifyAndPostToFHIR.DEID_TRANSACTION_ID_ATTRIBUTE);
		originalFlowFile.assertContentEquals(input);

		// Save the resource locations so we can clean up the FHIR server
		createdResources.add(successFlowFile.getAttribute(DeIdentifyAndPostToFHIR.LOCATION));
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testRunBadInput() throws IOException {
		testRunner.setProperty(DeIdentifyAndPostToFHIR.DEID_URL, deidURL);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_PASSWORD, fhirPassword);
		testRunner.assertValid();

		testRunner.enqueue("a bad file that isn't JSON");
		testRunner.run();
		testRunner.assertAllFlowFilesTransferred(DeIdentifyAndPostToFHIR.FAILURE);
	}

	/**
	 * @throws IOException 
	 */
	@Test
	public void testValidate() throws IOException {
		testRunner.setProperty(DeIdentifyAndPostToFHIR.DEID_URL, "http://badurl");
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_URL, fhirURL);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_USERNAME, fhirUsername);
		testRunner.setProperty(DeIdentifyAndPostToFHIR.FHIR_PASSWORD, fhirPassword);
		testRunner.assertNotValid();
	}

}
