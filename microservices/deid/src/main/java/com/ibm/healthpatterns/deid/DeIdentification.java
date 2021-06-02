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

import com.fasterxml.jackson.databind.JsonNode;

/**
 * The result of a de-identify operation.
 * <p>
 * A de-identify operation consists of putting a FHIR resource (bundle or an individual resource) 
 * through a de-identification service and subsequently saving that de-identified resource in a FHIR server. 
 * This object contains the elements that may be important to a requester of a de-identify operation such as
 * the initial resource, the de-identified resource, and any FHIR responses.  
 * 
 * @author Luis A. García
 */
public class DeIdentification {

	private JsonNode originalResource;
	private JsonNode deIdentifiedResource;
	private JsonNode fhirResponse;
	private String fhirLocationHeader;
	
	/**
	 * @return the originalResource
	 */
	public JsonNode getOriginalResource() {
		return originalResource;
	}
	
	/**
	 * @param originalResource the originalResource to set
	 */
	public void setOriginalResource(JsonNode originalResource) {
		this.originalResource = originalResource;
	}
	
	/**
	 * @return the deIdentifiedResource
	 */
	public JsonNode getDeIdentifiedResource() {
		return deIdentifiedResource;
	}
	
	/**
	 * @param deIdentifiedResource the deIdentifiedResource to set
	 */
	public void setDeIdentifiedResource(JsonNode deIdentifiedResource) {
		this.deIdentifiedResource = deIdentifiedResource;
	}
	
	/**
	 * @return the fhirResponse
	 */
	public JsonNode getFhirResponse() {
		return fhirResponse;
	}
	
	/**
	 * @param fhirResponse the fhirResponse to set
	 */
	public void setFhirResponse(JsonNode fhirResponse) {
		this.fhirResponse = fhirResponse;
	}
	
	/**
	 * @return the fhirLocationHeader
	 */
	public String getFhirLocationHeader() {
		return fhirLocationHeader;
	}
	
	/**
	 * @param fhirLocationHeader the fhirLocationHeader to set
	 */
	public void setFhirLocationHeader(String fhirLocationHeader) {
		this.fhirLocationHeader = fhirLocationHeader;
	}
}
