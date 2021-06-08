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
package com.ibm.healthpatterns.app;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.Patient;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.cohort.engine.CqlEvaluator;
import com.ibm.cohort.engine.DirectoryLibrarySourceProvider;
import com.ibm.cohort.engine.MultiFormatLibrarySourceProvider;
import com.ibm.cohort.engine.TranslatingLibraryLoader;
import com.ibm.cohort.engine.translation.CqlTranslationProvider;
import com.ibm.cohort.engine.translation.InJVMCqlTranslationProvider;
import com.ibm.cohort.fhir.client.config.FhirClientBuilder;
import com.ibm.cohort.fhir.client.config.FhirClientBuilderFactory;
import com.ibm.cohort.fhir.client.config.FhirServerConfig;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.parser.IParser;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.util.BundleUtil;

/**
 * The {@link CohortService} allows consumers to save CQL library files and execute them against
 * patients in a FHIR server.
 * 
 * @author Luis A. García
 */
public class CohortService {

	private static final Path CQL_DIRECTORY = Paths.get(System.getProperty("java.io.tmpdir"), "cqls");
	
	private static final CohortService INSTANCE = new CohortService();
	
	private FhirServerConfig fhirConnectionInfo;
	private Map<String, CQLFile> cqls;

	private IGenericClient fhir;

	private CqlEvaluator cqlEngine;

	/**
	 * @return the singleton instance of the {@link CohortService}
	 */
	public static CohortService getInstance() {
		return INSTANCE;
	}
	
	private CohortService() {
		cqls = new TreeMap<>();
		loadDefaultFHIRConfig();
		initializeCQLDirectory();
		initializeCQLEngine();
		loadCQLLibraries();
		installDefaultCQLLibraries();
	}

	/**
	 * Loads the default FHIR configuration for the FHIR server to whcih the service will connect to query patients.
	 */
	private void loadDefaultFHIRConfig() {
		ObjectMapper mapper = new ObjectMapper();
		ClassPathResource fhirFile = new ClassPathResource("config/default-ibm-fhir.json");
		try {
			fhirConnectionInfo = mapper.readValue(fhirFile.getInputStream(), FhirServerConfig.class);
		} catch (JsonMappingException e) {
			System.err.println("The default IBM FHIR connection JSON file does not match the corresponding connection class: " + e.getMessage());
		} catch (JsonProcessingException e) {
			System.err.println("The default IBM FHIR connection JSON file is not valid JSON: " + e.getMessage());
		} catch (IOException e) {
			System.err.println("The default IBM FHIR connection file could not be read or found: " + e.getMessage());
		}
	}

	/**
	 * Loads the default CQL libraries that are commonly used, such as the FHIRHelpers.cql, and register them with this service.
	 */
	private void installDefaultCQLLibraries() {
		// We use this Spring Framework utility class because when packaged the /cql is inside a JAR and this
		// class helps resolve the /cql classpath entry as a directory and iterate over its files
		PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
		Resource[] resources;
		try {
			resources = resolver.getResources("classpath:cql/*.*");
		} catch (IOException e) {
			System.err.println("The default CQL directory could not be loaded, default CQLs won't be available: " + e.getMessage());
			return;		
		}
		for (Resource cql : resources) {
			CQLFile cqlFile;
			try {
				cqlFile = new CQLFile(cql.getInputStream());
			} catch (IOException e) {
				System.err.println("The default CQL file " + cql.getFilename() + " could not be read: " + e.getMessage());
				continue;
			}
			if (getLibrary(cqlFile.getId()) == null) {
				try {
					System.out.println("Installing default CQL file: " + cqlFile.getFileName() + "...");
					addLibrary(cqlFile.getContent());
				} catch (IllegalArgumentException e) {
					System.err.println("The default CQL file " + cql + " is not valid CQL: " + e.getMessage());
				} catch (IOException e) {
					System.err.println("The default CQL file " + cql + " could not be added to the library: " + e.getMessage());
				}
			}
		}
	}

	/**
	 * Load the known CQL libraries to memory.
	 */
	private void loadCQLLibraries() {
		List<Path> defaultCQLs;
		try {
			defaultCQLs = Files.list(CQL_DIRECTORY).collect(Collectors.toList());
		} catch (IOException e) {
			System.err.println("The CQL directory could not be traversed, existing CQLs won't be available: " + e.getMessage());
			return;
		}
		for (Path cql : defaultCQLs) {
			try {
				CQLFile cqlFile = new CQLFile(cql);
				cqls.put(cqlFile.toString(), cqlFile);
			} catch (IOException e) {
				System.err.println("Problem reading existing CQL file: " + e.getMessage());
			}
		}
	}

