# Clinical Ingestion Flow
Clinical Ingestion Flow is a reference implementation of a clinical data ingestion process.  It allows medical data to be processed by various components, enriched, normalized, transformed, and eventually stored in a specified [FHIR](https://www.hl7.org/fhir/) server.

The Clinical Ingestion Flow is designed to read medical data from a configured [kafka](https://kafka.apache.org/) topic  or directly via REST API.  As the data is processed, any errors that are detected are logged and posted to target kafka topics (if configured).

Currently, the only supported medical data format is FHIR bundles. Other formats are on our backlog and will be coming soon, including [HL7](https://www.hl7.org/implement/standards/product_section.cfm?section=13) and [DICOM](https://www.dicomstandard.org/) image data.

In order for this flow to operate correctly, it is assumed that the following dependencies are already deployed and available, with required URL, port, authentication, etc:

- NiFi Registry 
- NiFi - Configured to access the NiFi Registry
- FHIR server
- Kafka - This is optional, but is necessary for the preferred entry point and proper logging of errors

To deploy the Clinical Ingestion Flow, follow the instructions found on the [NiFi Components](../nifi-components/README.md) readme.

The Clinical Ingestion Flow consists of multiple [Parameter Contexts](https://nifi.apache.org/docs/nifi-docs/html/user-guide.html#parameter-contexts), used to advise the various processor groups on where target environments can be accessed.  These parameters are important in order for the flow to operate correctly.  All parameters should be filled out, according to the help text provided for each.

In addition, certain components in the Clinical Ingestion Flow require specific controller services to be enabled in order for the flow to operate successfully.  Specifically:

- Clinical Ingestion Flow -> Enrich Patient -> Resolve Terminology -> FHIR Terminology Mapping -> Translate Codes -> Get Matching ConceptMap --> This relies on a SimpleKeyValueLookupService
- Clinical Ingestion Flow -> Enrich Patient -> Resolve Terminology -> FHIR Terminology Mapping -> Translate Codes -> Wait For All Extension Processing --> This relies on a DistributedMapCacheClientService and a DistributedMapCacheServer.

These dependencies can be enabled by clicking on "Configure" for the parent processor group, selecting "Controller Services" and then enabling each necessary service.  Continue to follow this process for any other processors that have warnings listing disabled services.


# Running a FHIR bundle through the Clinical Ingestion Flow

There are two ways to easily run a FHIR bundle through Clinical Ingestion Flow once it is deployed to NiFi.

1. Post the FHIR bundle json to the defined port (FHIR_LISTEN_PORT in "Clinical Ingestion Flow FHIR Parameter Context")

	`curl -X POST --header "ResolveTerminology: true" --header "Content-Type: application/json" -d @<<path/to/json>> "<<NIFI_SERVER>>:<<FHIR_LISTEN_PORT>>/fhirResource" --verbose`
	
	* "ResolveTerminology: true" tells the pipeline to run the bundle through the terminology normalization process. If you do not wish to run this step, you can omit this header.
	* "path/to/json" can refer to any FHIR bundle you wish to process. For example, "patientData/fhir_bundle_birthsex.json"
	* NIFI_SERVER and FHIR_LISTEN_PORT should be known values from the setup above.
	* The result of this command should be an HTTP 200 response indicating that it was successfully submitted.

2. Submit the FHIR bundle to the kafka topic configured above ("kafka.topic.in" parameter in "Clinical Ingestion Flow Kafka Parameter Context")
	* Using the configured kafka broker ("kafka.brokers" parameter in "Clinical Ingestion Flow Kafka Parameter Context"), post the FHIR bundle of your choice and the Clinical Ingestion Flow will automatically react and begin processing.
	* Posting data to kafka is a well-documented process, but there are no single line examples on how to post an entire file.  If you need help posting to a kafka topic, please start here: https://kafka.apache.org/quickstart#quickstart_send

Once submitted, you will see the bundle traverse the NiFi flow, resulting in many successful flowfiles accumulating at the end of the flow.
	* Any errors that occur during the processing will automatically get posted to a topic that matches your input topic, but ends in ".error".