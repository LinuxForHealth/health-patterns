# health-patterns Dev Ops Toolchain

Test scripts that are executed during toolchain execution:    
- **run-smoketests.sh** - simplest ingestion/enrichment deployment in namespace $CLUSTER_NAMESPACE"-smoke".  
- **run-fvttests.sh** - ingestion/enrichment deployment with more features configured in namespace $CLUSTER_NAMESPACE"-fvt".
- **run-ivttests.sh** - ingestion/enrichment deployment with all features configured in namespace $CLUSTER_NAMESPACE"-ivt".
- **toolchain-envsetup.sh** - Common setup steps executed in each of the "run-" scripts.
- **NifiKopValues.sh** - Configure and deploy NifiKop for a scured Nifi canvass.  Executed in run-fvttests.sh & run-ivttests.sh.

The helm release (ingestion or enrich) is determined by the CLUSTER_NAMESPACE value: 
- When 'tst-enrich', the helm release deployed will be 'enrich'. 
- When 'tst-ingest', the helm release deployed will be 'ingestion'. 


#### Toolchain Environment Variables

- **GIT_BRANCH** - alvearie repo branch for git clone operation of the alvearie repo.  This is 'main' by default and can be changed to a branch to test code/function before delivery to the main branch. 
- **CLUSTER_NAMESPACE** - base name to use when build the TEST_NAMESPACE name.  The default for ingestion is 'tst-ingest', and the default for enrichment is 'tst-enrich'.  
- **DEPLOY_WAIT** - the time in seconds to wait for the deployment to be operational after the helm install completes.  The default for ingestion is '360' seconds, and the default for enrichment is '240' seconds.
- **HELM_TIMEOUT** - the timeout time for the HELM command when using the --wait --timeout MmSs options (where M=minutes and S=seconds).  The default for all helm deployments is '8m0s'. 
- **ENV_CLEAN_UP** - flag to indicate to clean up the test environment at the end.  The default value is 'true'. 
- **INGRESS_SUBDOMAIN** - ingress subdomain for the deployment. The default value for the health-patterns-1 cluster is 'wh-health-patterns.dev.watson-health.ibm.com'.


#### Current Dev Ops Toolchain Links:

- [ingestion](https://cloud.ibm.com/devops/toolchains/f36a168d-7d0b-4f4b-acac-6172cd9abd39?env_id=ibm:yp:us-east)
- [enrichment](https://cloud.ibm.com/devops/toolchains/405c175f-df5c-4577-8674-f01de1d72db6?env_id=ibm:yp:us-east)