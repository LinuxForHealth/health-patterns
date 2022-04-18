package ui.tests;

import org.openqa.selenium.Keys;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.HasAuthentication;
import org.openqa.selenium.UsernameAndPassword;

import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;


import com.codeborne.selenide.WebDriverRunner;
import static com.codeborne.selenide.Selenide.open;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Properties;

import static com.codeborne.selenide.Selenide.closeWebDriver;

public class TestClass  {
	
	protected static WebDriver theWebDriver;

	protected final Logger LOGGER = LoggerFactory.getLogger(TestClass.class);
	
    protected static Properties envProps = new Properties();
    
    protected static String testURL;
    protected static String headlessTest;
	
	protected static void driverSetup() throws InterruptedException,IOException,FileNotFoundException {
		
        // load test env properties
	    envProps.load(new FileInputStream("src/test/resources/clinical-ingestion-flow.properties"));
		testURL = envProps.get("patient-browser").toString();
		headlessTest = envProps.get("patient-browser-headless").toString();
		
		// setup for Chrome in the test
		ChromeOptions options = new ChromeOptions();
		options.addArguments("--no-sandbox"); // Bypass OS security model
		options.addArguments("--disable-dev-shm-usage"); // overcome limited resource problems
		options.addArguments("--disable-extensions"); // disabling extensions
		
		// set headless option based on the properties
		if(headlessTest.contains("true")) {
			options.setHeadless(true);   
		}
		else {
			options.setHeadless(false);
		}

		
		System.setProperty("webdriver.chrome.driver","/usr/local/bin/chromedriver");
		
		theWebDriver = new ChromeDriver(options);  
		
		
	/*	System.setProperty("webdriver.gecko.driver","/usr/local/bin/geckodriver"); */
	/*	System.setProperty("webdriver.firefox.bin","/usr/local/bin/chromedriver");  */
		
	/*	FirefoxOptions options = new FirefoxOptions(); */
	/*	options.setHeadless(false);  */
	/*	theWebDriver = new FirefoxDriver(options); */
		
		((HasAuthentication) theWebDriver).register(UsernameAndPassword.of("fhiruser", "integrati0n"));
		
	/*	theWebDriver.get(url);  */
 
		
		WebDriverRunner.setWebDriver(theWebDriver);
		
		
	}
	
	
	protected static void browseToURL(String url) throws InterruptedException {
			
		open(url);
		
	}
	
	protected static void closeURL() throws InterruptedException {
		
		WebDriverRunner.closeWindow();
		WebDriverRunner.closeWebDriver();
		
		
	}
	
	
}
