# nifi-health-patterns-bundle

This bundle contains all custom processors created by/for the health-patterns project.  Currently, this includes:

- **ACDProcessor** - This processor feeds the current flow file to the Annotator for Clinical Data (ACD) to add NLP annotations to the current FHIR resource.
- **HL7ToFhirProcessor** - This processor converts an HL7-formatted flow file to FHIR
- **[GenerateFHIRFromMimic](./docs/GenerateFHIRFromMimic.md)** - This processor reads all patients from a source Mimic database and produces one FHIR bundle per patient representing all known data for that patient.
- **DeIdentifyAndPostToFHIR** - This processor takes the a FHIR resource (a Bundle or individual resources) de-identifies it and posts the result to a FHIR server.

## To build this artifact

### Prerequisites

The following must be installed on your system:

- maven >= 3.6.3 
- java >= 8
- previously built maven artifact for [mimic2fhir](https://github.com/Alvearie/mimic2fhir).  See [here](docs/MIMIC2FHIR.md) for instructions.
- Build the Alvearie Health Pattern Core Services. Instructions [here](/services/README.md)

### Steps

1. Navigate to the the *nifi-health-patterns-processor-bundle* directory.
1. Perform the build with `mvn clean install`
1. Navigate to the nifi-health-patterns-nar/target directory. The .nar file should be present.  
1. Copy the .nar file to your nifi implementation, either into the library folder or into the extensions folder.