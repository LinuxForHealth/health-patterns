#!/bin/bash

# Run the Avlearie Clinical Enrichment Deploy install per documented instructions
#
# Run the Clinical Enrichment smoke tests and add test results to smoketests.xml for the Insights Quality Dashboard

echo "*************************************"
echo "* Linux version                     *"
echo "*************************************"
cat /etc/redhat-release

echo "*************************************"
echo "* Current Directory                 *"
echo "*************************************"
pwd

echo "*************************************"
echo "* Set Test env variables            *"
echo "*************************************"
export DEFAULT_PASSWORD=integrati0n
export JAVA_HOME=/usr/lib/jvm/java-1.8.0
export TEST_NAMESPACE=$CLUSTER_NAMESPACE"-smoke"
#This is for VPC cluster health-patterns-1
export INGRESS_SUBDOMAIN=wh-health-patterns.dev.watson-health.ibm.com
#export JAVA_TOOL_OPTIONS=-Dhttps.protocols=TLSv1.3 

thisdeploy=$CLUSTER_NAMESPACE
ingest="clinical-ingestion"
enrich="clinical-enrich"

if [ $thisdeploy = $enrich ]
then
   export HELM_RELEASE=enrich
elif [ $thisdeploy = $ingest ] 
then
   export HELM_RELEASE=ingestion
fi


echo "*************************************"
echo "* setup base directory for test     *"
echo "*************************************"
cd /workspace
mkdir $TEST_NAMESPACE
cd $TEST_NAMESPACE

echo "*************************************"
echo "* create namespace and set to it    *"
echo "*************************************"
kubectl create namespace $TEST_NAMESPACE

echo " Set namespace to $TEST_NAMESPACE"
kubectl config set-context --current --namespace=$TEST_NAMESPACE

echo "*************************************"
echo "* Clinical Ingestion Deploy         *"
echo "*************************************"

echo " clone clinical ingestion git repo using "$GIT_BRANCH " branch"
git clone --branch $GIT_BRANCH https://github.com/Alvearie/health-patterns.git

echo " change to the correct directory"
cd health-patterns/helm-charts/health-patterns

echo " helm dependency update"
helm3 dependency update

echo " Current Directory:"
pwd

# Add hostname to values.yaml
sed -i -e "s/\&hostname replace-me/\&hostname $TEST_NAMESPACE.$INGRESS_SUBDOMAIN/g" values.yaml
cat values.yaml | grep $TEST_NAMESPACE.$INGRESS_SUBDOMAIN

if [ $thisdeploy = $enrich ] 
then
   # deploy enrich
   echo "$CLUSTER_NAMESPACE - enrich : Deploy via helm3  using Ingress"
   helm3 install $HELM_RELEASE . -f clinical_enrichment.yaml --set ascvd-from-fhir.ingress.enabled=true --set deid-prep.ingress.enabled=true --set term-services-prep.ingress.enabled=true --set nlp-insights.enabled=true --set nlp-insights.ingress.enabled=true --set nlp-insights.nlpservice.quickumls.endpoint=https://quickumls.wh-health-patterns.dev.watson-health.ibm.com/match --set nlp-insights.nlpservice.acd.endpoint=https://us-east.wh-acd.cloud.ibm.com/wh-acd/api --set nlp-insights.nlpservice.acd.apikey=$ACD_APIKEY --set nlp-insights.nlpservice.acd.flow=wh_acd.ibm_clinical_insights_v1.0_standard_flow --wait --timeout 6m0s
elif [ $thisdeploy = $ingest ] 
then
   # deploy ingestion
   echo "$CLUSTER_NAMESPACE - ingestion : Deploy via helm3  using Ingress"
   date
   helm3 install $HELM_RELEASE . -f clinical_ingestion.yaml --wait --timeout 6m0s
   date
fi

# setup all the env vars for input to maven
# FHIR Using INGRESS
export FHIR_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir
export FHIR_PORT=
echo "*************************************"
echo FHIR server: $FHIR_IP$FHIR_PORT
echo "*************************************"

