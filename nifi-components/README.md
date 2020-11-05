# NiFi Components

NiFi components contains deployable components that can be used in NiFi (https://nifi.apache.org/) flows.  These components may be contained in other artifacts in health-patterns, but are included here as building blocks for future use cases.


# To Deploy a NiFi component to a known NiFi Registry
To deploy a NiFi component into a running NiFi Registry (https://nifi.apache.org/registry.html), follow these steps:

1. Download and install the NiFi CLI Toolkit (https://nifi.apache.org/download.html)
1. Execute "cli" from the bin folder in the Toolkit
1. Identify the base URL for your NiFi registry (i.e. http://localhost:8080/nifi-registry)
1. Create a bucket for your target NiFi Registry to store the component (This will return the bucket identifier used in the next step):

	`registry create-bucket --baseUrl=<<BASE_URL>> --bucketName="Health Patterns"`
	
1. Create a bucket entry for component flow (This will return the flow identifier used in the next step):
	
	`registry create-flow --baseUrl=<<BASE_URL>> --bucketIdentifier <<BUCKET_IDENTIFIER>> --flowName <<FLOW_NAME>>`
	
1. Import current version of component using flow json:

	`registry import-flow-version --baseUrl=<<BASE_URL>> --flowIdentifier=<<FLOW_ID>> -i <<PATH_TO_FLOW_JSON>>`
	
1. Once the flow file is imported into the NiFi Registry, it can be added to a NiFi canvas and initialized according to normal NiFi instructions.