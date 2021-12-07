# FHIR Data Quality

A deployable service to check the data quality of provided FHIR bundle data.


## Build

### Pre-Requisites

- [Scala Build Tool (SBT)](https://www.scala-sbt.org/index.html)
- Java 8: Any compliant JVM should work.
    - [Java 8 JDK from Oracle](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
    - [Java 8 JDK from IBM (AIX, Linux, z/OS, IBM i)](http://www.ibm.com/developerworks/java/jdk/),
    or [Download a Liberty server package](https://developer.ibm.com/assets/wasdev/#filter/assetTypeFilters=PRODUCT)
    that contains the IBM JDK (Windows, Linux)

### Building

Check out the source and run:

`sbt assembly`


## Operations

- process a FHIR bundle and return the results of the data checks

    (POST)  https://\<FHIR-Data-Quality>:<port>

- general health of service-a simple sanity check on the service

    (GET)  https://\<FHIR-Data-Quality>:<port>/healthcheck