# nifi-hl7tofhir-processor custom processor

This custom nifi processor can be used to convert an incoming HL7 message to a FHIR message.

## To build this artifact

### Prerequisites

The following must be installed on your system:

- maven >= 3.6.3 
- java >= 8

### Steps

1. Navigate to the the nifi-hl7tofhir-processor-bundle directory.
1. Perform the build with `mvn clean install`
1. Navigate to the nifi-hl7tofhir-nar/target directory. The .nar file should be present.  
1. Copy the .nar file to your nifi implementation, either into the library folder or into the extensions folder.
