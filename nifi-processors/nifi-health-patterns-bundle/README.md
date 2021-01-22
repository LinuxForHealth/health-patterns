# nifi-health-patterns-bundle

This bundle contains all custom processors created by/for the health-patterns project.  Currently, this includes:

- **ACDProcessor** - This processor feeds the current flow file to the Annotator for Clinical Data (ACD) to add NLP annotations to the current FHIR resource.
- **HL7ToFhirProcessor** - This processor converts an HL7-formatted flow file to FHIR
- **[GenerateFHIRFromMimic](GenerateFHIRFromMimic_README.md)** - This processor reads all patients from a source Mimic database and produces one FHIR bundle per patient representing all known data for that patient.

## To build this artifact

### Prerequisites

The following must be installed on your system:

- maven >= 3.6.3 
- java >= 8
- previously built maven artifact for [mimic2fhir](https://github.com/Alvearie/mimic2fhir).  See [here](MIMIC2FHIR_README.md) for instructions.

### Steps

1. Navigate to the the nifi-health-patterns-processor-bundle directory.
1. Perform the build with `mvn clean install`
1. Navigate to the nifi-health-patterns-nar/target directory. The .nar file should be present.  
1. Copy the .nar file to your nifi implementation, either into the library folder or into the extensions folder.