/*
 * (C) Copyright IBM Corp. 2022
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

package ui.pageobjects;


import static com.codeborne.selenide.Selenide.$;

import java.util.ArrayList;
import java.util.List;

import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

public class PatientList extends PageClass{
	
	public PatientList(WebDriver driver)
	{
		super(driver);
	}
	
	// private element locator methods
	
	/**
	* A method to locate the web element that contains the "patient x to y of z" string 
	*/
	private WebElement patientCount() {
		try {
			return $(By.className("text-center"));
		} catch (NoSuchElementException|TimeoutException e) {
			return null;
		}
	}
	
	/**
	* A method to locate each patient on the patient list page and return a list of patient web elements
	*/
	private List<WebElement> patientListOnPage() {
		List<WebElement> plist = null;
		plist =  waitAndFindElements(By.className("patient"));
		return plist;
	}
	
	/**
	* A method to locate the "<- Prev" button
	*/
	private WebElement prevButton() {
		return waitAndFindElement(By.className("fa-arrow-left"));
	}
	
	/**
	* A method to locate the "Next ->" button
	*/
	private WebElement nextButton() {
		return waitAndFindElement(By.className("fa-arrow-right"));
	}
	
	/**
	* A method to locate desired Sort By button
	* @param string name of the Sort By button to locate/return
	*/
	private WebElement sortButton(String buttonName) {
		
		WebElement sortButton = null;
		WebElement sortSection = waitAndFindElement(By.className("nav-pills"));
		List<WebElement> sortButtons = sortSection.findElements(By.xpath("//li"));
		
		for(WebElement button: sortButtons) {
			if (button.getText().contains(buttonName)) {
				sortButton = button;
			}
		}
		
		return sortButton;
	}
	
	/**
	* A method to locate the "Patient ID" Sort By button
	*/
	private WebElement sortByIDButton() {
		
		return sortButton("Patient");
	}
	
	/**
	* A method to locate the "Name" Sort By button
	*/
	private WebElement sortByNameButton() {
		
		return sortButton("Name");
	}
	
	/**
	* A method to locate the "Gender" Sort By button
	*/
	private WebElement sortByGenderButton() {
		
		return sortButton("Gender");
	}
	
	/**
	* A method to locate the "DOB" Sort By button
	*/
	private WebElement sortByDOBButton() {
		
		return sortButton("DOB");
	}
	
	// public actions
	
	/**
	* A method to return the "patient x to y of z" string 
	*/
	public String getPatientCounts() {
		return patientCount().getText();
	}
	
	/**
	* A method to return "z" in the "patient x to y of z" string 
	*/
	public int getTotalPatientCount() {
		
		int totalPatients = 0;	
		String patientCounts = getPatientCounts();
		if(patientCounts.contains("patient")) {
			int posOfTotal = patientCounts.indexOf("of")+3;		
			totalPatients = Integer.parseInt(patientCounts.substring(posOfTotal));
		}

		return totalPatients;
	}
	
	/**
	* A method to return "x" in the "patient x to y of z" string 
	*/
	public int getPatientCountFirstOnPage() {
		
		int firstPatientOnPage = 0;	
		String patientCounts = getPatientCounts();
		if(patientCounts.contains("patient")) {
			int endPos = patientCounts.indexOf("to")-1;		
			firstPatientOnPage = Integer.parseInt(patientCounts.substring(8,endPos));
		}

		return firstPatientOnPage;
	}

	/**
	* A method to return "y" in the "patient x to y of z" string 
	*/
	public int getPatientCountLastOnPage() {
		
		int lastPatientOnPage = 0;	
		String patientCounts = getPatientCounts();
		if(patientCounts.contains("patient")) {
			int startPos = patientCounts.indexOf("to")+3;
			int endPos = patientCounts.indexOf("of")-1;		
			lastPatientOnPage = Integer.parseInt(patientCounts.substring(startPos,endPos));
		}

		return lastPatientOnPage;
	}
	
	/**
	* A method to return a list of patient IDs for each patient listed on the page
	*/
	public List<String> getPatientIDsOnPage()  {
		
		List<String> patientIDs = new ArrayList<String>();
		String pID;
		int idStart;
		int idEnd;
		
		List<WebElement> plist = patientListOnPage();
		
		for (WebElement patient: plist  )  {
			
			pID = patient.getText();
			idStart = pID.indexOf("ID: ") + 4;
			idEnd = idStart+37;
			pID = pID.substring(idStart,idEnd);
			patientIDs.add(pID);
			
		}
		
		return patientIDs;
		
	}
	
	/**
	* A method to return a list of patient Names (excluding MR., Mrs, and Ms. titles) for each patient listed on the page
	*/
	public List<String> getPatientNamesOnPage()  {
		
		List<String> patientNames = new ArrayList<String>();
		String pName;
		int nameStart;
		int nameEnd;
		
		List<WebElement> plist = patientListOnPage();
		
		for (WebElement patient: plist  )  {
			
			pName = patient.getText();
			nameStart = 0;
			nameEnd = pName.indexOf("\n");
			pName = pName.substring(nameStart,nameEnd);
			
			// Strip off titles
			if(pName.contains("Mr.") || pName.contains("Ms.")) {
				pName = pName.substring(4);
			}
			else if(pName.contains("Mrs.")) { 
				pName = pName.substring(5);
			}

			patientNames.add(pName);
			
		}
		
		return patientNames;
		
	}
	
	/**
	* A method to return a list of patient DOBs (date of birth) for each patient listed on the page
	*/
	public List<String> getPatientDOBsOnPage()  {
		
		List<String> patientDOBs = new ArrayList<String>();
		String pDOB;
		int dobStart;
		int dobEnd;
		
		List<WebElement> plist = patientListOnPage();
		
		for (WebElement patient: plist  )  {
			
			pDOB = patient.getText();
			dobStart = pDOB.indexOf("DOB: ") + 5;
			dobEnd = dobStart+10;
			pDOB = pDOB.substring(dobStart,dobEnd);
			patientDOBs.add(pDOB);
			
		}
		
		return patientDOBs;
		
	}
	
	/**
	* A method to return a list of patient genders for each patient listed on the page
	*/
	public List<String> getPatientGendersOnPage()  {
		
		List<String> patientGenders = new ArrayList<String>();
		String pGender;
		int genderStart;
		int genderEnd;
		
		List<WebElement> plist = patientListOnPage();
		
		for (WebElement patient: plist  )  {
			
			pGender = patient.getText();
			genderStart = pGender.indexOf("year old ") + 9;
			genderEnd = pGender.substring(genderStart).indexOf("\n");
			pGender = pGender.substring(genderStart).substring(0,genderEnd);
			patientGenders.add(pGender);
			
		}
		
		return patientGenders;
		
	}

	/**
	* A method to click on the Sort By Patient ID button
	*/
	public void clickOnSortByID() {	
		sortByIDButton().click();	
	}
	/**
	* A method to click on the Sort By Patient Name button
	*/
	public void clickOnSortByName() {
		sortByNameButton().click();
	}
	
	/**
	* A method to click on the Sort By Patient Gender button
	*/
	public void clickOnSortByGender() {
		sortByGenderButton().click();
	}
	
	/**
	* A method to click on the Sort By Patient DOB button
	*/
	public void clickOnSortByDOB() {
		sortByDOBButton().click();
	}
	
	/**
	* A method to click on the "<- Prev" button
	*/
	public void clickOnPrev() {
		prevButton().click();
	}
	
	/**
	* A method to click on the "Next ->" button
	*/
	public void clickOnNext() {
		nextButton().click();
	}


}


