# Health Patterns Helm Chart

The Health Patterns Helm Chart encompasses many services which are frequently used together to achieve health care goals.  This pattern can be configured via Helm values to operate differently based on your use case and needs. Currently, two different uses are supported: Clinical Ingestion and Clinical Enrichment. 

# Clinical Ingestion
Clinical Ingestion is a reference implementation of a clinical data ingestion process.  It allows medical data to be processed by various components, enriched, normalized, transformed, and eventually stored in a specified [FHIR](https://www.hl7.org/fhir/) server.

The Clinical Ingestion flow is designed to read medical data from a configured [kafka](https://kafka.apache.org/) topic.  As the data is processed, any errors that are detected are logged and posted to target kafka topics.

The current flow is designed to operate on FHIR resources. If [HL7](https://www.hl7.org/implement/standards/product_section.cfm?section=13) data is passed in, the pipeline is capable of converting it to FHIR and allowing it run through the pipeline.  Other data types (such as [DICOM](https://www.dicomstandard.org/) image data) are being considered but are currently supported.

The Clinical Ingestion flow can also enrich the data as it flows through. This relies on the Clinical Enrichment flow described below.

# Clinical Enrichment
Clinical Enrichment is a reference implementation of a clinical data enrichment process.  It allows medical data to be enriched using various components, such as de-identification, terminology normalization, and the [ASCVD](https://github.com/Alvearie/health-analytics/tree/main/ascvd) analytic evaluation.

The Clinical Enrichment Flow is designed to read medical data (in FHIR format) from a configured [kafka](https://kafka.apache.org/) topic.  As the data is processed, any errors that are detected are logged and posted to target kafka topics (if configured).  Once complete, the updated FHIR data is posted back to a Kafka topic for further use.

The current flow is designed to operate on FHIR resources. If [HL7](https://www.hl7.org/implement/standards/product_section.cfm?section=13) data is passed in, the pipeline is capable of converting it to FHIR and allowing it run through the pipeline.  Other data types (such as [DICOM](https://www.dicomstandard.org/) image data) are being considered but are currently supported.

Currently we support the following enrichment steps:

* FHIR Terminology Service - This step will update the clinical data by adding/updating values to adhere to the terminology service configuration. The configuration mapping rules are currently static and can be found:

>health-patterns/services/terminology-service-core/src/main/resources/mappings

* [De-Identification](https://github.com/Alvearie/de-identification) Service - This step will de-identify the clinical data flowing through the pipeline and store the de-identified version in a separate FHIR server.  The de-identification rules are currently static and can be found [here](../../services/deid-core/src/main/resources/de-id-config.json).

* [Million Hearts ASCVD Model](https://github.com/Alvearie/health-analytics/tree/main/ascvd): This step will calculate a ten-year risk of cardiovascular disease using the Million Hearts ASCVD Model.

## Deploying the Health Patterns Helm chart

The Health Patterns Helm chart relies on a number of underlying services to operate.  These can all be deployed and configured automatically using instructions provided [here](README_Helm.md).  However, if you wish to deploy and configure your own, follow the instructions [here](README_MANUAL_DEPLOY.md).

## Submitting data to a Health Patterns flow

To submit data to the Clinical Ingestion or Clinical Enrichment pipelines, it needs to be posted to the configured Kafka topic. The Kafka topic to target depends on which pipeline you are running:

* Clinical Ingestion  - "ingest.clinical.in"  (This can be found/updated in the Nifi parameter context "cms_adapter_parameters" under the parameter "kafka.topic.in")
* Clinical Enrichment - "patients.updated.out"  (This can be found/updated in the Nifi parameter context "cms_adapter_parameters" under the parameter "enrich.in")

For convenience, an HTTP endpoint will be deployed to allow easy access to the Kafka broker used by the pipelines. To use, call:

`curl -X POST --header "RequestId: request-0001" --header "ResolveTerminology: true" --header "DeidentifyData: true" --header "Content-Type: application/json" -d @<<path/to/json>> "<<Expose Kafka URL>>?topic=<<Topic>>" --verbose`


Alternatively, you can directly post to Kafka if your environment allows. Posting data to kafka is a well-documented process, but there are no single line examples on how to post an entire file.  If you need help posting to a kafka topic, please start here: https://kafka.apache.org/quickstart#quickstart_send

An explanation of the parameters:

* "path/to/json" - (Required) Clinical data you wish to process (for example, "patientData/patient-with-us-core-birthsex.json"). Currently only FHIR and HL7 data are supported by this flow. 
* "Expose Kafka URL" - (Required) The URL for the Expose Kafka service.  By default, this is an ingress URL that you can find listed in your kubernetes ingresses under "ingestion-expose-kafka".  It is also listed in the notes shown at the end of the helm install process.
* "RequestId: request-0001" - (Optional) A user-generated ID. When used, the provided value will be persisted throughout the ingestion pipeline as a flowfile attribute for better tracking of the request.
* "ResolveTerminology: true" - (Optional) Run the bundle through the terminology normalization process.
* "DeidentifyData: true" - (Optional) Run the de-identify logic. This will store the de-identified data to a separate FHIR server and allow the original data to continue through the flow.
* "RunASCVD: true" - (Optional) Run the FHIR bundle through the ASCVD service. This will calculate a ten-year risk of cardiovascular disease and store the result as an attribute in the flow file.  Use of the attribute is left up to the user of the Clinical Ingestion pipeline to determine.

NOTE: The default values for the enrichment parameters (ResolveTerminology, DeidentifyData, and RunASCVD) can also be set in the Enrichment Parameter Context.  These are configured during deployment, but can be updated at any time you wish to modify the default behavior.  Any values provided in the request header will always be respected first, but when no header value is provided, the defaults will be used.  

The result of this command should be an HTTP 200 response indicating that it was successfully submitted.

Once submitted, you can watch the Nifi flow process the request, resulting in many successful flowfiles accumulating at the end of the flow.
	* Any errors that occur during the processing will automatically get posted to a topic that matches your input topic, but ends in ".error".