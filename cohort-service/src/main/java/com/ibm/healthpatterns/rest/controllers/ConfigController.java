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
package com.ibm.healthpatterns.rest.controllers;

import java.io.IOException;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.cohort.fhir.client.config.FhirServerConfig;
import com.ibm.healthpatterns.app.CohortService;

/**
 * The controller that handles the configuration service, currently the only configuration is the FHIR config.
 * 
 * @author Luis A. García
 */
@RestController
@RequestMapping("/config")
public class ConfigController {

	private CohortService cohortService;
	
	/**
	 * 
	 */
	public ConfigController() {
		cohortService = CohortService.getInstance();
	}
	
	/**
	 * 
	 * @return the response
	 */
	@GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
	public @ResponseBody ResponseEntity<String> getFHIRConfig() {
		ObjectMapper mapper = new ObjectMapper();
		String json;
		try {
			json = mapper.writeValueAsString(cohortService.getFHIRConnectionInfo());
		} catch (JsonProcessingException e) {
			return new ResponseEntity<String>("Could not map connection info: " + e, HttpStatus.INTERNAL_SERVER_ERROR);	
		}
		return new ResponseEntity<String>(json, HttpStatus.OK);
	}

	/**
	 * 
	 * @param fhirConnection
	 * @return the response of updating the given library
	 * @throws IOException
	 */
	@PutMapping
	public @ResponseBody ResponseEntity<String> updateLibrary(@RequestBody String fhirConnection) throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		FhirServerConfig fhirConnectionInfo;
		try {
			fhirConnectionInfo = mapper.readValue(fhirConnection, FhirServerConfig.class);
		} catch (JsonMappingException e) {
			return new ResponseEntity<String>("The FHIR connection JSON does not match the corresponding connection class: " + e.getMessage(), HttpStatus.BAD_REQUEST);
		} catch (JsonProcessingException e) {
			return new ResponseEntity<String>("The FHIR connection JSON is not valid JSON: " + e.getMessage(), HttpStatus.BAD_REQUEST);
		} 
		cohortService.updateFHIRConecetionInfo(fhirConnectionInfo);
		return new ResponseEntity<String>("FHIR Connection Updated!", HttpStatus.OK);
	}	

}
