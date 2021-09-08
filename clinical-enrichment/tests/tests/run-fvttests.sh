#!/usr/bin/env bash

# Run the Avlearie Clinical Enrichment Deploy install per documented instructions
#
# Run the Clinical Enrichment smoke tests and add test results to fvttest.xml for the Insights Quality Dashboard

echo "*************************************"
echo "* Linux version                     *"
echo "*************************************"
cat /etc/redhat-release

echo "*************************************"
echo "* Current Directory                 *"
echo "*************************************"
pwd
  
#echo "*************************************"
#echo "* Install OpenJDK 11                *"
#echo "*************************************"
#wget --quiet https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz
#tar -xf openjdk-11+28_linux-x64_bin.tar.gz
#sudo mv jdk-14.0.2 /usr/lib/jvm

#ls /usr/lib/jvm

echo "*************************************"
echo "* Set Test env variables            *"
echo "*************************************"
export DEFAULT_PASSWORD=integrati0n
export JAVA_HOME=/usr/lib/jvm/java-1.8.0
export HELM_RELEASE=enrich
export TEST_NAMESPACE=$CLUSTER_NAMESPACE"-fvt"
#This is for VPC cluster health-patterns-1
export INGRESS_SUBDOMAIN=wh-health-patterns.dev.watson-health.ibm.com
#export JAVA_TOOL_OPTIONS=-Dhttps.protocols=TLSv1.3 

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

# figure out the ingress subdomain and save as INGRESS_SUBDOMAIN
# This is for non-VPC clusters
#export INGRESS_SUBDOMAIN=$(ibmcloud ks cluster get --cluster integration-k8s-cluster -json | grep hostname)
#export INGRESS_SUBDOMAIN=${INGRESS_SUBDOMAIN:21}
#export INGRESS_SUBDOMAIN=${INGRESS_SUBDOMAIN:0:${#INGRESS_SUBDOMAIN}-2}

# Add hostname to values.yaml
sed -i -e "s/\&hostname replace-me/\&hostname $TEST_NAMESPACE.$INGRESS_SUBDOMAIN/g" values.yaml
cat values.yaml | grep $TEST_NAMESPACE.$INGRESS_SUBDOMAIN
 
echo "********************************************************************" 
echo "* Copy ACD and quickUMLS config files for the NLP-Insights Service *" 
echo "********************************************************************" 
# Setup config files for the NLP-Insights service for ACD
cp -f /workspace/$TEST_NAMESPACE/health-patterns/clinical-enrichment/src/test/resources/configs/acd_config.ini  /workspace/$TEST_NAMESPACE/health-patterns/services/nlp-insights/text_analytics/acd/acd_config.ini
# Setup config files for the NLP-Insights service for quickUMLS
cp -f /workspace/$TEST_NAMESPACE/health-patterns/clinical-enrichment/src/test/resources/configs/quickumls_config.ini /workspace/$TEST_NAMESPACE/health-patterns/services/nlp-insights/text_analytics/quickUMLS/quickumls.ini
 
# deploy 
echo "Deploy via helm3  using Ingress"
helm3 install $HELM_RELEASE . -f clinical_enrichment.yaml --set ascvd-from-fhir.ingress.enabled=true --set deid-prep.ingress.enabled=true --set term-services-prep.ingress.enabled=true --set nlp-insights.enabled=true --set nlp-insights.ingress.enabled=true --wait --timeout 6m0s

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

# Wait a bit for Nifi to come up
# Need to change this to some polling of service status for more reliability 
echo "*************************************"
echo "* Waiting for 2 minutes             *"
echo "*************************************"
date
sleep 120  
date

# KAFKA - using Load Balancer
export KAFKA_IP=$(kubectl get svc --namespace $TEST_NAMESPACE $HELM_RELEASE-kafka-0-external -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
export KAFKA_PORT=:$(kubectl get svc $HELM_RELEASE-kafka-0-external -o jsonpath='{.spec.ports[0].port}') 
echo KAFKA server: $KAFKA_IP$KAFKA_PORT

echo "*************************************" 
echo "* A Look At Everything              *"
echo "*************************************"
kubectl get all

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
echo "<testsuites>" > /workspace/clinical-enrichment/tests/fvttest.xml
cat target/surefire-reports/*.xml >> /workspace/clinical-enrichment/tests/fvttest.xml
echo "</testsuites>" >> /workspace/clinical-enrichment/tests/fvttest.xml

# then clean up
echo "*************************************"
echo "* Delete the Deployment             *"
echo "*************************************"
helm3 delete $HELM_RELEASE
kubectl delete namespace $TEST_NAMESPACE
