/**
 * 
 */
package com.ibm.healthpatterns.app;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import org.springframework.core.io.ClassPathResource;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.cohort.engine.FhirServerConfig;

/**
 * @author Luis A. Garía
 *
 */
public class CohortService {

	private FhirServerConfig fhirConnectionInfo;
	
	private static final CohortService INSTANCE = new CohortService();
	
	public static CohortService getInstance() {
		return INSTANCE;
	}
	
	private CohortService() {
		ObjectMapper om = new ObjectMapper();
		ClassPathResource fhirFile = new ClassPathResource("config/default-ibm-fhir.json");
		try {
			fhirConnectionInfo = om.readValue(fhirFile.getFile(), FhirServerConfig.class);
		} catch (JsonMappingException e) {
			System.err.println("The default IBM FHIR connection JSON file does not match the corresponding connection class: " + e.getMessage());
			e.printStackTrace();
		} catch (JsonProcessingException e) {
			System.err.println("The default IBM FHIR connection JSON file is not valid JSON: " + e.getMessage());
			e.printStackTrace();
		} catch (IOException e) {
			System.err.println("The default IBM FHIR connection file could not be read or found: " + e.getMessage());
			e.printStackTrace();
		}
	}
	
	public FhirServerConfig getFHIRConnectionInfo() {
		return fhirConnectionInfo;
	}
	
	public void addLibrary(InputStream inputstream) {
		
		
	}
}
