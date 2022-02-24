# Enrichment Test Repository

## Overview
This is a Maven project that uses [Zerocode](https://github.com/authorjapps/zerocode) to define the tests and Java Junits to execute the tests.  The tests are organized and executed by Junit categories.  The tests use a properties file, [enrich-flow.properties](https://github.com/LinuxForHealth/health-patterns/blob/main/enrich/src/test/resources/enrich-flow.properties), that defines the URLs for each of the enrich services used in the tests.

## Repository Organization
- [Zercode Test Scenarios](https://github.com/LinuxForHealth/health-patterns/tree/main/enrich/src/test/resources/scenarios)
- [Junit Tests](https://github.com/LinuxForHealth/health-patterns/tree/main/enrich/src/test/java/tests)
- [Junit Test Categories](https://github.com/LinuxForHealth/health-patterns/tree/main/enrich/src/test/java/categories)


## Test Build

Execute the following maven command in the enrich folder:

```
mvn clean install  --log-file ./mvnBuild.log /
-Dip.fhir=<Primary FHIR Server URL> /
-Dip.fhir.deid=<DEID FHIR Server URL> /
-Dip.deid.prep=<DEID Prep Service URL> /
-Dip.term.prep=<TERM Prep Service URL> /
-Dip.ascvd.from.fhir=<ASCVD From FHIR Service URL> /
-Dip.nlp.insights=<NLP-Insights Service URL> /
-Dpw=<Default Password for FHIR Server User fhiruser> /
-Dloglevel=<TRACE, DEBUG, INFO, WARN or ERROR>

```
This will populate the properties file with the correct URLs and other values and build the test cases.  The properies required to run tests will vary on the services deployed.

## Test Execution by Test Category

```
mvn -DskipTests=false -Dtest=<test category name> test
```