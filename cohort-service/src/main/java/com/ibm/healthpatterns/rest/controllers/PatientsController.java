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

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.healthpatterns.app.CQLExecutionException;
import com.ibm.healthpatterns.app.CohortService;

/**
 * The controller that handles the patients services, within the context of a library.
 * 
 * @author Luis A. García
 */
@RestController
@RequestMapping("/libraries/{libraryID}")
public class PatientsController {

	private CohortService cohortService;

	/**
	 * 
	 */
	public PatientsController() {
		cohortService = CohortService.getInstance();
	}

	/**
	 * 
	 * @param libraryID the library id
	 * @param ids the optional list of patient IDs to run the cohort, instead of using all patients in the FHIR server
	 * @param reverse run the CQL engine with a reversed where only the patients that don't match the cohort are returned
	 * @return the list of patients
	 */
	@GetMapping("/patientIds")
	public @ResponseBody ResponseEntity<String> getPatientIds(@PathVariable String libraryID, 
															  @RequestParam(required = false) String ids,
															  @RequestParam(required = false) String reverse) {
		List<String> patientIds = parsePatientIDs(ids);
		boolean reverseMatch = parseReverse(reverse);
		List<String> cohort;
		try {
			cohort = cohortService.getPatientIdsForCohort(libraryID, patientIds, reverseMatch);
		} catch (CQLExecutionException e) {
			return cqlExecutionExceptionResponse(e);
		}
		if (cohort == null) {
			return new ResponseEntity<String>("Library with ID '" + libraryID + "' was not found.", HttpStatus.NOT_FOUND);
		}
		ObjectMapper mapper = new ObjectMapper();
		String json;
		try {
			json = mapper.writeValueAsString(cohort);
		} catch (JsonProcessingException e) {
			return new ResponseEntity<String>("Could not serialize cohort: " + e, HttpStatus.INTERNAL_SERVER_ERROR);	
		}
		return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(json);
	}

	/**
	 * 
	 * @param libraryID the library id
	 * @param ids the optional list of patient IDs to run the cohort, instead of using all patients in the FHIR server
	 * @param reverse run the CQL engine with a reversed where only the patients that don't match the cohort are returned
	 * @return the list of patients
	 */
	@GetMapping("/patients")
	public @ResponseBody ResponseEntity<String> getPatients(@PathVariable String libraryID, 
															@RequestParam(required = false) String ids,
															@RequestParam(required = false) String reverse) {
		List<String> patientIds = parsePatientIDs(ids);
		boolean reverseMatch = parseReverse(reverse);
		String fhirResponse;
		try {
			fhirResponse = cohortService.getPatientsForCohort(libraryID, patientIds, reverseMatch);
		} catch (CQLExecutionException e) {
			return cqlExecutionExceptionResponse(e);
		}
		if (fhirResponse == null) {
			return new ResponseEntity<String>("Library with ID '" + libraryID + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(fhirResponse);
	}

	private List<String> parsePatientIDs(String ids) {
		List<String> patientIDs = new ArrayList<>();
		if (ids == null || ids.trim().isEmpty()) {
			return patientIDs;
		}
		String[] idsArray = ids.split(",");
		for (String id : idsArray) {
			patientIDs.add(id.trim());
		}
		return patientIDs;
	}

	private boolean parseReverse(String reverse) {
		if (reverse == null || reverse.trim().isEmpty()) {
			return false;
		}
		return Boolean.valueOf(reverse);
	}

	private ResponseEntity<String> cqlExecutionExceptionResponse(CQLExecutionException e) {
		StringWriter sw = new StringWriter();
		PrintWriter pw = new PrintWriter(sw);
		pw.println("Error in the Cohort Engine executing the given library.");
		pw.println();
		e.printStackTrace(pw);
		return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
				.contentType(MediaType.TEXT_PLAIN)
				.body(sw.toString());
	}
}
