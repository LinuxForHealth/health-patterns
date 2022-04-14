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

import static com.codeborne.selenide.Selenide.open;
import static org.junit.Assert.assertTrue;

import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLDecoder;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebDriverException;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.codeborne.selenide.WebDriverRunner;

public abstract class PageClass {

	protected static WebDriver theWebDriver;
	protected boolean initialized = false;
	protected String testURLnoLogonInfo;
	protected String initialWindowHandle;
	protected static Properties setupProperties = new Properties();
    private static final Logger LOGGER = LoggerFactory.getLogger(PageClass.class);

	// public static final Properties setupProperties =
	public static final String browser = getBrowserType();
	public static String FIREFOX = "Firefox";
	public static String CHROME = "Chrome";

	public PageClass() {

	}

	public PageClass(WebDriver driver) {
		theWebDriver = driver;
	}
	
	/**
	* A method to specify a pause for a specified length of time
	* @param seconds the amount of time to sleep in seconds
	* @param reason The reason for sleeping
	*/
	public static void sleepWithReason(int seconds, String reason) {
		try {
			int inMilliseconds = seconds * 1000;
			LOGGER.info("sleeping for " + seconds + " seconds. Reason: " + reason);
			Thread.sleep(inMilliseconds);
		} catch (InterruptedException e) {
			Thread.currentThread().interrupt();

		}
	}

	/**
	* A method to specify a pause for a specified length of time
	* @param seconds the amount of time to sleep in seconds
	*/
	public static void sleep(int seconds) {
		try {
			int inMilliseconds = seconds * 1000;
			LOGGER.info("sleeping for " + seconds + " seconds");
			Thread.sleep(inMilliseconds);
		} catch (InterruptedException e) {
			Thread.currentThread().interrupt();
		}
	}

	/**
	 * Indicates the browser in use (i.e. Firefox, Chrome, etc)
	 * NOTE currently only Firefox is used in Interop
	 * @return the type of browser
	 */
	public static String getBrowserType() {
		return setupProperties.getProperty("test.browser", "Firefox");
	}

	/**
	 * Method to indicate whether or not an element is visible on the page
	 * @param locator
	 * @return True if on the page and currently displayed, False if it is not
	 */
	protected boolean isElementVisible(By locator) {
		boolean found = true;
		try {
			found = waitAndFindElement(locator).isDisplayed();
		} catch (Exception e) {
			found = false;

			System.out.println(" Exception isElementVisible");
		}
		return found;
	}

	/**
	 * Method to indicate whether or not an element is visible on the page
	 * @param secondsPerWait Amount of time to wait for the element
	 * @param waitsToAttempt Number of times to check for the element
	 * @param locator
	 * @return
	 */
	protected boolean isElementVisible(int secondsPerWait, int waitsToAttempt, By locator) {
		boolean found = true;
		try {
			found = waitAndFindElement(secondsPerWait, waitsToAttempt, locator).isDisplayed();
		} catch (Exception e) {
			found = false;

			System.out.println(" Exception isElementVisible");
		}
		return found;
	}

	/**
	 * Method to indicate if a web page element is clickable (i.e. a button)
	 * @param secondsPerWait Amount of time to wait for the element
	 * @param locator
	 * @return
	 */
	protected boolean isElementClickable(int secondsPerWait, By locator) {
		boolean found = true;
		try {
			found = waitAndFindClickableElement(secondsPerWait, locator).isDisplayed();
		} catch (Exception e) {
			found = false;

			System.out.println("Exception isElementClickable");
		}
		return found;
	}

