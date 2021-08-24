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
import java.net.URI;
import java.util.Collection;

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

/**
 * The controller that handles the library services (CRUD operations for libraries).
 *  
 * @author Luis A. García
 */
@RestController
@RequestMapping("/libraries")
public class LibrariesController {

	private CohortService cohortService;

	/**
	 * 
	 */
	public LibrariesController() {
		cohortService = CohortService.getInstance();
	}

	/**
	 * 
	 * @return all available libraries
	 */
	@GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
	public @ResponseBody ResponseEntity<String> getLibraries() {
		ObjectMapper mapper = new ObjectMapper();
		String json;
		Collection<CQLFile> libraries = cohortService.getLibraries();
		for (CQLFile cqlFile : libraries) {
			URI uri = ServletUriComponentsBuilder
	                .fromCurrentRequest()
	                .path("/{id}")
	                .buildAndExpand(cqlFile.getId())
	                .toUri();		
			cqlFile.setUri(uri.toString());
		}
		try {
			json = mapper.writeValueAsString(libraries);
		} catch (JsonProcessingException e) {
			return new ResponseEntity<String>("Could not map connection info: " + e, HttpStatus.INTERNAL_SERVER_ERROR);	
		}
		return new ResponseEntity<String>(json, HttpStatus.OK);
	}

	/**
	 * 
	 * @param cql
	 * @return the response of adding a new library
	 * @throws IOException
	 */
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
		return ResponseEntity.created(location).body("CQL created! - URI: " + location);
	}

	/**
	 * 
	 * @param id
	 * @return the library by the given ID
	 */
	@GetMapping("/{id}")
	public @ResponseBody ResponseEntity<String> getLibrary(@PathVariable String id) {
		CQLFile cql = cohortService.getLibrary(id);
		if (cql == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return ResponseEntity.ok().contentType(MediaType.TEXT_PLAIN).body(cql.getContent());
	}

	/**
	 * 
	 * @param id
	 * @param cql
	 * @return the response of updating the given library
	 * @throws IOException
	 */
	@PutMapping("/{id}")
	public @ResponseBody ResponseEntity<String> updateLibrary(@PathVariable String id, @RequestBody String cql) throws IOException {
		CQLFile updatedCQL = cohortService.updateLibrary(id, cql);
		if (updatedCQL == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return new ResponseEntity<String>("CQL Updated!", HttpStatus.OK);
	}	
	
	/**
	 * 
	 * @param id
	 * @return the response of updating the given library
	 * @throws IOException
	 */
	@DeleteMapping("/{id}")
	public @ResponseBody ResponseEntity<String> deleteLibrary(@PathVariable String id) throws IOException {
		CQLFile cql = cohortService.deleteLibrary(id);
		if (cql == null) {
			return new ResponseEntity<String>("Library with ID '" + id + "' was not found.", HttpStatus.NOT_FOUND);
		}
		return new ResponseEntity<String>("CQL Deleted!", HttpStatus.OK);
	}	
}