# FHIR DEID - using INGRESS
export FHIR_DEID_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir-deid
export FHIR_DEID_PORT=
echo "*************************************"
echo FHIR DEID server: $FHIR_DEID_IP$FHIR_DEID_PORT
echo "*************************************"

# DEID - using INGRESS
export DEID_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/deid
export DEID_PORT=
echo "*************************************"
echo DEID server: $DEID_IP$DEID_PORT
echo "*************************************"

# NIFI - using INGRESS
export NIFI_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/
export NIFI_PORT=
echo "*************************************"
echo NIFI server: $NIFI_IP$NIFI_PORT
echo "*************************************"

# EXPOSE KAFKA Service using INGRESS
export EXP_KAFKA_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/expose-kafka
export EXP_KAFKA_PORT=
echo "*************************************"
echo EXPOSE KAFKA Service: $EXP_KAFKA_IP$EXP_KAFKA_PORTT
echo "*************************************"

# DEID Prep - using INGRESS
export DEID_PREP_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/deid-prep
export DEID_PREP_PORT=
echo "*************************************"
echo DEID-PREP server: $DEID_PREP_IP$DEID_PREP_PORT
echo "*************************************"

# TERM Services Prep - using INGRESS
export TERM_PREP_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/term-services-prep
export TERM_PREP_PORT=
echo "*************************************"
echo TERM-SERVICES-PREP server: $TERM_PREP_IP$TERM_PREP_PORT
echo "*************************************"

# ASCVD From FHIR Service - using INGRESS
export ASCVD_FROM_FHIR_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/ascvd-from-fhir
export ASCVD_FROM_FHIR_PORT=
echo "*************************************"
echo ASCVD-FROM-FHIR server: $ASCVD_FROM_FHIR_IP$ASCVD_FROM_FHIR_PORT
echo "*************************************"

# NLP Insights Service - using INGRESS
export NLP_INSIGHTS_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/nlp-insights
export NLP_INSIGHTS_PORT=
echo "*************************************"
echo NLP Insights server: $NLP_INSIGHTS_IP$NLP_INSIGHTS_PORT
echo "*************************************"

# Wait for deployment to be ready
if [ $thisdeploy = $enrich ] 
then 
   echo "*************************************"
   echo "* Waiting for 2 minutes             *"
   echo "*************************************"
   date
   sleep 120  
   date   
elif [ $thisdeploy = $ingest ] 
then 
   echo "*************************************"
   echo "* Waiting for 5 minutes             *"
   echo "*************************************"
   date
   sleep 300  
   date
fi

echo "*************************************" 
echo "* A Look At Everything              *"
echo "*************************************"
kubectl get all

