package com.ibm.healthpatterns.rest.controllers;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.healthpatterns.app.CQLExecutionException;
import com.ibm.healthpatterns.app.CohortService;

/**
 * The controller that handles the patients services, within the context of a library.
 * 
 * @author Luis A. Garía
 *
 */
@RestController
@RequestMapping("/cohort-service/libraries/{id}")
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
	 * @param id the library id
	 * @return the list of patients
	 */
	@GetMapping("/patientIDs")
	public @ResponseBody ResponseEntity<String> getPatientIds(@PathVariable String id) {
		List<String> cohort;
		try {
			cohort = cohortService.getPatientIdsForCohort(id);
		} catch (CQLExecutionException e) {
			return cqlExecutionExceptionResponse(e);
		}
		if (cohort == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
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
	 * @param id the library id
	 * @return the list of patients
	 */
	@GetMapping("/patients")
	public @ResponseBody ResponseEntity<String> getPatients(@PathVariable String id) {
		String fhirResponse;
		try {
			fhirResponse = cohortService.getPatientsForCohort(id);
		} catch (CQLExecutionException e) {
			return cqlExecutionExceptionResponse(e);
		}
		if (fhirResponse == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(fhirResponse);
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