	/**
	 * Initializes the directory where CQL files are persisted. 
	 */
	private void initializeCQLDirectory() {
		if (Files.exists(CQL_DIRECTORY)) {
			System.out.println("Using existing CQLs directory: " + CQL_DIRECTORY);
			return;
		}
		try {
			Files.createDirectories(CQL_DIRECTORY);
			System.out.println("Created CQLs directory: " + CQL_DIRECTORY);			
		} catch (IOException e) {
			System.out.println("Could not create CQLs directory " + CQL_DIRECTORY + ": " + e.getMessage());
		}
	}

	/**
	 * Initialized the CQL engine (using the instance's FHIR connection info) runnig over the {@value #CQL_DIRECTORY}.
	 */
	private void initializeCQLEngine() {
		FhirClientBuilderFactory factory = FhirClientBuilderFactory.newInstance();
		FhirContext fhirContext = FhirContext.forR4();
		// Currently the socket connection  may time out on a FHIR server 
		// with several dozen patients so increasing the timeout to avoid that
		fhirContext.getRestfulClientFactory().setSocketTimeout(60 * 1000);
		FhirClientBuilder fhirBuilder = factory.newFhirClientBuilder(fhirContext);
		fhir = fhirBuilder.createFhirClient(fhirConnectionInfo);
		System.out.println("Created FHIR connection to " + fhirConnectionInfo.getEndpoint());
		cqlEngine = new CqlEvaluator();
		cqlEngine.setDataServerClient(fhir);
		cqlEngine.setMeasureServerClient(fhir);
		cqlEngine.setTerminologyServerClient(fhir);
		resetCQLDirectory();
	}

	/**
	 * Reload the CQL directory into the CQL Engine.
	 */
	private void resetCQLDirectory() {
		MultiFormatLibrarySourceProvider sourceProvider;
		try {
			sourceProvider = new DirectoryLibrarySourceProvider(CQL_DIRECTORY);
		} catch (Exception e) {
			System.err.println("Problem accessing the directory library source provider on the CQL repository: " + e.getMessage());
			e.printStackTrace();
			return;
		}
		CqlTranslationProvider translationProvider = new InJVMCqlTranslationProvider(sourceProvider);
		cqlEngine.setLibraryLoader(new TranslatingLibraryLoader(sourceProvider, translationProvider, true));
		System.out.println("Re-initialized CQL Engine over directory " + CQL_DIRECTORY);
	}
	
	/**
	 * @return the FHIR connection info object
	 */
	public FhirServerConfig getFHIRConnectionInfo() {
		return fhirConnectionInfo;
	}

	/**
	 * Updates the FHIR connection info
	 * 
	 * @param fhirConnectionInfo 
	 */
	public void updateFHIRConecetionInfo(FhirServerConfig fhirConnectionInfo) {
		this.fhirConnectionInfo = fhirConnectionInfo;
		initializeCQLEngine();
	}

	/**
	 * Adds the given library to the {@link CohortService}. 
	 * 
	 * @param cql the CQL file
	 * @return the new {@link CQLFile} created 
	 * @throws IllegalArgumentException if the given CQL is invalid or if it already exists
	 * @throws IOException if there is a problem adding the library to this cohort service
	 */
	public CQLFile addLibrary(String cql) throws IllegalArgumentException, IOException {
		CQLFile cqlFile = new CQLFile(cql);
		if (cqls.containsKey(cqlFile.getId())) {
			throw new IllegalArgumentException("This library already exists, it is possible to use the update API to modify it if needed.");
		}
		Path path = Paths.get(CQL_DIRECTORY.toString(), cqlFile.getFileName());
		// We persist the library for the next time the service starts
		Files.copy(new ByteArrayInputStream(cql.getBytes()), path, StandardCopyOption.REPLACE_EXISTING);
		cqls.put(cqlFile.toString(), cqlFile);
		resetCQLDirectory();
		System.out.println("Added new CQL file: " + cqlFile.getFileName());
		return cqlFile;
	}

	/**
	 * @return all the known CQL libraries to this service
	 */
	public Collection<CQLFile> getLibraries() {
		return cqls.values();
	}

	/**
	 * @param libraryId the library ID
	 * @return the {@link CQLFile} that matches the corresponding library ID, or null if it does not exist
	 */
	public CQLFile getLibrary(String libraryId) {
		return cqls.get(libraryId);
	}

