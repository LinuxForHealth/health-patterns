*NOTE: This is not the recommended approach for deploying the Clinical Ingestion flow. Use the [Helm chart](helm-charts/alvearie-ingestion/README.md) unless you are sure you need manual control over the deployment process.*

# Manual Deploy and Configuration of the Clinical Ingestion Flow

If you prefer to manually provide the underlying services used by the Clinical Ingestion Flow, you will need to provision the following:

- NiFi Registry 
- NiFi - Configured to access the NiFi Registry
- FHIR server
- Kafka - This is optional, but is necessary for the preferred entry point and proper logging of errors


## Deploying the Clinical Ingestion Flow to a Nifi Canvas

In order to add the Clinical Ingestion Flow to your Nifi canvas, you can either rely on a configured Nifi Registry pointing at the [Health Patterns Nifi Flow](https://github.com/Alvearie/health-patterns-nifi-flows) Github repo, or you can import the flow from there manually:

To deploy a NiFi flow into a running [NiFi Registry](https://nifi.apache.org/registry.html), follow these steps:

1. Download and install the [NiFi CLI Toolkit](https://nifi.apache.org/download.html)
1. Execute "cli" from the bin folder in the Toolkit
1. Identify the base URL for your NiFi registry (i.e. http://localhost:8080/nifi-registry)
1. Create a bucket for your target NiFi Registry to store the component (This will return the bucket identifier used in the next step):

	`registry create-bucket --baseUrl=<<BASE_URL>> --bucketName="Health Patterns"`
	
1. Create a bucket entry for component flow (This will return the flow identifier used in the next step):
	
	`registry create-flow --baseUrl=<<BASE_URL>> --bucketIdentifier <<BUCKET_IDENTIFIER>> --flowName <<FLOW_NAME>>`
	
1. Import current version of component using flow json:

	`registry import-flow-version --baseUrl=<<BASE_URL>> --flowIdentifier=<<FLOW_ID>> -i <<PATH_TO_FLOW_JSON>>`
	
1. Once the flow file is imported into the NiFi Registry, it can be added to a NiFi canvas and initialized according to normal NiFi instructions.


## Configuring NiFi for the Clinical Ingestion Flow

The Clinical Ingestion Flow consists of multiple [Parameter Contexts](https://nifi.apache.org/docs/nifi-docs/html/user-guide.html#parameter-contexts), used to advise the various processor groups on where target environments can be accessed.  These parameters are important in order for the flow to operate correctly.  All parameters should be filled out, according to the help text provided for each.

In addition, certain components in the Clinical Ingestion Flow require specific controller services to be enabled in order for the flow to operate successfully.  In order to enable them, open the configuration options for the Clinical Ingestion processor group, and click on the Controller Services tab.  Enable each listed service.