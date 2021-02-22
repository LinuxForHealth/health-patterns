# Clinical Ingestion Flow
Clinical Ingestion Flow is a reference implementation of a clinical data ingestion process.  It allows medical data to be processed by various components, enriched, normalized, transformed, and eventually stored in a specified [FHIR](https://www.hl7.org/fhir/) server.

The Clinical Ingestion Flow is designed to read medical data from a configured [kafka](https://kafka.apache.org/) topic  or directly via REST API.  As the data is processed, any errors that are detected are logged and posted to target kafka topics (if configured).

The current flow is designed to operate on FHIR resources. If [HL7](https://www.hl7.org/implement/standards/product_section.cfm?section=13) data is passed in, the pipeline is capable of converting it to FHIR and allowing it run through the pipeline.  Other data types (such as [DICOM](https://www.dicomstandard.org/) image data) are being considered but are currently supported.

In order for this flow to operate correctly, it is assumed that the following dependencies are already deployed and available, with required URL, port, authentication, etc:

- NiFi Registry 
- NiFi - Configured to access the NiFi Registry
- FHIR server
- Kafka - This is optional, but is necessary for the preferred entry point and proper logging of errors

If you already have the services mentioned above, to deploy the Clinical Ingestion Flow, follow the instructions found on the [NiFi Components](../nifi-components/README.md) readme.

You may also use the provided [Alvearie Clinical Ingestion pattern Helm Chart](helm-charts) to install the necessary dependencies, and then run the ingestion use case in the next section.

## Configuring NiFi for the Clinical Ingestion Flow

The Clinical Ingestion Flow consists of multiple [Parameter Contexts](https://nifi.apache.org/docs/nifi-docs/html/user-guide.html#parameter-contexts), used to advise the various processor groups on where target environments can be accessed.  These parameters are important in order for the flow to operate correctly.  All parameters should be filled out, according to the help text provided for each.

In addition, certain components in the Clinical Ingestion Flow require specific controller services to be enabled in order for the flow to operate successfully.  Specifically:

- Clinical Ingestion Flow -> Enrich Patient -> Resolve Terminology -> FHIR Terminology Mapping -> Translate Codes -> Get Matching ConceptMap --> This relies on a SimpleKeyValueLookupService
- Clinical Ingestion Flow -> Enrich Patient -> Resolve Terminology -> FHIR Terminology Mapping -> Translate Codes -> Wait For All Extension Processing --> This relies on a DistributedMapCacheClientService and a DistributedMapCacheServer.

These dependencies can be enabled by clicking on "Configure" for the parent processor group, selecting "Controller Services" and then enabling each necessary service.  Continue to follow this process for any other processors that have warnings listing disabled services.

## Configuring the Clinical Ingestion Flow using a helper script [OPTIONAL]

To assist with the configuration, a Python script (utilities/setupClinicalIngestionFlow.py) has been provided that will automate the steps necessary to use the Clinical Ingestion Flow.  The script will

1. Load the Clinical Ingestion Flow processor group onto the Nifi canvas
1. Set the missing passwords in the parameter contexts described above
1. Enable the controller services described above

Prerequisites
  - Python 3 installed
  - The `requests` module must be installed (`pip install requests`)
  - Change the permissions on the script to add executable (`chmod +x setupClinicalIngestionFlow.py`)
  
In order to execute the script, two arguments must be provided.  
  1. The base URL for the Nifi instance including the port.
  1. The default password to be used.  The script assumes that all passwords will be set to the same default.
  
For example, from the `utilities` directory, run

`./setupClinicalIngestionFlow <<Nifi Server:Nifi Port>> <<default password>>`

If your Nifi server was running on `http://nifi.xyz.org:8080` and you want the default password to be `twinkle`, then it would be

`./setupClinicalIngestionFlow http://nifi.xyz.org:8080  twinkle`

Status messages will log the activity of the script and you will see a completion message at the end.  At that point, you may need to refresh your Nifi canvas to see the new process group.

## Running a FHIR bundle through the Clinical Ingestion Flow

There are two ways to easily run a FHIR bundle through Clinical Ingestion Flow once it is deployed to NiFi.

1. Post the FHIR bundle json to the defined port.  By default, it is set to 7001, but can be updated in the Nifi Parameter Context named "Clinical Ingestion FHIR Parameter Context" by changing the parameter FHIR_LISTEN_PORT.

	`curl -X POST --header "ResolveTerminology: true" --header "Content-Type: application/json" -d @<<path/to/json>> "<<NIFI_SERVER>>:<<FHIR_LISTEN_PORT>>/fhirResource" --verbose`
	
	* "ResolveTerminology: true" tells the pipeline to run the bundle through the terminology normalization process. If you do not wish to run this step, you can omit this header.
	* "path/to/json" can refer to any FHIR bundle you wish to process. For example, "patientData/patient-with-us-core-birthsex.json"
	* NIFI_SERVER and FHIR_LISTEN_PORT should be known values from the setup above.
	* The result of this command should be an HTTP 200 response indicating that it was successfully submitted.
	* It is also possible to use a special HTTP header *RequestId* with a user generated ID. When providing this, that header will be persisted throughout the Ingestion pipeline as a flow file attribute, in order to match any user request to its corresponding flow file. Sample usage:
	    * `curl -X POST --header "RequestId: request-0001" -d @<<path/to/json>> "<<NIFI_SERVER>>:<<FHIR_LISTEN_PORT>>/fhirResource" --verbose`

2. Submit the FHIR bundle to the kafka topic configured above ("kafka.topic.in" parameter in "Clinical Ingestion Kafka Parameter Context")
	* Using the configured kafka broker ("kafka.brokers" parameter in "Clinical Ingestion Kafka Parameter Context"), post the FHIR bundle of your choice and the Clinical Ingestion Flow will automatically react and begin processing.
	* Posting data to kafka is a well-documented process, but there are no single line examples on how to post an entire file.  If you need help posting to a kafka topic, please start here: https://kafka.apache.org/quickstart#quickstart_send

Once submitted, you will see the bundle traverse the NiFi flow, resulting in many successful flowfiles accumulating at the end of the flow.
	* Any errors that occur during the processing will automatically get posted to a topic that matches your input topic, but ends in ".error".
