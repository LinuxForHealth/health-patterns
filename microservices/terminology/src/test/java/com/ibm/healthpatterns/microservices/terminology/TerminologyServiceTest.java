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
package com.ibm.healthpatterns.microservices.terminology;

import com.fasterxml.jackson.databind.JsonNode;
import com.ibm.healthpatterns.microservices.common.FHIRService;
import com.ibm.healthpatterns.microservices.common.FHIRServiceTest;

import org.apache.commons.io.IOUtils;
import org.junit.Test;

import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import static org.junit.Assert.*;

/**
 * This test runs the {@link TerminologyService} against a real FHIR server dedicated 
 * to ensure the functionality here works.
 * <p>
 * The corresponding services are running in the IBM Cloud in the Integration Squad's Kubernetes 
 * Cluster under a namespace called <code>custom-processors</code>.
 *  
 * @author Luis A. García
 */
public class TerminologyServiceTest extends FHIRServiceTest {

	private TerminologyService terminology;
	
	/**
	 * 
	 */
	public TerminologyServiceTest() {
		terminology = new TerminologyService(fhirURL, fhirUsername, fhirPassword);
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.microservices.terminology.TerminologyService#healthCheck(java.io.StringWriter)}.
	 */
	@Test
	public void testHealthCheck() {
		StringWriter status = new StringWriter();
		boolean healthCheck = terminology.healthCheck(status);
		System.out.println(status);
		assertTrue(status.toString(), healthCheck);
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.microservices.terminology.TerminologyService#healthCheck(java.io.StringWriter)}.
	 */
	@Test
	public void testHealthCheckBadFHIR() {
		terminology = new TerminologyService("http://wrong-us-south.lb.appdomain.cloud:8080/api/v1", fhirUsername, fhirPassword);
		StringWriter status = new StringWriter();
		boolean healthCheck = terminology.healthCheck(status);
		System.out.println(status);
		assertFalse(healthCheck);
	}
	
	/**
	 * Test method for {@link com.ibm.healthpatterns.microservices.terminology.TerminologyService#healthCheck(java.io.StringWriter)}.
	 */
	@Test
	public void testHealthCheckBadFHIRCredentials() {
		terminology = new TerminologyService(fhirURL, "wronguser", fhirPassword);
		StringWriter status = new StringWriter();
		boolean healthCheck = terminology.healthCheck(status);
		System.out.println(status);
		assertFalse(healthCheck);
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.microservices.terminology.TerminologyService#translate(InputStream)}
	 * 
	 * @throws IOException 
	 * @throws TerminologyServiceException 
	 */
	@Test
	public void testTranslateResource() throws IOException, TerminologyServiceException {
		// This first pass tests (in addition to the actual translation) 
		// the path were the FHIR Terminology Service resources are installed from scratch on the FHIR server
		Path jsonFile = Paths.get("src/test/resources/Antonia30_Acosta403_Patient.json");
		InputStream inputStream = Files.newInputStream(jsonFile);
		Translation translation = terminology.translate(inputStream);
		
		JsonNode originalResource = translation.getOriginalResource();
		JsonNode translatedResource = translation.getTranslatedResource();
		assertNotNull(originalResource);
		assertNotNull(translatedResource);
		
		// Check the original code
		JsonNode valueCodeExtension = originalResource.findParent("valueCode");
		assertEquals("F", valueCodeExtension.get("valueCode").asText());
		assertEquals("http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex", valueCodeExtension.get("url").asText());
		
		// Check the translated code
		JsonNode translatedValueCodeExtension = translatedResource.findParent("valueCode");
		assertEquals("female", translatedValueCodeExtension.get("valueCode").asText());
		assertEquals("http://ibm.com/fhir/cdm/StructureDefinition/sex-assigned-at-birth", translatedValueCodeExtension.get("url").asText());

		// Then this second pass tests (in addition to the actual translation) 
		// the path were the FHIR Terminology Service resources are already installed on the FHIR server
		jsonFile = Paths.get("src/test/resources/Antonio30_Acosta403_Patient.json");
		inputStream = Files.newInputStream(jsonFile);
		translation = terminology.translate(inputStream);
		
		originalResource = translation.getOriginalResource();
		translatedResource = translation.getTranslatedResource();
		assertNotNull(originalResource);
		assertNotNull(translatedResource);
		
		// Check the original code
		valueCodeExtension = originalResource.findParent("valueCode");
		assertEquals("M", valueCodeExtension.get("valueCode").asText());
		assertEquals("http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex", valueCodeExtension.get("url").asText());
		
		// Check the translated code
		translatedValueCodeExtension = translatedResource.findParent("valueCode");
		assertEquals("male", translatedValueCodeExtension.get("valueCode").asText());
		assertEquals("http://ibm.com/fhir/cdm/StructureDefinition/sex-assigned-at-birth", translatedValueCodeExtension.get("url").asText());
		
		// Save created resources to clean up
		createdResources.addAll(terminology.getInstalledResources());
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.microservices.terminology.TerminologyService#translate(InputStream)}
	 * 
	 * @throws IOException 
	 * @throws TerminologyServiceException 
	 */
	@Test
	public void testTranslateResourceWithNothingToTranslate() throws IOException, TerminologyServiceException{
		Path jsonFile = Paths.get("src/test/resources/Nothing_To_Translate_Patient.json");
		InputStream inputStream = Files.newInputStream(jsonFile);
		Translation translation = terminology.translate(inputStream);
		
		JsonNode originalResource = translation.getOriginalResource();
		JsonNode translatedResource = translation.getTranslatedResource();
		assertNotNull(originalResource);
		assertNull(translatedResource);
		
		createdResources.addAll(terminology.getInstalledResources());
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.microservices.terminology.TerminologyService#translate(InputStream)}
	 * 
	 * @throws IOException 
	 * @throws TerminologyServiceException 
	 */
	@Test
	public void testTranslateBundle() throws IOException, TerminologyServiceException{
		// This first pass tests (in addition to the actual translation) 
		// the path were the FHIR Terminology Service resources are installed from scratch on the FHIR server
		Path jsonFile = Paths.get("src/test/resources/Antonia30_Acosta403_Bundle.json");
		InputStream inputStream = Files.newInputStream(jsonFile);
		Translation translation = terminology.translate(inputStream);
		
		JsonNode originalResource = translation.getOriginalResource();
		JsonNode translatedResource = translation.getTranslatedResource();
		assertNotNull(originalResource);
		assertNotNull(translatedResource);
		
		// Check the original code
		JsonNode valueCodeExtension = originalResource.findParent("valueCode");
		assertEquals("F", valueCodeExtension.get("valueCode").asText());
		assertEquals("http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex", valueCodeExtension.get("url").asText());
		
		// Check the translated code
		JsonNode translatedValueCodeExtension = translatedResource.findParent("valueCode");
		assertEquals("female", translatedValueCodeExtension.get("valueCode").asText());
		assertEquals("http://ibm.com/fhir/cdm/StructureDefinition/sex-assigned-at-birth", translatedValueCodeExtension.get("url").asText());

		// Save created resources to clean up
		createdResources.addAll(terminology.getInstalledResources());
	}

	/**
	 * Test method for {@link com.ibm.healthpatterns.microservices.terminology.TerminologyService#translate(java.io.InputStream)}.
	 * 
	 * @throws IOException 
	 * @throws TerminologyServiceException 
	 */
	@Test(expected = TerminologyServiceException.class)
	public void testTranslateBadJSON() throws IOException, TerminologyServiceException {
		InputStream inputStream = IOUtils.toInputStream("some bad JSON", Charset.forName("UTF-8"));
		terminology.translate(inputStream);
	}

	/* (non-Javadoc)
	 * @see com.ibm.healthpatterns.core.FHIRServiceTest#getFHIRService()
	 */
	@Override
	protected FHIRService getFHIRService() {
		return terminology;
	}
	
}