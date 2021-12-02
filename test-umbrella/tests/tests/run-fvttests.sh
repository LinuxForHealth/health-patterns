#!/bin/bash

# Run the Avlearie enrich/ingestion Deploy install per documented instructions (selection based on CLUSER_NAMESPACE from toolchain input
#
# Run the enrich/ingestion FVT and add test results to fvttest.xml for the Insights Quality Dashboard
#
# Environment Variables passed in from the toolchain:
# CLUSTER_NAMESPACE - base name to use when build the TEST_NAMEPSACE name
# DEPLOY_WAIT - the time in seconds to wait for the deployment to be operational after the helm install completes
# HELM_TIMEOUT - the timeout time for the HELM command when using the --wait --timeout MmSs options (where M=minutes and S=seconds)
# ENV_CLEAN_UP - flag to indicate to clean up the test environment at the end
# INGRESS_SUBDOMAIN - ingress subdomain for the deployment

# Setup the test environment
chmod +x ./tests/toolchain-envsetup.sh
source ./tests/toolchain-envsetup.sh "fvt"

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
   helm3 install $HELM_RELEASE . --set ascvd-from-fhir.ingress.enabled=true --set deid-prep.ingress.enabled=true --set term-services-prep.ingress.enabled=true --set nlp-insights.enabled=true --set nlp-insights.ingress.enabled=true  --wait --timeout $HELM_TIMEOUT
elif [ $CLUSTER_NAMESPACE = "tst-ingest" ] 
then
   # deploy ingestion
   helm3 install $HELM_RELEASE . --wait --timeout $HELM_TIMEOUT 
fi

echo "*************************************"
echo "* Waiting for "$DEPLOY_WAIT" seconds          *"
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
   mvn clean install -e -Dip.fhir=$FHIR_IP -Dip.fhir.deid=$FHIR_DEID_IP -Dip.deid.prep=$DEID_PREP_IP -Dip.term.prep=$TERM_PREP_IP -Dip.ascvd.from.fhir=$ASCVD_FROM_FHIR_IP -Dip.nlp.insights=$NLP_INSIGHTS_IP -Dpw=$DEFAULT_PASSWORD

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn -e -DskipTests=false -Dtest=EnrichmentInitTests test
   mvn -e -DskipTests=false -Dtest=BasicEnrichmentTests test
   mvn -e -DskipTests=false -Dtest=EnrichmentConfigTests test
   mvn -e -DskipTests=false -Dtest=ASCVDEnrichmentTests test
   mvn -e -DskipTests=false -Dtest=NLPEnrichmentFVTTests test

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.EnrichmentInitTests.txt
   cat target/surefire-reports/categories.BasicEnrichmentTests.txt
   cat target/surefire-reports/categories.EnrichmentConfigTests.txt
   cat target/surefire-reports/categories.ASCVDEnrichmentTests.txt
   cat target/surefire-reports/categories.NLPEnrichmentFVTTests.txt
   
elif [ $CLUSTER_NAMESPACE = "tst-ingest" ] 
then

   echo "****************************************************" 
   echo "* Goto the testcase folder in the repo             *"
   echo "****************************************************"
   cd /workspace/$TEST_NAMESPACE/health-patterns/ingest/

   echo "*************************************" 
   echo "* Build the testcases               *"
   echo "*************************************"
   mvn clean install -e -Dip.fhir=$FHIR_IP -Dip.fhir.deid=$FHIR_DEID_IP -Dip.nifi=$NIFI_IP -Dip.nifi.api=$NIFI_API_IP -Dip.kafka=$KAFKA_IP -Dip.deid=$DEID_IP -Dip.expkafka=$EXP_KAFKA_IP -Dkafka.topic.in=$KAFKA_TOPIC_IN -Dpw=$DEFAULT_PASSWORD

   echo "*************************************" 
   echo "* Execute the initialize testcases  *"
   echo "*************************************"
   mvn -e -DskipTests=false -Dtest=BasicIngestionInitTests test

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn  -e  -DskipTests=false -Dtest=BasicIngestionTests test
   mvn  -e  -DskipTests=false -Dtest=BasicIngestionBLKTests test
   mvn  -e  -DskipTests=false -Dtest=DeIDIngestionTests test
   mvn  -e  -DskipTests=false -Dtest=DeIDIngestionBLKTests test
   mvn  -e  -DskipTests=false -Dtest=ASCVDIngestionTests test
   mvn  -e  -DskipTests=false -Dtest=ASCVDIngestionBLKTests test

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.BasicIngestionInitTests.txt
   cat target/surefire-reports/categories.BasicIngestionTests.txt
   cat target/surefire-reports/categories.BasicIngestionBLKTests.txt
   cat target/surefire-reports/categories.DeIDIngestionTests.txt
   cat target/surefire-reports/categories.DeIDIngestionBLKTests.txt
   cat target/surefire-reports/categories.ASCVDIngestionTests.txt
   cat target/surefire-reports/categories.ASCVDIngestionBLKTests.txt

fi

echo "*************************************" 
echo "* Report Test Results to Insights   *"
echo "*************************************"
echo "<testsuites>" > /workspace/test-umbrella/tests/fvttest.xml
cat target/surefire-reports/*.xml >> /workspace/test-umbrella/tests/fvttest.xml
echo "</testsuites>" >> /workspace/test-umbrella/tests/fvttest.xml

# Looking for test failures. If any are found, then save the environment for debug 
TEST_FAILURE=$(cat target/surefire-reports/*.txt | grep FAILURE!)

if [[ cat target/surefire-reports/*.txt | grep FAILURE! ]]
then
   echo "********************************************************************"
   echo "*  Test Failures detected.  Saving the test environment for debug. *"
   echo "********************************************************************"
   ENV_CLEAN_UP = "false"
else
   echo "*********************************"
   echo "*  No Test Failures detected.   *"
   echo "*********************************"  
fi

# ENV_CLEAN_UP is set in the toolchain environment properties.  The default value is true, but it can be changed on toolchain start
# It can can be set to false if test errors are detected
# if we need to keep the test environment available for debug
if [ $ENV_CLEAN_UP = "true" ]  
then
	# then clean up
	echo "*************************************"
	echo "* Delete the Deployment             *"
	echo "*************************************"
	helm3 delete $HELM_RELEASE
	echo "*************************************"
	echo "* Waiting for 30  seconds           *"
	echo "*************************************"
	date
	sleep 30   
	date
	echo "*************************************"
	echo "* Delete NifiKop                    *"
	echo "*************************************"
	helm3 delete nifikop
	echo "*************************************"
	echo "* Waiting for 30  seconds           *"
	echo "*************************************"
	date
	sleep 30  
	date
	echo "*************************************"
	echo "* Delete Namespace                  *"
	echo "*************************************"
	kubectl delete namespace $TEST_NAMESPACE	
else
    # save the test deployment
	echo "*************************************************************"
	echo "* Test deployment "$HELM_RELEASE" in "$TEST_NAMESPACE" saved            *"
	echo "*************************************************************"
fi
