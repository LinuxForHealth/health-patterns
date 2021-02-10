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
package com.ibm.healthpatterns.processors.common;

import java.util.ArrayList;
import java.util.List;

import org.apache.nifi.util.TestRunner;
import org.junit.After;

/**
 * @author Luis A. García
 */
public abstract class FHIRCustomProcessorTest {

	protected TestRunner testRunner;
	
	protected String fhirURL;
	protected String fhirUsername;
	protected String fhirPassword;
	
	protected List<String> createdResources;

	/**
	 * 
	 */
	public FHIRCustomProcessorTest() {
		// This URL is for IBM Cloud services that we setup specifically to run these tests
		fhirURL = "http://4603f72b-us-south.lb.appdomain.cloud/fhir-server/api/v4";
		fhirUsername = "fhiruser";
		fhirPassword = "integrati0n";
		createdResources = new ArrayList<>();
	}
	
	/**
	 * Clean up the FHIR resources created by this test.
	 * <p>
	 * The URIs saved by the test cases can be of the form:
	 * - http://server/fhir-server/api/v4/{ResourceType}/{id}/_history/{version}
	 * - http://server/fhir-server/api/v4/{ResourceType}/{id}
	 */
	@After
	public void cleanUpFHIR() {
		for (String uri : createdResources) {
			String[] uriElements = uri.split("/");
			String id;
			String type;
			if (uri.contains("_history")) {
				id = uriElements[uriElements.length - 3];
				type = uriElements[uriElements.length - 4];
			} else {
				id = uriElements[uriElements.length - 1];
				type = uriElements[uriElements.length - 2];
			}
			System.out.println("Deleting " + type + " resource " + id);
			getCustomProcessor().getFHIRService()
				.getFhirClient()
				.delete()
				.resourceById(type, id)
				.execute();
		}
		System.out.println("------------------");
		System.out.println();    	
	}

	/**
	 * @return the {@link FHIRServiceCustomProcessor} used by this test
	 */
	public abstract FHIRServiceCustomProcessor getCustomProcessor();
}