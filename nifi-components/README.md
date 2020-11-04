# NiFi Components

NiFi components contains deployable components that can be used in NiFi (https://nifi.apache.org/) flows.  These components may be contained in other artifacts in health-patterns, but are included here as building blocks for future use cases.


# To Deploy a NiFi component to a known NiFi Registry
To deploy a NiFi component into a running NiFi Registry (https://nifi.apache.org/registry.html), follow these steps:

- Download and install the NiFi CLI Toolkit (https://nifi.apache.org/download.html)
- Execute "cli" from the bin folder in the Toolkit
- Create a bucket your target NiFi Registry to store the component:
	- Run "registry create-bucket --baseUrl=<<BASE_URL>> --bucketName=<<BUCKET_NAME>>"
	- This will return the bucket identifier used in the next step.
- Create a bucket entry for component flow:
	- Run "registry create-flow --baseUrl=<<BASE_URL>> --bucketIdentifier <<BUCKET_IDENTIFIER>> --flowName <<FLOW_NAME>>
	- This will return the flow identifier used in the next step.
- Import current version of component using flow json:
	- Run "registry import-flow-version --baseUrl=<<BASE_URL>> --flowIdentifier=<<FLOW_ID>> -i <<PATH_TO_FLOW_JSON>>
- Once the flow file is imported into the NiFi Registry, it can be added to a NiFi canvas and initialized according to normal NiFi instructions.