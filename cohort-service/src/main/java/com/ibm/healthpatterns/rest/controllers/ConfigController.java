package com.ibm.healthpatterns.rest.controllers;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.healthpatterns.app.CohortService;

/**
 * The controller that handles the configuration service, currently the only configuration is the FHIR config.
 * 
 * @author Luis A. Garía
 *
 */
@RestController
@RequestMapping("/cohort-service/config")
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
	@RequestMapping(method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON_VALUE)
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
}
