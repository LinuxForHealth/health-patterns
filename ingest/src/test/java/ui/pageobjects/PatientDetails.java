/*
 * (C) Copyright IBM Corp. 2022
 *
 * SPDX-License-Identifier: Apache-2.0
 */

package ui.pageobjects;


import static com.codeborne.selenide.Selenide.$;

import java.util.HashMap;
import java.util.List;

import org.openqa.selenium.By;
import org.openqa.selenium.NoSuchElementException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

public class PatientDetails extends PageClass{
	
	public PatientDetails(WebDriver driver)
	{
		super(driver);
	}
	
	// private element locator methods
	
	/**
	* A method to locate the patient details element
	*/
	private WebElement patientName() {
		return waitAndFindElement(By.className("patient-name"));
	}
	
	/**
	* A method to locate the patient summary element
	*/
	private WebElement patientSummary() {
			return waitAndFindElement(By.className("patient")).findElement(By.className("row")).findElement(By.className("row"));
	}
	
	/**
	* A method to locate the patient details element
	*/
	private WebElement patientDetails() {
		return waitAndFindElement(By.className("patient-details"));
	}
	
	/**
	* A method to locate the patient resource list element within the patient details element
	*/
	private WebElement patientResources() {
		return patientDetails().findElement(By.className("list-group"));
	}	
	
	/**
	* A method to locate the patient resource table element
	*/
	private WebElement patientResourceDetails() {
		return patientDetails().findElement(By.className("table"));
	}
	
	/**
	* A method to locate the selected (or active) patient resource in the patient resource list
	*/
	private WebElement selectedResource() {
		return patientResources().findElement(By.className("active"));
	}
	
	/**
	* A method to locate the nlp popup table
	*   NOTE: This only works to verify the popup when the popup is displayed.  
	*         There is an empty element with id=popup-root when the popup is not displayed, but selenium only finds it when it is not empty
	*/
	private boolean nlpPopupDisplayed() {
		
		return waitAndFindElement(By.id("popup-root")).findElement(By.className("table")).isDisplayed();
	}
	
	
	
	/**
	* A method to locate the nlp popup table
	*   NOTE: This only works when the popup when the popup is displayed.  
	*         There is an empty element with id=popup-root when the popup is not displayed, but selenium only finds it when it is not empty 
	*/
	private WebElement nlpPopup() {
		
		WebElement popUp = waitAndFindElement(By.id("popup-root"));
		
		return popUp.findElement(By.className("table"));
	}
	
	/**
	* A method to locate a specified resource from the list of resources
	*/
	private WebElement resourceEntry(String resourceName) {
		
		List<WebElement> resourceList = patientResources().findElements(By.className("list-group-item"));
		WebElement theResource = null;
		for(WebElement resource: resourceList) {
			
			if(resource.getText().contains(resourceName)) {
				theResource = resource;
			}	
		}
				
		return theResource;
	}

	/**
	* A method to locate the specified NLP Light Bulb Button in the resource details table by the aria-describedBy text
	*/
	private WebElement nlpLightBulbButton(String ariaLabel) {
		return patientDetails().findElement(By.cssSelector("button[aria-describedby='"+ariaLabel+"'"));
	}
	
	/**
	* A method check if the specified Resource is selected in the list of resources on the page
	*/
	private boolean isResourceSelected(String resource) {	
		boolean resourceIsSelected = false;		
		if(getSelectedResource().contains(resource)) {
			resourceIsSelected = true;
		}		
		return resourceIsSelected;		
	}
	
	/**
	 * A method to return the highlighted text in the nlp data popup for a resource
	 */
	
	private String highLightedNLPText() {
		
		WebElement popUp = waitAndFindElement(By.id("popup-root"));
		
		return popUp.findElement(By.className("search-match")).getText();

	}

	
	// public actions
	
	/**
	* A method to locate & return the text of the selected patient resource
	*/
	public String getSelectedResource() {	
		return selectedResource().getText();
	}
	
	/**
	* A method to return the patient's name from the summary section
	*/
	public String getPatientName() {
		return patientName().getText();
	}
	
	/**
	* A method to return the patient's DOB from the summary section
	*/
	public String getPatientDOB() {

		String pDOB = patientSummary().getText();
		int pDateStart = pDOB.indexOf("DOB:\n")+5;
		int pDateEnd = pDOB.indexOf("Age:\n")-1;
		
		pDOB = pDOB.substring(pDateStart, pDateEnd);
	
		return pDOB;
	}

	/**
	* A method check if the Patient Resource is selected in the list of resources on the page
	*/
	public boolean isPatientResourceSelected() {		
		return isResourceSelected("Patient");		
	}
	
	/**
	* A method check if the Condition Resource is selected in the list of resources on the page
	*/
	public boolean isConditionResourceSelected() {		
		return isResourceSelected("Condition");		
	}

	/**
	 * A method to return the list of resources for the patient in a HashMap
	 */
	public HashMap<String,String> getPatientResourceList() {
		
		HashMap<String,String> resourceList = new HashMap<String,String>();
		
		String resources = patientResources().getText();
		
		String resourceCount;
		String resourceName;
		
		while(!resources.isEmpty()) {
			resourceCount = resources.substring(0,resources.indexOf("\n"));
			resources = resources.substring(resources.indexOf("\n")+1);

			// if on the last resource in the list, there won't be a \n
			if (resources.contains("\n")) {
				resourceName = resources.substring(0,resources.indexOf("\n"));
				resources = resources.substring(resources.indexOf("\n")+1);
			}
			else {
				// last resource in the list so take the remaining string as the name
				resourceName = resources;
				resources = "";
			}

			resourceList.put(resourceName, resourceCount);
		}
		
		return resourceList;
		
	}

	/**
	 * A method to select the Condition resource in the list of resources
	 */
	public void selectConditionResourceInList() {
		resourceEntry("Condition").click();
	}
	
	/**
	 * A method to press the first NLP Light bulb button in the table of resource details
	 */
	public void pressTheFirstNLPButton() {
		nlpLightBulbButton("popup-1").click();
	}

	/**
	 * A method to check if the nlp popup table is displayed
	 */
	public boolean isNLPPopupDisplayed() {
		
		return nlpPopupDisplayed();

	}
	
	/**
	 * A method to check if the nlp popup table is displayed
	 */
	public String[] getNLPInfo() {
		
		return nlpPopup().getText().split("\n");

	}

	/**
	 * A method to get the hightlighted text in the nlp "light bulb" pop-up 
	 */
	public String getNLPHighLightedText() {
		
		return highLightedNLPText();
		
	}


}


