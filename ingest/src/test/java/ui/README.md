# patient-browser UI Tests

## Overview
These are Selenium-based tests to test the patient-browser that is deployed with health-patterns ingestion.  These are java junit tests that are part of the Maven build of the ingest tests.   The tests are setup to use only Chrome browser.

## Repository Organization
- [Java Tests](https://github.com/LinuxForHealth/health-patterns/tree/main/ingest/src/test/java/ui/tests)
- [Selenium Java Page Objects](https://github.com/LinuxForHealth/health-patterns/tree/main/ingest/src/test/java/ui/pageobjects)

## Requirements
The Selenium version used (set in [pom.xml](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/pom.xml)) is sensitive to the Chromedriver version and the Chrome browser version.   When running tests on your local workstation, be aware of any automatic updates of the Chrome browser.   If the Chrome browser gets updated to a version not compatible with the Chromedriver, the Chromedriver used by Selenium will need to be updated.   

### Selenium
Selenium 4.1.4 is currently being used for these UI tests.  This Selenium version is compatible with the Chrome versions listed below.

### Chrome & Chromedriver
- Chrome browser Version 101.0.4951.54
- Chromedriver compatible with Chrome Version 101.0.4951.54.  [Chromedriver downloads](https://chromedriver.chromium.org/downloads) 

### Running Tests Headless
In the ingest test properties file, [clinical-ingestion-flow.properties](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/src/test/resources/clinical-ingestion-flow.properties), property 'patient-browser-headless' is used for displaying/not displaying the web browser while the tests run.
- When false: the test activity can be observed in a Chrome web browser. 
- When true:  the tests run without the web browser being displayed.   Use this value when running in toolchains.