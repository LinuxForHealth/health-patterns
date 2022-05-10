/*
 * (C) Copyright IBM Corp. 2022
 *
 * SPDX-License-Identifier: Apache-2.0
 */


package ui.tests;

import static org.junit.Assert.assertTrue;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;

import com.codeborne.selenide.WebDriverRunner;

import ui.pageobjects.PatientDetails;
import ui.pageobjects.PatientList;

public class PatientDetailsPageTests extends TestClass {
	
	static PatientList patientListPage = null;
	static PatientDetails patientDetailsPage = null;
	
	// test patient details used for verification of patient details and quickumls
	static String testPatientID = "c3ef31a1-eba9-43f4-b935-0bf60846f7b1";
	static String testPatientName = "Mr. Emanuel231 Rutherford999";
	static String testPatientDOB = "1978-12-25";
	static HashMap<String,String> testPatientResourceList = new HashMap<String,String>();
	
	static String[] testPatientQuickUmlsData = {"Insight Source Resource Self",
			                                    "Insight Source Resource Location Condition.code.text",
			                                    "Resource Element Insight Pertains to Condition.code.coding"};
	
	
	// patient data for ACD tests
	static String testPatientForACDID = "c70e2a78-1e77-4eb1-8215-8b83351ce009";
	static String[] testPatientACDData = {"Insight Source Resource DiagnosticReport 0192be49-eddd-44df-8870-89b9140965f3",
            "Insight Source Resource Location DiagnosticReport.presentedForm[0].data",
            "Covered Text \"Patient has diabetes and aortic regurgitation.\" [12:20]",
            "Confidence 99.6%"};
	static String testPatientHighlightACD = "diabetes";

	/**
	 * A method to verify patient summary information
	 */
	private void verifyPatientSummaryDetails() {
		
		// Verify selected (meaning not all) patient data in the summary section at the top
		assertTrue("Expected '"+testPatientName+"' but found '"+patientDetailsPage.getPatientName()+"'",patientDetailsPage.getPatientName().contains(testPatientName));
		assertTrue("Expected '"+testPatientDOB+"' but found '"+patientDetailsPage.getPatientDOB()+"'",patientDetailsPage.getPatientDOB().equals(testPatientDOB));
		
		// Verify the list of patient resources (resource name and number of resources)
		assertTrue("Patient Resource List is not correct.  \nExpected: '"+testPatientResourceList.toString()+"'\nFound: '"+patientDetailsPage.getPatientResourceList().toString(),patientDetailsPage.getPatientResourceList().equals(testPatientResourceList));
		
		// Verify the patient resource is selected in the list of patient resources
		assertTrue("Expected the Patient Resource to be selected but found "+patientDetailsPage.getSelectedResource()+" is selected.",patientDetailsPage.isPatientResourceSelected());

		
	}
	
	
	/**
	* A method that runs before each test to set up the selenium environment 
	* and loads the patient list page
	*/
	@Before
	public void setupForTest() throws InterruptedException,IOException,FileNotFoundException
	{
		// Setup Up the selenium/selenide structure and create the page objects
		driverSetup();		
		patientListPage = new PatientList(theWebDriver);
		patientDetailsPage = new PatientDetails(theWebDriver);
		
		//Set up the expected patient list of resources
		testPatientResourceList.put("CarePlan",                  "1");
		testPatientResourceList.put("CareTeam",                  "1");
		testPatientResourceList.put("Claim",                     "8");
		testPatientResourceList.put("Condition",                 "3");
		testPatientResourceList.put("DiagnosticReport",          "6");
		testPatientResourceList.put("Encounter",                 "6");
		testPatientResourceList.put("ExplanationOfBenefit",      "6");
		testPatientResourceList.put("Goal",                      "5");
		testPatientResourceList.put("Immunization",              "6");
		testPatientResourceList.put("MedicationRequest",         "2");
		testPatientResourceList.put("Observation - Laboratory",  "46");
		testPatientResourceList.put("Observation - Survey",      "4");
		testPatientResourceList.put("Observation - Vital Signs", "20");
		testPatientResourceList.put("Patient",                   "1");
		testPatientResourceList.put("Procedure",                 "7");
		
		
		// Open the patient-browser to the patient list page
		browseToURL(testURL);
		
		PatientList.sleepWithReason(2, "Wait For Patient List Page to Be Displayed");
		
	}

	
	