	/**
	 * Method to locate a web page element
	 * @param secondsPerWait Amount of time to wait for the element
	 * @param waitsToAttempt Number of times to check for the element
	 * @param locator
	 * @return
	 */
	protected WebElement waitAndFindElement(int secondsPerWait, int waitsToAttempt, By locator) {
		boolean elementFound = false;
		int count = 0;
		WebElement elementIs = null;
		while (count < waitsToAttempt && !elementFound) {
			count++;
			LOGGER.info("Attempting to check for element with locator " + locator + " . Iteration: " + count);
			try {
				elementIs = new WebDriverWait(theWebDriver, secondsPerWait).pollingEvery(Duration.ofSeconds(1))
						.until(ExpectedConditions.visibilityOfElementLocated(locator));
				if (elementIs != null)
					elementFound = true;
			} catch (Exception e) {
				LOGGER.info("Exception thrown while waitAndFindElement: " + e.getCause());
			}
		}
		if (elementIs == null) {
			LOGGER.info(locator + " element is still not found after waiting for " + secondsPerWait * waitsToAttempt
					+ " seconds...performing one final try");
			elementIs = new WebDriverWait(theWebDriver, secondsPerWait).pollingEvery(Duration.ofSeconds(1))
					.until(ExpectedConditions.visibilityOfElementLocated(locator));
		}

		if (elementIs != null) {

			if (browser.contains("InternetExplorer"))
				makeVisible(elementIs);
		}
		return elementIs;

	}

	/**
	 * Method to locate a web page element by using parent/child locators
	 * @param timeOutInSecs Amount of time to wait for the element
	 * @param parentLocator
	 * @param childLocator
	 * @return
	 */
	protected WebElement waitAndFindElement(long timeOutInSecs, By parentLocator, By childLocator) {
		try {
			WebElement element = new WebDriverWait(theWebDriver, timeOutInSecs).pollingEvery(Duration.ofSeconds(2))
					.until(ExpectedConditions.presenceOfNestedElementLocatedBy(parentLocator, childLocator));
			return new WebDriverWait(theWebDriver, timeOutInSecs).pollingEvery(Duration.ofSeconds(2))
					.until(ExpectedConditions.visibilityOf(element));
		} catch (Exception e) {
			LOGGER.info("Exception thrown while waitAndFindElement with parent & child locator: " + e.getCause());
			return null;
		}
	}
	
	/**
	 * Method to locate a web page element.
	 * Uses the default wait of 40 seconds (4 retries with 10 seconds in between)
	 * @param locator
	 * @return
	 */
	protected WebElement waitAndFindElement(By locator) {
		return waitAndFindElement(10, 4, locator);

	}

	/*
	 * wait for elements to be visible AND use parent child locators. It more than
	 * one elements match parent locator it uses the first one ONLY
	 */
	protected List<WebElement> waitAndFindElements(long timeOutInSecs, By parentLocator, By childLocator) {
		try {
			List<WebElement> elements = new WebDriverWait(theWebDriver, timeOutInSecs).pollingEvery(Duration.ofSeconds(2))
					.until(ExpectedConditions.presenceOfNestedElementsLocatedBy(parentLocator, childLocator));
			return new WebDriverWait(theWebDriver, timeOutInSecs).pollingEvery(Duration.ofSeconds(2))
					.until(ExpectedConditions.visibilityOfAllElements(elements));
		} catch (Exception e) {
			LOGGER.info("Exception thrown while waitAndFindElement with parent & child locator: " + e.getCause());
			return null;
		}
	}

	/**
	 * Method to verify a web page element is not displayed.  
	 * Uses default wait of 10 seconds
	 * @param locator
	 */
	protected void waitAndLoseElement(By locator) {
		waitAndLoseElement(10, locator, null);

	}

	/**
	 * Method to verify a web page element is not displayed.  
	 * Uses default wait of 10 seconds
	 * @param locator
	 * @param reason The reason to wait for the web page element to disappear
	 */
	protected void waitAndLoseElement(By locator, String reason) {
		waitAndLoseElement(10, locator, reason);

	}

