# health-patterns Dev Ops Toolchain

Test scripts that are executed during toolchain execution:    
- **run-smoketests.sh** - simplest ingestion/enrichment deployment in namespace $CLUSTER_NAMESPACE"-smoke".  
- **run-fvttests.sh** - ingestion/enrichment deployment with more features configured in namespace $CLUSTER_NAMESPACE"-fvt".
- **run-ivttests.sh** - ingestion/enrichment deployment with all features configured in namespace $CLUSTER_NAMESPACE"-ivt".
- **toolchain-envsetup.sh** - Common setup steps executed in each of the "run-" scripts.
- **testCleanUp.sh** - Common common test cleanup steps used in each of the "run-" scripts.
- **NifiKopValues.sh** - Configure and deploy NifiKop for a scured Nifi canvass.  Executed in run-fvttests.sh & run-ivttests.sh.



#### Toolchain Environment Variables

- **ACD_APIKEY** - API Key for the ACD Service used in the pipeline for data enrichment. 
- **GIT_BRANCH** - LinuxForHealth health-patterns repo branch for git clone operation.  This is 'main' by default and can be changed to a branch to test code/function before delivery to the main branch. 
- **CLUSTER_NAMESPACE** - base name to use when build the TEST_NAMESPACE name.  The default for ingestion is 'tst-ingest', and the default for enrichment is 'tst-enrich'.  
- **COS_ACCESSKEY** - Used for accessing Cloud Object Storage (only used for the CQL Bulk Export Testing). 
- **COS_APIKEY** - Used for accessing Cloud Object Storage (only used for the CQL Bulk Export Testing). 
- **COS_SECRETKEY** - Used for accessing Cloud Oject Storage (only for the CQL Bulk Export Testing). 
- **DEPLOY_NIFIKOP** - true/false switch  to determine if Nifikop is to be deployed.  The default is false.
- **DEPLOY_WAIT** - the time in seconds to wait for the deployment to be operational after the helm install completes.  The default for ingestion deployments is '360' seconds, and the default for enrichment deployments is '240' seconds.
- **HELM_TIMEOUT** - the timeout time for the HELM command when using the --wait --timeout MmSs options (where M=minutes and S=seconds).  The default for all helm deployments is '8m0s'. 
- **HELM_RELEASE** - 'ingestion' or 'enrich' Determines the type of health-patterns deployment to be done.
- **ENV_CLEAN_UP** - flag to indicate to clean up the test environment at the end.  The default value is 'true'. 
- **INGRESS_SUBDOMAIN** - ingress subdomain for the deployment. The default value for the health-patterns-1 cluster is 'wh-health-patterns.dev.watson-health.ibm.com'.
- **LOGLEVEL** - Console log level (TRACE, DEBUG, INFO, WARN or ERROR)   The default is ERROR.
- **RUN_FVT** - true/false switch to determine to run the FVT tests.  Default is true.
- **RUN_IVT** - true/false switch to determine to run the IVT tests.  Default is true.
- **RUN_SMOKE** - true/false switch to determine to run the Smoke tests.  Default is true.



#### Current Dev Ops Toolchain Links:

- [ingestion](https://cloud.ibm.com/devops/toolchains/2e515e70-2d32-4815-ae60-e7128aa0b016?env_id=ibm:yp:us-east)
- [enrichment](https://cloud.ibm.com/devops/toolchains/370a80ea-6b9e-40cf-8f5b-3360b49689ad?env_id=ibm:yp:us-east)