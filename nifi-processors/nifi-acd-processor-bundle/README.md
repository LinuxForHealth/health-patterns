# nifi-acd-processor custom processor

This custom nifi processor is a simple acd handler that will take a string of text and
via a call to acd, create flowfiles corresponding to any resources (medications or procedures)
that are found in the response.

## To build this artifact

### Prerequisites

The following must be installed on your system:

- maven
- java 8

### Steps

1. Navigate to the the nifi-acd-processor-bundle directory
1. Perform the build with **mvn clean install**
1. Navigate to the nifi-acd-nar/target directory. The .nar file should be present.  
1. Copy the .nar file to your nifi implementation, either into the library folder or into the extensions folder
