package com.ibm.healthpatterns.rest.controllers;

import java.io.IOException;
import java.net.URI;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.healthpatterns.app.CQLFile;
import com.ibm.healthpatterns.app.CohortService;

@RestController
@RequestMapping("/cohort-service/libraries")
public class LibrariesController {

	private CohortService cohortService;

	/**
	 * 
	 */
	public LibrariesController() {
		cohortService = CohortService.getInstance();
	}

	@GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
	public @ResponseBody ResponseEntity<String> getLibraries() {
		ObjectMapper mapper = new ObjectMapper();
		String json;
		try {
			json = mapper.writeValueAsString(cohortService.getLibraries());
		} catch (JsonProcessingException e) {
			return new ResponseEntity<String>("Could not map connection info: " + e, HttpStatus.INTERNAL_SERVER_ERROR);	
		}
		return new ResponseEntity<String>(json, HttpStatus.OK);
	}

	@PostMapping
	public ResponseEntity<String> addLibrary(@RequestBody String cql) throws IOException {
		CQLFile cqlFile;
		try {
			cqlFile = cohortService.addLibrary(cql);
		} catch (IllegalArgumentException e) {
			return new ResponseEntity<String>(e.getMessage(), HttpStatus.BAD_REQUEST);
		}
		URI location = ServletUriComponentsBuilder
                .fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(cqlFile.getId())
                .toUri();		
		return ResponseEntity.created(location).build();
	}

	@GetMapping("/{id}")
	public @ResponseBody ResponseEntity<String> getLibrary(@PathVariable String id) {
		CQLFile cql = cohortService.getLibrary(id);
		if (cql == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return new ResponseEntity<String>(cql.getContent(), HttpStatus.OK);
	}

	@PutMapping("/{id}")
	public @ResponseBody ResponseEntity<String> updateLibrary(@PathVariable String id, @RequestBody String cql) throws IOException {
		CQLFile updatedCQL = cohortService.updateLibrary(id, cql);
		if (updatedCQL == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return new ResponseEntity<String>("CQL Updated!", HttpStatus.OK);
	}	
	
	@DeleteMapping("/{id}")
	public @ResponseBody ResponseEntity<String> deleteLibrary(@PathVariable String id) throws IOException {
		CQLFile cql = cohortService.deleteLibrary(id);
		if (cql == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return new ResponseEntity<String>("CQL Deleted!", HttpStatus.OK);
	}	
}