	/**
	 * Method to verify a web page element is not displayed
	 * @param timeOutInSecs Amount of time to wait for the element to disappear
	 * @param locator
	 * @param reason The reason to wait for the web page element to disappear
	 */
	public void waitAndLoseElement(long timeOutInSecs, By locator, String reason) {
		boolean elementFound = true;
		int count = 0;
		while (count < 30 && elementFound) {
			count++;
			if (reason != null & reason.length() > 0) {
				LOGGER.info(reason + " count=" + count);
			} else {
				LOGGER.info("Attempting to check for the element is gone, trying  times..." + count);
			}
			try {
				new WebDriverWait(getWebDriver(), timeOutInSecs).pollingEvery(Duration.ofSeconds(1))
						.until(ExpectedConditions.invisibilityOfElementLocated(locator));
				elementFound = false;
			} catch (Exception e) {
				// e.printStackTrace();
				LOGGER
						.info("Exception thrown while waitAndLoseElement for " + timeOutInSecs + " : " + e.getCause());
			}
		}
		if (elementFound) {
			assertTrue(locator
					+ " element STILL FOUND (Failing here because this item never disappeared which means next step can't proceed)",
					false);
		}
	}

	/**
	 * Method to locate a web page element that should be clickable (i.e. a button)
	 * @param timeOutInSecs Amount of time to wait for the element
	 * @param locater
	 * @return
	 */
	protected WebElement waitAndFindClickableElement(long timeOutInSecs, By locater) {
		return new WebDriverWait(theWebDriver, timeOutInSecs).pollingEvery(Duration.ofSeconds(1))
				.until(ExpectedConditions.elementToBeClickable(locater));
	}

	/**
	 * Method to locate a list of web page elements
	 * @param timeOutInSecst Amount of time to wait for the elements
	 * @param locator
	 * @return
	 */
	protected List<WebElement> waitAndFindElements(long timeOutInSecs, By locator) {
		List<WebElement> elements = null;
		try {
			elements = new WebDriverWait(theWebDriver, timeOutInSecs).pollingEvery(Duration.ofSeconds(2))
					.until(ExpectedConditions.visibilityOfAllElementsLocatedBy(locator));
		} catch (Exception e) {
			LOGGER.error("Element(s) not found " + e.getMessage());
		}

		return elements;
	}

	/**
	 * Method to locate a list of web page elements
	 * @param locator
	 * @return
	 */
	protected List<WebElement> waitAndFindElements(By locator) {
		return waitAndFindElements(10, locator);
	}	

	/**
	 * Method to scroll to element if it is not currently visible on the page
	 * @param element
	 */
	protected void makeVisible(WebElement element) {
		int elementX = element.getLocation().x;
		int elementY = element.getLocation().y;
		int screenXMax = theWebDriver.manage().window().getSize().getWidth();
		int screenYMax = theWebDriver.manage().window().getSize().getHeight();
		if (elementX < 20 || elementX > screenXMax - 20 || elementY < 20 || elementY > screenYMax - 20) {
			LOGGER.info("Element location is x: " + elementX + " y: " + elementY + " and requires scrolling.");
			((JavascriptExecutor) theWebDriver).executeScript("arguments[0].scrollIntoView(true);", element);
			sleepWithReason(2, "Ensuring scroll has completed.");
		}
	}


