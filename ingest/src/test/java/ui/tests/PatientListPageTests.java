/*
 * (C) Copyright IBM Corp. 2019, 2021
 *
 * SPDX-License-Identifier: Apache-2.0
 */


package ui.tests;

import static org.junit.Assert.assertTrue;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runner.RunWith;

import com.codeborne.selenide.WebDriverRunner;

import ui.pageobjects.PatientList;

public class PatientListPageTests extends TestClass {
	
	static PatientList patientListPage = null;
	
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
		
		// Open the patient-browser
		browseToURL(testURL);
		
		PatientList.sleepWithReason(2, "Wait For Patient List Page to Be Displayed");
	}
	
	/**
	* Sort By Patient IDs Ascending 
	* Press the Sort By Patient IDs button once
	* Scroll through the list of patients and collect the IDs
	* Verify the ID list is in ascending order
	*/
	@Test
	public void sortAscendingByIDTest() throws InterruptedException {

		patientListPage.clickOnSortByID();	
		
        List<String> patientIDs = patientListPage.getPatientIDsOnPage();
        
        // scroll through all pages of the patient list to collect IDs
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {
        	
            patientListPage.clickOnNext();
            
            patientIDs.addAll(patientListPage.getPatientIDsOnPage());
        }
        
        // Go through the list and verify ascending order
        String prevItem = patientIDs.get(0);
        
        for( String id: patientIDs )  {
        	System.out.println(id);
        	if(id.compareTo(prevItem)<0) {
        		assertTrue("Patient ID Ascending Sort Fail",false);
        	}
        	prevItem = id;
        }
		
	}
	
	/**
	* Sort By Patient IDs Descending 
	* Press the Sort By Patient IDs button twice
	* Scroll through the list of patients and collect the IDs
	* Verify the ID list is in descending order
	*/
	@Test
	public void sortDescendingByIDTest() throws InterruptedException {

		// click twice to perform the Descending sort
		patientListPage.clickOnSortByID();			
		patientListPage.clickOnSortByID();
		
        List<String> patientIDs = patientListPage.getPatientIDsOnPage();
        
        // scroll through all pages of the patient list to collect IDs
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {
            
        	patientListPage.clickOnNext();
            
            patientIDs.addAll(patientListPage.getPatientIDsOnPage());
  
        }
        
        // Go through the list and verify descending order
        String prevItem = patientIDs.get(0);
        
        for( String id: patientIDs )  {
        	System.out.println(id);
        	if(id.compareTo(prevItem)>0) {
        		assertTrue("Patient ID Descending Sort Fail",false);
        	}
        	prevItem = id;
        }
		
	}
	
	/**
	* Sort By Patient Names Ascending 
	* Press the Sort By Name button once
	* Scroll through the list of patients and collect the Names (removing titles Mr., Mrs., and Ms.)
	* Verify the Name list is in ascending order
	*/
	@Test
	public void sortAscendingByNameTest() throws InterruptedException {
		
		patientListPage.clickOnSortByName();
		
        List<String> patientNames = patientListPage.getPatientNamesOnPage();
        
        // scroll through all pages of the patient list to collect Names
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {
        	
            patientListPage.clickOnNext();
            
            patientNames.addAll(patientListPage.getPatientNamesOnPage());
            	
        }
        
        // Go through the list and verify ascending order
        String prevItem = patientNames.get(0);
        
        for( String name: patientNames )  {
        	System.out.println(name);
        	if(name.compareTo(prevItem)<0) {
        		assertTrue("Patient Name Ascending Sort Fail",false);
        	}
        	prevItem = name;
        }

	}
	
	/**
	* Sort By Patient Names Descending 
	* Press the Sort By Name button twice
	* Scroll through the list of patients and collect the Names (removing titles Mr., Mrs., and Ms.)
	* Verify the Name list is in descending order
	*/
	@Test
	public void sortDescendingByNameTest() throws InterruptedException {
		
		// click twice to perform the Descending sort
		patientListPage.clickOnSortByName();		
		patientListPage.clickOnSortByName();
		
        List<String> patientNames = patientListPage.getPatientNamesOnPage();
        
        // scroll through all pages of the patient list to collect Names
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {
        	
            patientListPage.clickOnNext();
            
            patientNames.addAll(patientListPage.getPatientNamesOnPage());
        }
       
        // Go through the list and verify descending order
        String prevItem = patientNames.get(0);
        
        for( String name: patientNames )  {
        	System.out.println(name);
        	if(name.compareTo(prevItem)>0) {
        		assertTrue("Patient Name Descending Sort Fail",false);
        	}
        	prevItem = name;
        }

	}
	
	/**
	* Sort By Gender Ascending 
	* Press the Sort By Gender button once
	* Scroll through the list of patients and collect the Genders 
	* Verify the Gender list is in ascending order
	*/
	@Test
	public void sortAscendingByGenderTest() throws InterruptedException {

		patientListPage.clickOnSortByGender();
		
        List<String> patientGenders = patientListPage.getPatientGendersOnPage();
        
        // scroll through all pages of the patient list to collect Genders
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {

	        patientListPage.clickOnNext();
	        
	        patientGenders.addAll(patientListPage.getPatientGendersOnPage());
        }
        
        // Go through the list and verify ascending order
        String prevItem = patientGenders.get(0);
        
        for( String gender: patientGenders )  {
        	System.out.println(gender);
        	if(gender.compareTo(prevItem)<0) {
        		assertTrue("Patient Gender Ascending Sort Fail",false);
        	}
        	prevItem = gender;
        }

	}
	
	/**
	* Sort By Gender Descending 
	* Press the Sort By Gender button twice
	* Scroll through the list of patients and collect the Genders 
	* Verify the Gender list is in descending order
	*/
	@Test
	public void sortDescendingByGenderTest() throws InterruptedException {

		// click twice to perform the Descending sort
		patientListPage.clickOnSortByGender();		
		patientListPage.clickOnSortByGender();
		
        List<String> patientGenders = patientListPage.getPatientGendersOnPage();
        
        // scroll through all pages of the patient list to collect Genders
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {
        
	        patientListPage.clickOnNext();
	        
	        patientGenders.addAll(patientListPage.getPatientGendersOnPage());
        }
        
        // Go through the list and verify descending order
        String prevItem = patientGenders.get(0);
        
        for( String gender: patientGenders )  {
        	System.out.println(gender);
        	if(gender.compareTo(prevItem)>0) {
        		assertTrue("Patient Gender Descending Sort Fail",false);
        	}
        	prevItem = gender;
        }

	}
	
	/**
	* Sort By DOB Ascending 
	* Press the Sort By DOB button once
	* Scroll through the list of patients and collect the DOBs 
	* Verify the DOB list is in ascending order
	*/
	@Test
	public void sortAscendingByDOBTest() throws InterruptedException {

		patientListPage.clickOnSortByDOB();
		
        List<String> patientDOBs = patientListPage.getPatientDOBsOnPage();
        
        // scroll through all pages of the patient list to collect DOBs
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {
        
	        patientListPage.clickOnNext();
	        
	        patientDOBs.addAll(patientListPage.getPatientDOBsOnPage());
        }
        
        // Go through the list and verify ascending order
        String prevItem = patientDOBs.get(0);
        
        for( String dob: patientDOBs )  {
        	System.out.println(dob);
        	if(dob.compareTo(prevItem)<0) {
        		assertTrue("Patient DOB Ascending Sort Fail",false);
        	}
        	prevItem = dob;
        }

	}
	
	/**
	* Sort By DOB Descending 
	* Press the Sort By DOB button twice
	* Scroll through the list of patients and collect the DOBs 
	* Verify the DOB list is in descending order
	*/
	@Test
	public void sortDescendingByDOBTest() throws InterruptedException {

		// click twice to perform the Descending sort
		patientListPage.clickOnSortByDOB();
		patientListPage.clickOnSortByDOB();
		
        List<String> patientDOBs = patientListPage.getPatientDOBsOnPage();
        
        // scroll through all pages of the patient list to collect DOBs
        while(patientListPage.getPatientCountLastOnPage() < patientListPage.getTotalPatientCount()) {
        
	        patientListPage.clickOnNext();
	        
	        patientDOBs.addAll(patientListPage.getPatientDOBsOnPage());
        }
        
     // Go through the list and verify descending order
        String prevItem = patientDOBs.get(0);
        
        for( String dob: patientDOBs )  {
        	System.out.println(dob);
        	if(dob.compareTo(prevItem)>0) {
        		assertTrue("Patient DOB Descending Sort Fail",false);
        	}
        	prevItem = dob;
        }

	}
	
	/**
	* Patient list scrolling test 
	* Press the Sort By DOB button once
	* Scroll forward (Next ->) through the patient list and verify x, y, and z in "patient x to y of z"
	* Scroll backward (<- Prev) through the patient list and verify x, y, and z in "patient x to y of z"
	*/
	@Test
	public void scrollingTest() throws InterruptedException {
		
		
		// Scroll forward through the patient list using "Next ->" and check "patient x to y of z" values on each page
		// Then
		// Scroll backward through the patient list using "<- Prev" and check "patient x to y of z" values on each page

		int firstPatientOnPage = 1;
		int lastPatientOnPage = 25;
		int patientsPerPage = 25;
		int maxPatients = lastPatientOnPage;
		int totalPatients = patientListPage.getTotalPatientCount();
		boolean scrolling = true;
		
		if (lastPatientOnPage > totalPatients) {
			//handle the case when there are the totals number of patients is less than the number of patients on a page
			// there won't be any page scrolling in this test, but  the test won't fail
			lastPatientOnPage = totalPatients;
		}

		//Use the Next-> button to scroll forward through the patient list
		//Check "patient x to y of z" values
		
        while(scrolling) {
        	
        	if (lastPatientOnPage == totalPatients) {
        		// this means were are done scrolling via the Next -> button
        		scrolling = false;
        	}
        	
        	//Check "patient x to y of z" values
        	assertTrue("First patient number error on Next, expecting "+firstPatientOnPage+" actual is "+patientListPage.getPatientCountFirstOnPage(),patientListPage.getPatientCountFirstOnPage()==firstPatientOnPage);
        	assertTrue("Last patient number error on Next, expecting "+lastPatientOnPage+" actual is "+patientListPage.getPatientCountLastOnPage(),patientListPage.getPatientCountLastOnPage()==lastPatientOnPage);
        	
        	// if still scrolling, get ready for scrolling to the next page
        	if (scrolling) {
            	firstPatientOnPage = firstPatientOnPage + patientsPerPage;
            	lastPatientOnPage = lastPatientOnPage + patientsPerPage;
            	maxPatients = lastPatientOnPage;   // this value gets used when the <- Prev scrolling test is executed
            	
            	if (lastPatientOnPage > totalPatients) {
            		lastPatientOnPage = totalPatients;
            	} 
            	
            	patientListPage.clickOnNext();
            	PatientList.sleepWithReason(1, "Wait page scrolling to complete");   		
        	}       	  
        }
        
        scrolling = true;   // reset for the <-Prev test
        
        while(scrolling)  {
        	
        	if( firstPatientOnPage == 1) {
        		// done scrolling if on the first page of the Patient List
        		scrolling = false;
        	}
        	assertTrue("First patient number error on Prev, expecting "+firstPatientOnPage+" actual is "+patientListPage.getPatientCountFirstOnPage(),patientListPage.getPatientCountFirstOnPage()==firstPatientOnPage);
        	assertTrue("Last patient number error on Prev, expecting "+lastPatientOnPage+" actual is "+patientListPage.getPatientCountLastOnPage(),patientListPage.getPatientCountLastOnPage()==lastPatientOnPage);
        	
        	// If still scrolling, get setup for scrolling to the prev page.
           	if (scrolling) {
           		
            	firstPatientOnPage = firstPatientOnPage - patientsPerPage;
            	
            	if ((lastPatientOnPage+patientsPerPage)>maxPatients) {
            		lastPatientOnPage = maxPatients-patientsPerPage;
            	}
            	else  {
            		lastPatientOnPage = lastPatientOnPage - patientsPerPage;
            	}
           	      		
            	patientListPage.clickOnPrev();
            	PatientList.sleepWithReason(1, "Wait page scrolling to complete");   		
        	} 
        	
        
        }
        
	}
	
	/**
	* A method that runs after each test to close the web page  
	*/
	@After
	public void cleanUpTest() throws InterruptedException{
		
	    closeURL();
	    
	}

}
