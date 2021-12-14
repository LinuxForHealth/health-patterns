#!/bin/bash

# Run the Avlearie enrich/ingestion Deploy install per documented instructions (selection based on CLUSER_NAMESPACE from toolchain input
#
# Run the enrich/ingestion smoke tests and add test results to ivttests.xml for the Insights Quality Dashboard
#
# Environment Variables passed in from the toolchain:
# CLUSTER_NAMESPACE - base name to use when build the TEST_NAMEPSACE name
# DEPLOY_WAIT - the time in seconds to wait for the deployment to be operational after the helm install completes
# HELM_TIMEOUT - the timeout time for the HELM command when using the --wait --timeout MmSs options (where M=minutes and S=seconds)
# ENV_CLEAN_UP - flag to indicate to clean up the test environment at the end
# INGRESS_SUBDOMAIN - ingress subdomain for the deployment
# LOGLEVEL - test execution logging level (logback-test) ERROR, WARNING, or INFO

# Setup the test environment
chmod +x ./tests/toolchain-envsetup.sh
source ./tests/toolchain-envsetup.sh "ivt"

# Setup for NifiKop Deployment
cd /workspace/$TEST_NAMESPACE/health-patterns/test-umbrella/tests
chmod +x ./tests/NifiKopValues.sh
source ./tests/NifiKopValues.sh

# Use kafka input topic used in sercure Nifi
export KAFKA_TOPIC_IN="ingest.topic.in"

echo " change to the correct deployment directory"
cd /workspace/$TEST_NAMESPACE/health-patterns/helm-charts/health-patterns

# Execute the desired deployment
echo "***************************************"
echo $TEST_NAMESPACE" : Deploy via helm3"
date
echo "***************************************"
if [ $CLUSTER_NAMESPACE = "tst-enrich" ] 
then
  # disable the ingestion deploy for an enrich-only deployment
  sed -i -e "s/\&ingestionEnabled true/\&ingestionEnabled false/g" values.yaml

  # deploy enrich
  helm3 install $HELM_RELEASE . -f /workspace/$TEST_NAMESPACE/health-patterns/enrich/src/test/resources/configs/NLP-IVT-values.yaml --set ascvd-from-fhir.ingress.enabled=true --set deid-prep.ingress.enabled=true --set term-services-prep.ingress.enabled=true --set nlp-insights.nlpservice.acd.apikey=$ACD_APIKEY --wait --timeout $HELM_TIMEOUT
elif [ $CLUSTER_NAMESPACE = "tst-ingest" ] 
then

   # deploy ingestion
   helm3 install $HELM_RELEASE . -f /workspace/$TEST_NAMESPACE/health-patterns/ingest/src/test/resources/configs/NLP-ingestion-values.yaml  --set fhir.proxy.enabled=true --set fhir-deid.proxy.enabled=true --set nlp-insights.nlpservice.acd.apikey=$ACD_APIKEY --wait --timeout $HELM_TIMEOUT --set fhir-data-quality.enabled=true --set fhir-data-quality.requestTimeout=60 --set expose-kafka.requestTimeout=60
fi


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


if [ $CLUSTER_NAMESPACE = "tst-enrich" ]  
then

   echo "****************************************************" 
   echo "* Goto the testcase folder in the repo             *"
   echo "****************************************************"
   cd /workspace/$TEST_NAMESPACE/health-patterns/enrich/

   echo "*************************************" 
   echo "* Build the testcases               *"
   echo "*************************************"
   mvn clean install  --log-file ./mvnBuild.log -Dip.fhir=$FHIR_IP -Dip.fhir.deid=$FHIR_DEID_IP -Dip.deid.prep=$DEID_PREP_IP -Dip.term.prep=$TERM_PREP_IP -Dip.ascvd.from.fhir=$ASCVD_FROM_FHIR_IP -Dip.nlp.insights=$NLP_INSIGHTS_IP -Dpw=$DEFAULT_PASSWORD -Dloglevel=$LOGLEVEL

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn -DskipTests=false -Dtest=EnrichmentInitTests test
   mvn -DskipTests=false -Dtest=BasicEnrichmentTests test
   mvn -DskipTests=false -Dtest=EnrichmentConfigTests test
   mvn -DskipTests=false -Dtest=ASCVDEnrichmentTests test
   mvn -DskipTests=false -Dtest=NLPEnrichmentTests test

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.EnrichmentInitTests.txt
   cat target/surefire-reports/categories.BasicEnrichmentTests.txt
   cat target/surefire-reports/categories.EnrichmentConfigTests.txt
   cat target/surefire-reports/categories.ASCVDEnrichmentTests.txt
   cat target/surefire-reports/categories.NLPEnrichmentTests.txt