	/**
	 * @param url
	 *            is the url for the browser to open
	 * @param newBrowser
	 *            if true the current browser will close and a new one opened with the specified url
	 */
	public static void browseToURL(String url, String browserType, Map<String, String> propMap) {
		
		LOGGER.info("In method browseToURL");
		
		for (Map.Entry<String, String> entry : propMap.entrySet()) {
			System.out.println("Setting browser property " + entry.getKey() + " " + entry.getValue());
			System.setProperty(entry.getKey(), entry.getValue());
		}
		
		if(browserType.equalsIgnoreCase(CHROME)) {
			LOGGER.info("Browser is Chrome");
			ChromeOptions options = new ChromeOptions();
			options.addArguments("--no-sandbox"); // Bypass OS security model
			options.addArguments("--disable-dev-shm-usage"); // overcome limited resource problems
			options.addArguments("--disable-extensions"); // disabling extensions
			options.setHeadless(true);

			try {
				theWebDriver = new ChromeDriver(options);
			}
			catch(Exception e) {
				LOGGER.error(e.getMessage());
			}
		}
		
		else { //Default to Firefox
			LOGGER.info("Browser is Firefox");
			FirefoxOptions options = new FirefoxOptions();
			options.setHeadless(true);
			theWebDriver = new FirefoxDriver(options);
		}

		try {
			if(theWebDriver != null) {
				//Toggle this line in and the others in this block off
				//to not use Selenide
				//theWebDriver.get(url);
				WebDriverRunner.setWebDriver(theWebDriver);
				open(url);
			}
			else LOGGER.error("Problems initializing theWebDriver");
			
		} catch (Exception e) {
			//If exception is that we reached error page, this is expected with certain tests
			//such as invalid scopes
			if(e.getMessage().startsWith("Reached error page:"))
				return;
			else throw e;
		}

	}

	/*
	 * Method to scroll to a specified element
	 */
	protected void scrollToElement(WebElement elem) {
		// ((JavascriptExecutor)
		// theWebDriver).executeScript("arguments[0].scrollIntoView(true);",elem);
		JavascriptExecutor js = (JavascriptExecutor) theWebDriver;
		js.executeScript("arguments[0].scrollIntoView(true);", elem);
	}

	/**
	 * Provide a mechanism for us to go back on the browser.
	 */
	public void selectBackOnBrowser() {
		LOGGER.info("Selecting back button on the browser.");
		JavascriptExecutor js = (JavascriptExecutor) theWebDriver;
		js.executeScript("javascript: setTimeout(\"history.go(-1)\",2000)");
		theWebDriver.navigate().back();
	}

	/**
	 * Method to return the web driver for the class
	 */
	public WebDriver getWebDriver() {
		return theWebDriver;
	}

	/**
	 * Method to scroll to the top of the screen
	 */
	public void scrollToTopOfScreen() {
		JavascriptExecutor jse = (JavascriptExecutor) theWebDriver;
		jse.executeScript("window.scrollTo(0,0)");
	}

	/**
	 * Method to refresh the browser page
	 */
	public void refreshBrowser() {
		getWebDriver().navigate().refresh();
	}
	
	/**
	 * This method examines the URL and if there is a code set (i.e. code=XYZ) the code is returned
	 * @return the code set in the URL
	 * @throws InterruptedException
	 */
	public static String getCodeFromBrowser() throws InterruptedException{
		
        Map<String, String> response = new HashMap<String, String>();
        // poll at 500 ms interval until 'code' is present in URL query parameter list.
        // Usually this loop completes in  under 2.5 seconds.
        for ( int i =0; i< 50; i++)
        {
            sleepWithReason(1, "Short pause to let browser to its work");
            LOGGER.debug("driver url before exception path: " + theWebDriver.getCurrentUrl());
            
            String[] pairs;
            try {
                pairs = new URI(theWebDriver.getCurrentUrl()).getQuery().split("&");
                for (String pair : pairs) {
                    int idx = pair.indexOf("=");
                    response.put(URLDecoder.decode(pair.substring(0, idx), "UTF-8"), 
                            URLDecoder.decode(pair.substring(idx + 1), "UTF-8"));
                }

            } catch (URISyntaxException e) {
                // catch exception -- hopefully next URL is successful
                e.printStackTrace();
            } catch ( UnsupportedEncodingException e ) {
                // catch exception -- hopefully next URL is successful
                e.printStackTrace();
            }
            
            if ( response.keySet().contains("code") )
            {
            	return response.get("code");
            }
            
            // If response contains error=access_denied return with null
            // This occurs if the user selected No to consent
            if ( response.keySet().contains("error") )
            {
            	return "0";
            }
           
        }
        //If we got here then a code was not returned
        return "0";
	}
	
	public static void closeBrowser() {
		theWebDriver.close();
	}

}
