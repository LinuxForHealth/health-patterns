/**
 * 
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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.cohort.engine.CqlEngineWrapper;
import com.ibm.cohort.engine.DirectoryLibrarySourceProvider;
import com.ibm.cohort.engine.FhirClientBuilder;
import com.ibm.cohort.engine.FhirClientBuilderFactory;
import com.ibm.cohort.engine.FhirServerConfig;
import com.ibm.cohort.engine.MultiFormatLibrarySourceProvider;
import com.ibm.cohort.engine.TranslatingLibraryLoader;
import com.ibm.cohort.engine.translation.CqlTranslationProvider;
import com.ibm.cohort.engine.translation.InJVMCqlTranslationProvider;

import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.util.BundleUtil;

/**
 * The {@link CohortService} allows consumers to save CQL library files and execute them against
 * patients in a FHIR server.
 * 
 * @author Luis A. Garía
 *
 */
public class CohortService {

	private static final Path CQL_DIRECTORY = Paths.get(System.getProperty("java.io.tmpdir"), "cqls");

	private static final CohortService INSTANCE = new CohortService();
	
	private FhirServerConfig fhirConnectionInfo;
	private Map<String, CQLFile> cqls;
	
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
		loadDefaultCQLLibraries();
		loadCQLLibraries();
	}

	/**
	 * Loads the default FHIR configuration for the FHIR server to whcih the service will connect to query patients.
	 */
	private void loadDefaultFHIRConfig() {
		ObjectMapper mapper = new ObjectMapper();
		ClassPathResource fhirFile = new ClassPathResource("config/default-ibm-fhir.json");
		try {
			fhirConnectionInfo = mapper.readValue(fhirFile.getFile(), FhirServerConfig.class);
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
	private void loadDefaultCQLLibraries() {
		ClassPathResource cqlDirectoryResource = new ClassPathResource("cql");
		Path cqlDirectory;
		try {
			cqlDirectory = cqlDirectoryResource.getFile().toPath();
		} catch (IOException e) {
			System.err.println("The default CQL directory could not be loaded, default CQLs won't be available: " + e.getMessage());
			return;
		}
		List<Path> defaultCQLs;
		try {
			defaultCQLs = Files.list(cqlDirectory).collect(Collectors.toList());
		} catch (IOException e) {
			System.err.println("The default CQL directory " + cqlDirectory + " could not be traversed, default CQLs won't be available: " + e.getMessage());
			return;
		}
		for (Path cql : defaultCQLs) {
			try {
				CQLFile cqlFile = new CQLFile(cql);
				cqls.put(cqlFile.toString(), cqlFile);
			} catch (IOException e) {
				System.err.println("The default CQL file " + cql + " could not be read: " + e.getMessage());
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
	 * @return the FHIR connection info object
	 */
	public FhirServerConfig getFHIRConnectionInfo() {
		return fhirConnectionInfo;
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
		if (cqls.containsKey(id)) {
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
	 * @return the list of patients that matched, an empty list if none matched, or null if the library ID does not exist
	 */
	public List<String> getPatients(String libraryID) {
		CQLFile cql = cqls.get(libraryID);
		if (cql == null) {
			return null;
		}
		FhirClientBuilderFactory factory = FhirClientBuilderFactory.newInstance();
		FhirClientBuilder builder = factory.newFhirClientBuilder();
		IGenericClient fhir = builder.createFhirClient(fhirConnectionInfo);
		List<Patient> patients = new ArrayList<>();

		// We'll do a search for all Patients and extract the first page
		Bundle bundle = fhir
		   .search()
		   .forResource(Patient.class)
		   .returnBundle(Bundle.class)
		   .count(1000)
		   .execute();
		patients.addAll(BundleUtil.toListOfResourcesOfType(fhir.getFhirContext(), bundle, Patient.class));
		List<String> patientIds = getPatientIds(patients);
		
		CqlEngineWrapper wrapper = new CqlEngineWrapper(builder);
		wrapper.setDataServerConnectionProperties(fhirConnectionInfo);
		wrapper.setMeasureServerConnectionProperties(fhirConnectionInfo);
		wrapper.setTerminologyServerConnectionProperties(fhirConnectionInfo);
		
		MultiFormatLibrarySourceProvider sourceProvider;
		try {
			sourceProvider = new DirectoryLibrarySourceProvider(CQL_DIRECTORY);
		} catch (Exception e) {
			System.err.println("Problem creating the directoryu library source provider on the CQL repository: " + e.getMessage());
			e.printStackTrace();
			return null;
		}		
		List<String> cohort = new ArrayList<>();
		CqlTranslationProvider translationProvider = new InJVMCqlTranslationProvider(sourceProvider);
		wrapper.setLibraryLoader(new TranslatingLibraryLoader(sourceProvider, translationProvider, true));
		// TODO: Add support for parameters
		// parameters = parseParameterArguments(arguments.parameters);
		try {
			wrapper.evaluate(cql.getName(), cql.getVersion(), null, null, patientIds, new CQLExecutionCallback(cohort));
		} catch (Exception e) {
			e.printStackTrace();
		}
//		String theSearchUrl = fhir.getServerBase() + "/Patient?_id=" + String.join(",", cohort);
//		System.out.println(theSearchUrl);
//		Bundle cohortBundle = fhir.search()
//				   .byUrl(theSearchUrl)
//				   .returnBundle(Bundle.class)
//				   .execute();
//				   
//		System.out.println("cohort" + cohortBundle.getTotal());
		return cohort;
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
