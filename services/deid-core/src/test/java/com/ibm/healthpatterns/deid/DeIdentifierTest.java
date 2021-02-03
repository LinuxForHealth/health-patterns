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

import static org.junit.Assert.assertNotNull;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.BeforeClass;
import org.junit.Test;

/**
 * @author Luis A. García
 */
public class DeIdentifierTest {

	private DeIdentifier deid;

	/**
	 * 
	 */
	public DeIdentifierTest() {
		deid = new DeIdentifier();
	}
	/**
	 * @throws java.lang.Exception
	 */
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
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
		assertNotNull(deidentification.getFhirResponse());
	}

}
