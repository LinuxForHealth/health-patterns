#!/bin/bash

# Run the Avlearie enrich/ingestion Deploy install per documented instructions (selection based on CLUSER_NAMESPACE from toolchain input
#
# Run the enrich/ingestion smoke tests and add test results to smoketests.xml for the Insights Quality Dashboard
#
# Environment Variables passed in from the toolchain:
# HELM_RELEASE - deployment release name:  enrich or ingestion
# CLUSTER_NAMESPACE - base name to use when build the TEST_NAMEPSACE name
# DEPLOY_WAIT - the time in seconds to wait for the deployment to be operational after the helm install completes
# HELM_TIMEOUT - the timeout time for the HELM command when using the --wait --timeout MmSs options (where M=minutes and S=seconds)
# ENV_CLEAN_UP - flag to indicate to clean up the test environment at the end
# INGRESS_SUBDOMAIN - ingress subdomain for the deployment
# LOGLEVEL - test execution logging level (logback-test) ERROR, WARNING, or INFO
# DEPLOY_NIFIKOP - true to configure/deploy nifikop, false to skip nifikop deployment

# Setup the test environment
chmod +x ./tests/toolchain-envsetup.sh
source ./tests/toolchain-envsetup.sh "smoke"

# Setup for NifiKop Deployment if enabled
cd /workspace/$TEST_NAMESPACE/health-patterns/test-umbrella/tests
chmod +x ./tests/NifiKopValues.sh
source ./tests/NifiKopValues.sh

# Use kafka input topic used in sercure Nifi
export KAFKA_TOPIC_IN="ingest.topic.in"

echo " change to the correct deployment directory"
cd /workspace/$TEST_NAMESPACE/health-patterns/helm-charts/health-patterns

# Execute the desired deployment
echo "***************************************"
echo $TEST_NAMESPACE" : Deploy "$HELM_RELEASE"via helm3"
date
echo "***************************************"
if [ $HELM_RELEASE = "enrich" ] 
then
   # disable the ingestion deploy for an enrich-only deployment
   sed -i -e "s/\&ingestionEnabled true/\&ingestionEnabled false/g" values.yaml

   export DEPLOY_OPTIONS="--set ascvd-from-fhir.ingress.enabled=true --set deid-prep.ingress.enabled=true --set term-services-prep.ingress.enabled=true --set nlp-insights.enabled=true --set nlp-insights.ingress.enabled=true --set nlp-insights.nlpservice.quickumls.endpoint=https://quickumls.wh-health-patterns.dev.watson-health.ibm.com/match --set nlp-insights.nlpservice.acd.endpoint=https://us-east.wh-acd.cloud.ibm.com/wh-acd/api --set nlp-insights.nlpservice.acd.apikey="$ACD_APIKEY" --set nlp-insights.nlpservice.acd.flow=wh_acd.ibm_clinical_insights_v1.0_standard_flow --wait --timeout "$HELM_TIMEOUT
   
   if [ $DEPLOY_NIFIKOP != "true" ]
   then
      export DEPLOY_OPTIONS=" -f clinical_enrichment.yaml "$DEPLOY_OPTIONS
   fi

   # deploy enrich
   # helm3 install $HELM_RELEASE . --set ascvd-from-fhir.ingress.enabled=true --set deid-prep.ingress.enabled=true --set term-services-prep.ingress.enabled=true --set nlp-insights.enabled=true --set nlp-insights.ingress.enabled=true --set nlp-insights.nlpservice.quickumls.endpoint=https://quickumls.wh-health-patterns.dev.watson-health.ibm.com/match --set nlp-insights.nlpservice.acd.endpoint=https://us-east.wh-acd.cloud.ibm.com/wh-acd/api --set nlp-insights.nlpservice.acd.apikey=$ACD_APIKEY --set nlp-insights.nlpservice.acd.flow=wh_acd.ibm_clinical_insights_v1.0_standard_flow --wait --timeout $HELM_TIMEOUT
