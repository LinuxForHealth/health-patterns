# Building the Mimic2FHIR dependency

Mimic2FHIR is required for the NAR process to build correctly.  Specifically the Alvearie fork of this project.  To accomplish this:

1. git clone https://github.com/alvearie/mimic2fhir.git
1. cd mimic2fhir
1. mvn clean install

This will build the JAR and add it to your maven repository. This will allow the Health Patterns Processors project to build successfully.