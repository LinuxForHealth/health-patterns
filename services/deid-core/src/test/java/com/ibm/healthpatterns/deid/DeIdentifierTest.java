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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.IOUtils;
import org.junit.After;
import org.junit.Test;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * This test runs the {@link DeIdentifier} against a real de-id service and FHIR server dedicated 
 * to ensure the functionality here works.
 * <p>
 * The corresponding services are running in the IBM Cloud in the Integration Squad's Kubernetes 
 * Cluster under a namespace called <code>custom-processors</code>.
 *  
 * @author Luis A. García
 */
public class DeIdentifierTest {

	private DeIdentifier deid;
	private List<String> createdResources;
	
	private String deidURL;
	private String fhirURL;
	private String fhirUsername;
	private String fhirPassword;

	/**
	 * 
	 */
	public DeIdentifierTest() {
		deidURL = "http://3a5d0fa4-us-south.lb.appdomain.cloud:8080/api/v1";
		fhirURL = "http://4603f72b-us-south.lb.appdomain.cloud/fhir-server/api/v4";
		fhirUsername = "fhiruser";
		fhirPassword = "integrati0n";
		deid = new DeIdentifier(deidURL, fhirURL, fhirUsername, fhirPassword);
		createdResources = new ArrayList<String>();
	}

	/**
	 * Clean up the FHIR resources created by this test 
	 */
	@After
	public void cleanUpFHIR() {
		for (String uri : createdResources) {
			String[] uriElements = uri.split("/");
			String id = uriElements[uriElements.length - 3];
			String type = uriElements[uriElements.length - 4];
			System.out.println("Deleting " + type + " resource " + id);
			deid.getFhirClient()
					.delete()
					.resourceById(type, id)
					.execute();
		}
		System.out.println("------------------");
		System.out.println();
	}
	
	/**
	 * Test method for {@link com.ibm.healthpatterns.deid.DeIdentifier#healthCheck(java.io.StringWriter)}.
	 */
	@Test
	public void testHealthCheck() {
		StringWriter status = new StringWriter();
		boolean healthCheck = deid.healthCheck(status);
		System.out.println(status);
		assertTrue(status.toString(), healthCheck);
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.deid.DeIdentifier#healthCheck(java.io.StringWriter)}.
	 */
	@Test
	public void testHealthCheckBadDeID() {
		deid = new DeIdentifier("http://wrong-us-south.lb.appdomain.cloud:8080/api/v1", fhirURL, fhirUsername, fhirPassword);
		StringWriter status = new StringWriter();
		boolean healthCheck = deid.healthCheck(status);
		System.out.println(status);
		assertFalse(healthCheck);
	}
	
	/**
	 * Test method for {@link com.ibm.healthpatterns.deid.DeIdentifier#healthCheck(java.io.StringWriter)}.
	 */
	@Test
	public void testHealthCheckBadFHIR() {
		deid = new DeIdentifier(deidURL, "http://wrong-us-south.lb.appdomain.cloud/fhir-server/api/v4", fhirUsername, fhirPassword);
		StringWriter status = new StringWriter();
		boolean healthCheck = deid.healthCheck(status);
		System.out.println(status);
		assertFalse(healthCheck);
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.deid.DeIdentifier#healthCheck(java.io.StringWriter)}.
	 */
	@Test
	public void testHealthCheckBadFHIRCredentials() {
		deid = new DeIdentifier(deidURL, fhirURL, "wronguser", fhirPassword);
		StringWriter status = new StringWriter();
		boolean healthCheck = deid.healthCheck(status);
		System.out.println(status);
		assertFalse(healthCheck);
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.deid.DeIdentifier#deIdentify(java.io.InputStream)}.
	 * 
	 * @throws IOException 
	 * @throws DeIdentifierException 
	 */
	@Test
	public void testDeIdentifyResource() throws IOException, DeIdentifierException {
		Path jsonFile = Paths.get("src/test/resources/Antonia30_Acosta403_Patient.json");
		InputStream inputStream = Files.newInputStream(jsonFile);
		DeIdentification deidentification = deid.deIdentify(inputStream);
		assertNotNull(deidentification.getFhirLocationHeader());
		
		// We test that the original patient is present and check its known birthdate
		JsonNode originalPatient = deidentification.getOriginalResource();
		assertNotNull(originalPatient);
		assertEquals("1970-09-06", originalPatient.findPath("birthDate").asText());
		
		// We test that the de-identified resource indeed has been de-identified and its birthdate offset
		JsonNode deidPatient = deidentification.getDeIdentifiedResource();
		assertNotEquals("1970-09-06", deidPatient.findPath("birthDate").asText());
		
		// We test that there is a Location header from the FHIR server 
		String location = deidentification.getFhirLocationHeader();
		assertNotNull(location);
		
		// We ensure that the FHIR response is empty, FHIR doesn't return nothing when adding a single patient resource
		assertNull(deidentification.getFhirResponse());
		
		// We save the location of the created resources to clean up
		createdResources.add(location);
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.deid.DeIdentifier#deIdentify(java.io.InputStream)}.
	 * 
	 * @throws IOException 
	 * @throws DeIdentifierException 
	 */
	@Test
	public void testDeIdentifyBundle() throws IOException, DeIdentifierException {
		Path jsonFile = Paths.get("src/test/resources/Antonia30_Acosta403_Bundle.json");
		InputStream inputStream = Files.newInputStream(jsonFile);
		DeIdentification deidentification = deid.deIdentify(inputStream);
		assertNotNull(deidentification);
		
		// We test that the Bundle contains the known birthdate for the original patient
		JsonNode originalBundle = deidentification.getOriginalResource();
		assertNotNull(originalBundle);
		assertEquals("1970-09-06", originalBundle.findPath("birthDate").asText());
		
		// We test that the de-identified Bundle's patient birthdate has been de-identified
		JsonNode deidBundle = deidentification.getDeIdentifiedResource();
		assertNotEquals("1970-09-06", deidBundle.findPath("birthDate").asText());
		
		// We test that there is no Location header from the FHIR server, since when running Bundles it doesn't return one 
		String location = deidentification.getFhirLocationHeader();
		assertNull(location);
		
		// We ensure that the FHIR response is not empty, FHIR doesn't returns the Bundle transaction results here
		JsonNode fhirResponse = deidentification.getFhirResponse();
		assertNotNull(fhirResponse);

		// We save the location of the created resources to clean up
		List<JsonNode> locations = fhirResponse.findValues("location");
		for (JsonNode jsonNode : locations) {
			createdResources.add(jsonNode.asText());
		}
	}
	
	/**
	 * Test method for {@link com.ibm.healthpatterns.deid.DeIdentifier#deIdentify(java.io.InputStream)}.
	 * 
	 * @throws IOException 
	 * @throws DeIdentifierException 
	 */
	@Test(expected = DeIdentifierException.class)
	public void testDeIdentifyBadJSON() throws IOException, DeIdentifierException {
		InputStream inputStream = IOUtils.toInputStream("some bad JSON", Charset.forName("UTF-8"));
		deid.deIdentify(inputStream);
	}
	
}