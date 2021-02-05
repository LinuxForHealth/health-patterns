# Alvearie Health Patterns Core Services

Alvearie Core Services are used in the Alvearie Health Patterns to provide functionality via Java APIs to some of the various
services used within Alvearie. Currently the Core Services include the following APIs:

- DeIdentifier: A Java API to integrate FHIR resource de-identification and FHIR server persisting.
- TerminologyService: A Java API to translate FHIR resources using the FHIR Terminology Service.

The Core Services can be used independently, but they are mainly used by the Alvearie NiFi Custom Processors.

## Build

### Pre-Requisites

- [Maven](https://maven.apache.org/install.html) >= 3.6.3 
- Java 8: Any compliant JVM should work.
    - [Java 8 JDK from Oracle](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
    - [Java 8 JDK from IBM (AIX, Linux, z/OS, IBM i)](http://www.ibm.com/developerworks/java/jdk/),
    or [Download a Liberty server package](https://developer.ibm.com/assets/wasdev/#filter/assetTypeFilters=PRODUCT)
    that contains the IBM JDK (Windows, Linux)

### Building

Check out the source and run maven:

1. `git clone https://github.com/Alvearie/health-patterns.git`
1. `cd clinical-ingestion/services`
1. `maven install`

This will build the JAR and add it to your Maven repository.
