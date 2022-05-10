# Ingestion Test Repository

## Overview
This is a Maven project that uses [Zerocode](https://github.com/authorjapps/zerocode) to define the tests and Java Junits to execute the tests.  The tests are organized and executed by Junit categories.  The tests use a properties file, [clinical-ingestion-flow.properties](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/src/test/resources/clinical-ingestion-flow.properties), that defines the URLs for each of the deployed ingestion services used in the tests.

## Repository Organization
- [Zercode Test Scenarios](https://github.com/LinuxForHealth/health-patterns/tree/main/ingest/src/test/resources/scenarios)
- [Junit Tests](https://github.com/LinuxForHealth/health-patterns/tree/main/ingest/src/test/java/tests)
- [Junit Test Categories](https://github.com/LinuxForHealth/health-patterns/tree/main/ingest/src/test/java/categories)
- [Junit UI Tests for patient-browser](https://github.com/LinuxForHealth/health-patterns/tree/main/ingest/src/test/java/ui/tests)
- [Selenium page object classes for the patient-browser UI tests](https://github.com/LinuxForHealth/health-patterns/tree/main/ingest/src/test/java/ui/pageobjects)


## Test Build
Execute the following maven command in the ingest folder:

```
mvn clean install --log-file ./mvnBuild.log /
-Dip.fhir=<Primary FHIR Server URL> /
-Dip.fhir.proxy=<Primary FHIR Proxy Server URL> /
-Dip.fhir.deid=<DEID FHIR Server URL> /
-Dip.fhir.deid.proxy=<DEID FHIR Proxy Server URL> /
-Dip.deid=<DEID Server URL> /
-Dip.nifi=<Base URL of the Nifi Server> /
-Dip.expkafka=<expose-kafka Service URL> /
-Dip.nlp.insights=<nlp-insights Server URL> /
-Dip.cohort=<cohort-service URL> / 
-Dip.cql.bulk.export=<cql-bulk-eport service URL>  /
-Dkafka.topic.in=<Input Topic for the expose-kafka Service> /
-Dip.patient.browser=<patient-browser URL> /
-Dpw=<Default Password for the FHIR Server fhiruser> /
-Dloglevel=<TRACE, DEBUG, INFO, WARN or ERROR>

```

This will populate the properties file with the correct URLs and other values and build the test cases.  The properties required to run tests will vary on the services deployed.

## Test Execution by Test Category
```
mvn -DskipTests=false -Dtest=<test category name> test
```

