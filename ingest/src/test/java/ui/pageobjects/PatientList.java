/*******************************************************************************
 * IBM Confidential OCO Source Materials
 * 5737-D31, 5737-A56
 * (C) Copyright IBM Corp. 2021
 *
 * The source code for this program is not published or otherwise
 * divested of its trade secrets, irrespective of what has
 * been deposited with the U.S. Copyright Office.
 *******************************************************************************/
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
	private WebElement patientCount() {
		try {
			return $(By.className("text-center"));
		} catch (NoSuchElementException|TimeoutException e) {
			return null;
		}
	}
	
	private List<WebElement> patientListOnPage() {
		List<WebElement> plist = null;
		plist =  waitAndFindElements(By.className("patient"));
		return plist;
	}
	
	private WebElement prevButton() {
		return waitAndFindElement(By.className("fa-arrow-left"));
	}
	
	private WebElement nextButton() {
		return waitAndFindElement(By.className("fa-arrow-right"));
	}
	
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
	
	private WebElement sortByIDButton() {
		
		return sortButton("Patient");
	}
	
	private WebElement sortByNameButton() {
		
		return sortButton("Name");
	}
	
	private WebElement sortByGenderButton() {
		
		return sortButton("Gender");
	}
	
	private WebElement sortByDOBButton() {
		
		return sortButton("DOB");
	}
	
	// public actions
	
	public String getPatientCounts() {
		return patientCount().getText();
	}
	
	public int getTotalPatientCount() {
		
		int totalPatients = 0;	
		String patientCounts = getPatientCounts();
		if(patientCounts.contains("patient")) {
			int posOfTotal = patientCounts.indexOf("of")+3;		
			totalPatients = Integer.parseInt(patientCounts.substring(posOfTotal));
		}

		return totalPatients;
	}
	
	public int getPatientCountFirstOnPage() {
		
		int firstPatientOnPage = 0;	
		String patientCounts = getPatientCounts();
		if(patientCounts.contains("patient")) {
			int endPos = patientCounts.indexOf("to")-1;		
			firstPatientOnPage = Integer.parseInt(patientCounts.substring(8,endPos));
		}

		return firstPatientOnPage;
	}
	
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

	public void clickOnSortByID() {	
		sortByIDButton().click();	
	}

	public void clickOnSortByName() {
		sortByNameButton().click();
	}
	
	public void clickOnSortByGender() {
		sortByGenderButton().click();
	}
	
	public void clickOnSortByDOB() {
		sortByDOBButton().click();
	}
	
	public void clickOnPrev() {
		prevButton().click();
	}
	public void clickOnNext() {
		nextButton().click();
	}


}