elif [ $CLUSTER_NAMESPACE = "tst-ingest" ] 
then

   echo "****************************************************" 
   echo "* Goto the testcase folder in the repo             *"
   echo "****************************************************"
   cd /workspace/$TEST_NAMESPACE/health-patterns/ingest/
  
   echo "*************************************" 
   echo "* Build the testcases               *"
   echo "*************************************"
   mvn clean install --log-file ./mvnBuild.log -Dip.fhir=$FHIR_IP -Dip.fhir.proxy=$FHIR_PROXY_IP -Dip.fhir.deid=$FHIR_DEID_IP -Dip.fhir.deid.proxy=$FHIR_DEID_PROXY_IP -Dip.deid=$DEID_IP -Dip.nifi=$NIFI_IP -Dip.expkafka=$EXP_KAFKA_IP -Dip.nlp.insights=$NLP_INSIGHTS_IP -Dkafka.topic.in=$KAFKA_TOPIC_IN -Dpw=$DEFAULT_PASSWORD -Dloglevel=$LOGLEVEL

   echo "*************************************" 
   echo "* Initialize the testcases          *"
   echo "*************************************"
   mvn --log-file ./BasicIngestionInitTests.log -DskipTests=false -Dtest=BasicIngestionInitTests test

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn -DskipTests=false -Dtest=FHIRProxyIngestionTests test
   mvn -DskipTests=false -Dtest=BasicIngestionTests test
   mvn -DskipTests=false -Dtest=BasicIngestionBLKTests test
   mvn -DskipTests=false -Dtest=DeIDIngestionTests test
   mvn -DskipTests=false -Dtest=DeIDIngestionBLKTests test
   mvn -DskipTests=false -Dtest=ASCVDIngestionTests test
   mvn -DskipTests=false -Dtest=ASCVDIngestionBLKTests test
   mvn -DskipTests=false -Dtest=NLPIngestionTests test
   mvn -DskipTests=false -Dtest=NLPIngestionBLKTests test
   mvn -DskipTests=false -Dtest=FHIRDataQualityBLKTests test

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.BasicIngestionInitTests.txt
   cat target/surefire-reports/categories.FHIRProxyIngestionTests.txt
   cat target/surefire-reports/categories.BasicIngestionTests.txt
   cat target/surefire-reports/categories.BasicIngestionBLKTests.txt
   cat target/surefire-reports/categories.DeIDIngestionTests.txt
   cat target/surefire-reports/categories.DeIDIngestionBLKTests.txt
   cat target/surefire-reports/categories.ASCVDIngestionTests.txt
   cat target/surefire-reports/categories.ASCVDIngestionBLKTests.txt
   cat target/surefire-reports/categories.NLPIngestionTests.txt
   cat target/surefire-reports/categories.NLPIngestionBLKTests.txt
   cat target/surefire-reports/categories.FHIRDataQualityBLKTests.txt   
    
fi   
echo "*************************************" 
echo "* Report Test Results to Insights   *"
echo "*************************************"
echo "<testsuites>" > /workspace/test-umbrella/tests/ivttest.xml
cat target/surefire-reports/*.xml >> /workspace/test-umbrella/tests/ivttest.xml
echo "</testsuites>" >> /workspace/test-umbrella/tests/ivttest.xml


# Clean up and shutdown the test environment
chmod +x /workspace/test-umbrella/tests/tests/testCleanUp.sh
source /workspace/test-umbrella/tests/tests/testCleanUp.sh