if [ $thisdeploy = $enrich ] 
then 
   echo "****************************************************" 
   echo "* Goto the testcase folder in the repo             *"
   echo "****************************************************"
   cd /workspace/$TEST_NAMESPACE/health-patterns/clinical-enrichment/
   pwd
   ls

   echo "*************************************" 
   echo "* Build the testcases               *"
   echo "*************************************"
   mvn clean install -e -Dip.fhir=$FHIR_IP -Dport.fhir=$FHIR_PORT -Dip.fhir.deid=$FHIR_DEID_IP -Dport.fhir.deid=$FHIR_DEID_PORT -Dip.deid.prep=$DEID_PREP_IP -Dport.deid.prep=$DEID_PREP_PORT -Dip.term.prep=$TERM_PREP_IP -Dport.term.prep=$TERM_PREP_PORT -Dip.ascvd.from.fhir=$ASCVD_FROM_FHIR_IP -Dport.ascvd.from.fhir=$ASCVD_FROM_FHIR_PORT -Dip.nlp.insights=$NLP_INSIGHTS_IP -Dport.nlp.insights=$NLP_INSIGHTS_PORT -Dpw=$DEFAULT_PASSWORD

   echo "*************************************" 
   echo "* Properties File:                  *"
   echo "*************************************"
   cat src/test/resources/enrich-flow.properties

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn -e -DskipTests=false -Dtest=EnrichmentInitTests test
   mvn -e -DskipTests=false -Dtest=BasicEnrichmentTests test
   mvn -e -DskipTests=false -Dtest=EnrichmentConfigTests test
   mvn -e -DskipTests=false -Dtest=ASCVDEnrichmentTests test

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.EnrichmentInitTests.txt
   cat target/surefire-reports/categories.BasicEnrichmentTests.txt
   cat target/surefire-reports/categories.EnrichmentConfigTests.txt
   cat target/surefire-reports/categories.ASCVDEnrichmentTests.txt

   echo "*************************************" 
   echo "* Report Test Results to Insights   *"
   echo "*************************************"
   echo "<testsuites>" > /workspace/clinical-enrichment/tests/smoketests.xml
   cat target/surefire-reports/*.xml >> /workspace/clinical-enrichment/tests/smoketests.xml
   echo "</testsuites>" >> /workspace/clinical-enrichment/tests/smoketests.xml
elif [ $thisdeploy = $ingest ] 
then
   echo "****************************************************" 
   echo "* Goto the testcase folder in the repo             *"
   echo "****************************************************"
   cd /workspace/$TEST_NAMESPACE/health-patterns/ingest/
   pwd
   ls
   
   echo "*************************************" 
   echo "* Build the testcases               *"
   echo "*************************************"
   mvn clean install -e -Dip.fhir=$FHIR_IP -Dport.fhir=$FHIR_PORT -Dip.fhir.deid=$FHIR_DEID_IP -Dport.fhir.deid=$FHIR_DEID_PORT -Dip.nifi=$NIFI_IP -Dport.nifi=$NIFI_PORT -Dip.nifi.api=$NIFI_API_IP -Dport.nifi.api=$NIFI_API_PORT -Dip.kafka=$KAFKA_IP -Dport.kafka=$KAFKA_PORT -Dip.deid=$DEID_IP -Dport.deid=$DEID_PORT -Dip.expkafka=$EXP_KAFKA_IP -Dport.expkafka=$EXP_KAFKA_PORT -Dpw=$DEFAULT_PASSWORD

   echo "*************************************" 
   echo "* Initialize the testcases          *"
   echo "*************************************"
   mvn -e -DskipTests=false -Dtest=BasicClinicalIngestionInitTests test

   echo "*************************************" 
   echo "* Execute the testcases             *"
   echo "*************************************"
   mvn -e -DskipTests=false -Dtest=BasicClinicalIngestionFlowTests test 

   # JUNIT execution reports available in the below folder
   ls -lrt target/surefire-reports
   cat target/surefire-reports/categories.BasicClinicalIngestionInitTests.txt
   cat target/surefire-reports/categories.BasicClinicalIngestionFlowTests.txt

   echo "*************************************" 
   echo "* Report Test Results to Insights   *"
   echo "*************************************"
   echo "<testsuites>" > /workspace/ingest/tests/smoketests.xml
   cat target/surefire-reports/*.xml >> /workspace/ingest/tests/smoketests.xml
   echo "</testsuites>" >> /workspace/ingestion/tests/smoketests.xml
fi


# then clean up
echo "*************************************"
echo "* Delete the Deployment             *"
echo "*************************************"
helm3 delete $HELM_RELEASE
kubectl delete namespace $TEST_NAMESPACE


# temp create a results file with "good" results while this script is developed
#cd /workspace/clinical-ingestion/e2e-tests
#output="<testcase classname=\"bash\" name=\"test1\" time=\"0\"/>"
#currentTime=`date +"%Y-%m-%dT%T"`
#header="<testsuite name=\"Smoke tests\" tests=\"0\" failures=\"0\" errors=\"0\" skipped=\"0\" timestamp=\"${currentTime}\" time=\"0\">"
#footer="</testsuite>"

#echo "Current Directory"
#pwd

#cat << EOF > smoketests.xml
#$header
#$output
#$footer
#EOF