elif [ $HELM_RELEASE = "ingestion" ] 
then
   # deploy ingestion
   export DEPLOY_OPTIONS="--wait --timeout "$HELM_TIMEOUT
   
   if [ $DEPLOY_NIFIKOP != "true" ]
   then
      export DEPLOY_OPTIONS=" -f clinical_ingestion.yaml "$DEPLOY_OPTIONS
   fi
   # helm3 install $HELM_RELEASE . --wait --timeout $HELM_TIMEOUT
fi

echo "Deployment options: '"$DEPLOY_OPTIONS"'"

helm3 install $HELM_RELEASE . $DEPLOY_OPTIONS

echo "*************************************"
echo "* Waiting for "$DEPLOY_WAIT" seconds           *"
echo "*************************************"
date
sleep $DEPLOY_WAIT  
date

echo "*************************************" 
echo "* A Look At Everything              *"
echo "*************************************"
kubectl get all

if [ $HELM_RELEASE = "enrich" ]  
then 
   echo "****************************************************" 
   echo "* Goto the testcase folder in the repo             *"
   echo "****************************************************"
   cd /workspace/$TEST_NAMESPACE/health-patterns/enrich/

   echo "*************************************" 
   echo "* Build the testcases               *"
   echo "*************************************"
   mvn clean install --log-file ./mvnBuild.log -Dip.fhir=$FHIR_IP -Dip.fhir.deid=$FHIR_DEID_IP -Dip.deid.prep=$DEID_PREP_IP -Dip.term.prep=$TERM_PREP_IP -Dip.ascvd.from.fhir=$ASCVD_FROM_FHIR_IP -Dip.nlp.insights=$NLP_INSIGHTS_IP -Dpw=$DEFAULT_PASSWORD -Dloglevel=$LOGLEVEL

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn -DskipTests=false -Dtest=EnrichmentInitTests test
   mvn -DskipTests=false -Dtest=BasicEnrichmentTests test
   mvn -DskipTests=false -Dtest=EnrichmentConfigTests test
   mvn -DskipTests=false -Dtest=ASCVDEnrichmentTests test

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.EnrichmentInitTests.txt
   cat target/surefire-reports/categories.BasicEnrichmentTests.txt
   cat target/surefire-reports/categories.EnrichmentConfigTests.txt
   cat target/surefire-reports/categories.ASCVDEnrichmentTests.txt
elif [ $HELM_RELEASE = "ingestion" ] 
then
   echo "****************************************************" 
   echo "* Goto the testcase folder in the repo             *"
   echo "****************************************************"
   cd /workspace/$TEST_NAMESPACE/health-patterns/ingest/
   
   echo "*************************************" 
   echo "* Build the testcases               *"
   echo "*************************************"
   mvn clean install --log-file ./mvnBuild.log -Dip.fhir=$FHIR_IP -Dip.fhir.deid=$FHIR_DEID_IP -Dip.nifi=$NIFI_IP -Dip.nifi.api=$NIFI_API_IP -Dip.kafka=$KAFKA_IP -Dip.deid=$DEID_IP -Dip.expkafka=$EXP_KAFKA_IP -Dkafka.topic.in=$KAFKA_TOPIC_IN -Dpw=$DEFAULT_PASSWORD -Dloglevel=$LOGLEVEL

   echo "*************************************" 
   echo "* Execute Initialize testcases      *"
   echo "*************************************"
   mvn -DskipTests=false -Dtest=BasicIngestionInitTests test

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn -DskipTests=false -Dtest=BasicIngestionTests test 
   mvn -DskipTests=false -Dtest=BasicIngestionBLKTests test

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.BasicIngestionInitTests.txt
   cat target/surefire-reports/categories.BasicIngestionTests.txt
   cat target/surefire-reports/categories.BasicIngestionBLKTests.txt
fi

echo "*************************************" 
echo "* Report Test Results to Insights   *"
echo "*************************************"
echo "<testsuites>" > /workspace/test-umbrella/tests/smoketests.xml
cat target/surefire-reports/*.xml >> /workspace/test-umbrella/tests/smoketests.xml
echo "</testsuites>" >> /workspace/test-umbrella/tests/smoketests.xml


# Clean up and shutdown the test environment
chmod +x /workspace/test-umbrella/tests/tests/testCleanUp.sh
source /workspace/test-umbrella/tests/tests/testCleanUp.sh