	/**
	* Patient Details Page Basic Verification
	*   Load a specific known patient
	*   Verify patient name and DOB in the summary section at the top
	*   Verify the list of patient resources (resource name and number of resources)
	*   Verify the patient resource is selected in the list of patient resources
	*/
	@Test
	public void testVerifyPatientDetails() throws InterruptedException {
		
		// Load a specific known patient
		patientListPage.openPatientDetails(testPatientID);
		PatientList.sleepWithReason(2, "Waiting for Patient Details to load.");
		
		// verify the Patient summary details
		verifyPatientSummaryDetails();
	}
	
	/**
	* Verify the display of an enriched resource (Condition)
	*   Load a specific known patient
	*   Select a patient resource known to be enriched (Condition)
	*   Press the light bulb button to display information about the enriched resource
	*   Basic verification of the enriched data information displayed in the popup window
	*/
	@Test
	public void testVerifyQuickUmlsDataDisplay() throws InterruptedException {
       
		patientListPage.openPatientDetails(testPatientID);
		PatientList.sleepWithReason(2, "Waiting for Patient Details to load.");
		
		patientDetailsPage.selectConditionResourceInList();
		PatientList.sleepWithReason(2, "Wait for the Condition resource to be displayed.");
		assertTrue("Expected Condition resource to be selected, but found "+patientDetailsPage.getSelectedResource(),patientDetailsPage.isConditionResourceSelected());

		patientDetailsPage.pressTheFirstNLPButton();
		assertTrue("NLP Popup not displayed as expected.",patientDetailsPage.isNLPPopupDisplayed());
		
		int i = 0;
	    for(String data: testPatientQuickUmlsData) {
	    	assertTrue("quickumls data error: \n Expected: '"+data+"' \n Received: '"+patientDetailsPage.getNLPInfo()[i]+"'",data.equals(patientDetailsPage.getNLPInfo()[i]));
	    	i++;
	    }
	}
	
	/**
	* Verify the display of an ACD-enriched resource (Condition)
	*   Load a specific known patient (using the open to a specific patient function)
	*   Select a patient resource known to be enriched (Condition)
	*   Press the light bulb button to display information about the enriched resource
	*   Basic verification of the enriched data information displayed in the popup window
	*   Verify the expected text is highlighted
	*/
	@Test
	public void testVerifyACDDataDisplay() throws InterruptedException {
       
		String patientURL = testURL + "/#/id/"+testPatientForACDID;  // add the patient data to the base URL
		// open browser directly to the patient details page
		browseToURL(patientURL);
		PatientList.sleepWithReason(2, "Waiting for Patient Details to load.");
		
		patientDetailsPage.selectConditionResourceInList();
		PatientList.sleepWithReason(2, "Wait for the Condition resource to be displayed.");
		assertTrue("Expected Condition resource to be selected, but found "+patientDetailsPage.getSelectedResource(),patientDetailsPage.isConditionResourceSelected());

		patientDetailsPage.pressTheFirstNLPButton();
		PatientList.sleepWithReason(2, "Wait for the Condition resource to be displayed.");
		assertTrue("NLP Popup not displayed as expected.",patientDetailsPage.isNLPPopupDisplayed());
		
	    
		int i = 0;
	    for(String data: testPatientACDData) {
	    	assertTrue("ACD data error: \n Expected: '"+data+"' \n Received: '"+patientDetailsPage.getNLPInfo()[i]+"'",data.equals(patientDetailsPage.getNLPInfo()[i]));
	    	i++;
	    }
	    
	    // Verify the highlighted text
	    assertTrue("Expected ACD Highlighted text '"+testPatientHighlightACD+"' but found '"+patientDetailsPage.getNLPHighLightedText()+"'",patientDetailsPage.getNLPHighLightedText().equals(testPatientHighlightACD));
	    
	}
	
	/**
	* Open the patient browser to a specific known patient
	*   Verify patient name and DOB in the summary section at the top
	*   Verify the list of patient resources (resource name and number of resources)
	*   Verify the patient resource is selected in the list of patient resources
	*/
	@Test
	public void testOpenBrowserToSpecificPatient() throws InterruptedException {
    
		String patientURL = testURL + "/#/id/"+testPatientID;  // add the patient data to the base URL
	
		// open browser directly to the patient details page
		browseToURL(patientURL);
		
		PatientList.sleepWithReason(2, "Wait for patient details to load.");
		
		// verify the Patient summary details
		verifyPatientSummaryDetails();
		
	}
	
	
	/**
	* A method that runs after each test to close the web page  
	*/
	@After
	public void cleanUpTest() throws InterruptedException{
		
	    closeURL();
	    
	}

}
