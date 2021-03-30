# Clinical Ingestion Flow
Clinical Ingestion Flow is a reference implementation of a clinical data ingestion process.  It allows medical data to be processed by various components, enriched, normalized, transformed, and eventually stored in a specified [FHIR](https://www.hl7.org/fhir/) server.

The Clinical Ingestion Flow is designed to read medical data from a configured [kafka](https://kafka.apache.org/) topic  or directly via REST API.  As the data is processed, any errors that are detected are logged and posted to target kafka topics (if configured).

The current flow is designed to operate on FHIR resources. If [HL7](https://www.hl7.org/implement/standards/product_section.cfm?section=13) data is passed in, the pipeline is capable of converting it to FHIR and allowing it run through the pipeline.  Other data types (such as [DICOM](https://www.dicomstandard.org/) image data) are being considered but are currently supported.

## Deploying the Clinical Ingestion Flow

The Clinical Ingestion flow requires a number of underlying service to operate.  These can all be deployed and configured automatically using instructions provided [here](helm-charts/alvearie-ingestion/README.md).  However, if you wish to deploy and configure your own, follow the instructions [here](README_MANUAL_DEPLOY.md).

## Running a FHIR bundle through the Clinical Ingestion Flow

There are two ways to easily send clinical data through the Clinical Ingestion Flow once it is deployed to NiFi.

1. Post the data (FHIR or HL7) to the Nifi HTTP Post URL:

	`curl -X POST --header "RequestId: request-0001" --header "ResolveTerminology: true" --header "DeidentifyData: true" --header "Content-Type: application/json" -d @<<path/to/json>> "<<Nifi Server URL>>/fhirResource" --verbose`

An explanation of the parameters:

* "RequestId: request-0001" - This is an *optional* parameter that can be used to specify a user-generated ID. When used, the provided value will be persisted throughout the ingestion pipeline as a flowfile attribute for better tracking of the request.
* "ResolveTerminology: true" - This is an *optional* parameter that tells the pipeline to run the bundle through the terminology normalization process.
* "DeidentifyData: true" - This is an *optional* parameter that tells the pipeline to run the de-identify logic. This will store the de-identified data to a separate FHIR server and allow the original data to continue through the flow.
* "path/to/json" - This is a *required* parameter that refers to any clinical data you wish to process (for example, "patientData/patient-with-us-core-birthsex.json"). Currently only FHIR and HL7 data are supported by this flow. 
* "Nifi Server URL" - This is a *required* parameter that represents the Nifi HTTP Post entry point.  By default, this is an ingress URL that you can find listed in your kubernetes ingresses under "ingestion-nifi-http-post-ingress".  It is also listed in the notes shown at the end of the helm install process. If you choose to deploy via load balancer, this address needs to include the URL and port (usually 7001) for the ingestion-nifi service.

The result of this command should be an HTTP 200 response indicating that it was successfully submitted.



2. Submit the FHIR bundle to the kafka topic configured above ("kafka.topic.in" parameter in "Clinical Ingestion Kafka Parameter Context")
	* Using the configured kafka broker ("kafka.brokers" parameter in "Clinical Ingestion Kafka Parameter Context"), post the FHIR bundle of your choice and the Clinical Ingestion Flow will automatically react and begin processing.
	* Posting data to kafka is a well-documented process, but there are no single line examples on how to post an entire file.  If you need help posting to a kafka topic, please start here: https://kafka.apache.org/quickstart#quickstart_send

Once submitted, you will see the bundle traverse the NiFi flow, resulting in many successful flowfiles accumulating at the end of the flow.
	* Any errors that occur during the processing will automatically get posted to a topic that matches your input topic, but ends in ".error".