	/**
	 * Updates the given library. 
	 * 
	 * @param id the library ID
	 * @param cql the updated CQL file
	 * @return the updated {@link CQLFile}, or null if the CQL did not exist initially  
	 * @throws IllegalArgumentException if the given CQL is invalid or if it already exists
	 * @throws IOException if there is a problem adding the library to this cohort service
	 */
	public CQLFile updateLibrary(String id, String cql) throws IllegalArgumentException, IOException {
		if (!cqls.containsKey(id)) {
			return null;
		}
		CQLFile cqlFile = new CQLFile(cql);
		Path path = Paths.get(CQL_DIRECTORY.toString(), cqlFile.getFileName());
		// We persist the library for the next time the service starts
		Files.copy(new ByteArrayInputStream(cql.getBytes()), path, StandardCopyOption.REPLACE_EXISTING);
		cqls.put(cqlFile.toString(), cqlFile);
		return cqlFile;
	}

	/**
	 * @param library the library to delete
	 * @return the deleted {@link CQLFile} or null if it did not exist
	 * @throws IOException if there is a problem deleting the library to this cohort service 
	 */
	public CQLFile deleteLibrary(String library) throws IOException {
		CQLFile cqlFile = cqls.remove(library);
		if (cqlFile != null) {
			Path path = Paths.get(CQL_DIRECTORY.toString(), cqlFile.getFileName());
			Files.delete(path);
		}
		return cqlFile;
	}

	/**
	 * Gets a list of patient IDs that matched the cohort defined by the given library ID.
	 * 
	 * @param libraryID the library ID
	 * @param patientsSubset the subset of patients over which to execute the cohort
	 * @param reverseMatch run the CQL such that only the patients that don't match it are returned 
	 * @return the list of patients that matched, an empty list if none matched, or null if the library ID does not exist
	 * @throws CQLExecutionException if there is a problem executing the library 
	 */
	public List<String> getPatientIdsForCohort(String libraryID, List<String> patientsSubset, boolean reverseMatch) throws CQLExecutionException {
		CQLFile cql = cqls.get(libraryID);
		if (cql == null) {
			return null;
		}
		List<Patient> patients = new ArrayList<>();
		List<String> cohort = new ArrayList<>();

		String theSearchUrl = fhir.getServerBase() + "/Patient?_count=1000";
		if (!patientsSubset.isEmpty()) {
			theSearchUrl += "&_id=" + String.join(",", patientsSubset);
		}
		Bundle bundle = fhir.search()
				   .byUrl(theSearchUrl)
				   .returnBundle(Bundle.class)
				   .execute();

		if (bundle.getTotal() == 0) {
			return cohort;
		}
		patients.addAll(BundleUtil.toListOfResourcesOfType(fhir.getFhirContext(), bundle, Patient.class));
		
		List<String> patientIds = getPatientIds(patients);
		
		// TODO: Add support for parameters
		// parameters = parseParameterArguments(arguments.parameters);
		try {
			cqlEngine.evaluate(cql.getName(), cql.getVersion(), null, null, patientIds, new CQLExecutionCallback(cohort, reverseMatch));
		} catch (Exception e) {
			throw new CQLExecutionException(e);
		}
		return cohort;
	}

	/**
	 * Gets the FHIR response with the patients that matched the cohort defined by the given library ID.
	 * 
	 * @param libraryID the library ID
	 * @param patientsSubset the subset of patients over which to execute the cohort
	 * @param reverseMatch run the CQL such that only the patients that don't match it are returned
	 * @return the FHIR JSON response (a Bundle) with all the patients that matched
	 * @throws CQLExecutionException if there is a problem executing the library 
	 */
	public String getPatientsForCohort(String libraryID, List<String> patientsSubset, boolean reverseMatch) throws CQLExecutionException {
		List<String> cohortPatients = getPatientIdsForCohort(libraryID, patientsSubset, reverseMatch);
		if (cohortPatients == null) {
			return null;
		}
		String theSearchUrl = fhir.getServerBase() + "/Patient?_id=" + String.join(",", cohortPatients);
		Bundle cohortBundle = fhir.search()
				   .byUrl(theSearchUrl)
				   .returnBundle(Bundle.class)
				   .execute();
				   
		IParser parser = fhir.getFhirContext().newJsonParser();
		String serialized = parser.encodeResourceToString(cohortBundle);
		return serialized;
	}

	/**
	 * Gets a list of patient IDs from the given list of patients
	 * 
	 * @param patients the patients
	 * @return the list of patient ids
	 */
	private List<String> getPatientIds(List<Patient> patients) {
		List<String> ids = new ArrayList<>();
		for (Patient patient : patients) {
			// For some reason the ID is the full URL of the history resource
			// e.g. http://e8a618a7-us-south.lb.appdomain.cloud/fhir-server/api/v4/Patient/1772aebdfd1-6301ff57-eda3-46ba-8944-f6ab0a1223b1/_history/1
			// Hence we do the following to get just the UUID
			String[] idElements = patient.getId().split("/");
			ids.add(idElements[idElements.length - 3]);
		}
		return ids;
	}
}
