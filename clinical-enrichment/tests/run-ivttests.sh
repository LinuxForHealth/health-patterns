#!/usr/bin/env bash

# Run the Alvearie Clinical Ingestion Deploy install per documented instructions
#
# Run the Clinical Ingestion flow IVT tests and add test results to ivttest.xml for the Insights Quality Dashboard

echo "*************************************"
echo "* Linux version                     *"
echo "*************************************"
cat /etc/redhat-release

echo "*************************************"
echo "* Current Directory                 *"
echo "*************************************"
pwd
  
#echo "*************************************"
#echo "* Install OpenJDK 14                *"
#echo "*************************************"
#wget --quiet https://download.java.net/java/GA/jdk14.0.2/205943a0976c4ed48cb16f1043c5c647/12/GPL/openjdk-14.0.2_linux-x64_bin.tar.gz
#tar -xf openjdk-14.0.2_linux-x64_bin.tar.gz
#sudo mv jdk-14.0.2 /usr/lib/jvm

#ls /usr/lib/jvm
 
echo "*************************************"
echo "* Set Test env variables            *"
echo "*************************************"
export DEFAULT_PASSWORD=integrati0n
export JAVA_HOME=/usr/lib/jvm/java-1.8.0
export HELM_RELEASE=ingestion
export TEST_NAMESPACE=$CLUSTER_NAMESPACE"-ivt"
#This is for VPC cluster health-patterns-1
export INGRESS_SUBDOMAIN=wh-health-patterns.dev.watson-health.ibm.com
export INGRESS_CLASS=public-iks-k8s-nginx
#export JAVA_TOOL_OPTIONS=-Dhttps.protocols=TLSv1.3


echo "**************************************" 
echo "* What SSL/TSL Versions we are using *"
echo "**************************************"
openssl ciphers -v | awk '{print $2}' | sort | uniq 

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

echo " clone clinical ingestion git repo"
git clone https://github.com/Alvearie/health-patterns.git

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
sed -i -e "s/\&hostname/\&hostname $TEST_NAMESPACE.$INGRESS_SUBDOMAIN/g" values.yaml
cat values.yaml | grep $TEST_NAMESPACE.$INGRESS_SUBDOMAIN
 
# deploy 
echo "Deploy via helm3 with De-id service, enabling FHIR Proxy server IPs,  using Ingress"
helm3 install $HELM_RELEASE . -f de-id-pattern-values.yaml -f clinical_ingestion.yaml --set fhir.proxy.enabled=true --set fhir-deid.proxy.enabled=true

# setup all the env vars for input to maven
# FHIR Using INGRESS
export FHIR_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir
export FHIR_PORT=
echo "*************************************"
echo FHIR server: $FHIR_IP$FHIR_PORT
echo "*************************************"

# FHIR PROXY Using INGRESS
export FHIR_PROXY_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir-proxy
export FHIR__PROXY_PORT=
echo "*************************************"
echo FHIR Proxy server: $FHIR_PROXY_IP$FHIR_PROXY_PORT
echo "*************************************"

# FHIR DEID - using INGRESS
export FHIR_DEID_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir-deid
export FHIR_DEID_PORT=
echo "*************************************"
echo FHIR DEID server: $FHIR_DEID_IP$FHIR_DEID_PORT
echo "*************************************"

# FHIR DEID PROXY- using INGRESS
export FHIR_DEID_PROXY_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir-deid-proxy
export FHIR_DEID_PROXY_PORT=
echo "*************************************"
echo FHIR DEID PROXY server: $FHIR_DEID_PROXY_IP$FHIR_DEID_PROXY_PORT
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

# NIFI API using INGRESS
export NIFI_API_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/nifi-http-post
export NIFI_API_PORT=
echo "*************************************"
echo NIFI HTTP Post API: $NIFI_API_IP$NIFI_API_PORT
echo "*************************************"

# EXPOSE KAFKA Service using INGRESS
export EXP_KAFKA_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/expose-kafka
export EXP_KAFKA_PORT=
echo "*************************************"
echo EXPOSE KAFKA Service: $EXP_KAFKA_IP$EXP_KAFKA_PORTT
echo "*************************************"

# Wait a bit for Nifi to come up
# Need to change this to some polling of service status for more reliability 
echo "*************************************"
echo "* Waiting for 5 minutes             *"
echo "*************************************"
date
sleep 300  
date

# KAFKA - using Load Balancer
export KAFKA_IP=$(kubectl get svc --namespace $TEST_NAMESPACE $HELM_RELEASE-kafka-0-external -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
export KAFKA_PORT=:$(kubectl get svc $HELM_RELEASE-kafka-0-external -o jsonpath='{.spec.ports[0].port}') 
echo KAFKA server: $KAFKA_IP$KAFKA_PORT

echo "*************************************" 
echo "* A Look At Everything              *"
echo "*************************************"
kubectl get all

echo "*************************************" 
echo "* Get the testcase repo             *"
echo "*************************************"
cd /workspace/$TEST_NAMESPACE
git clone -b $UMBRELLA_GIT_BRANCH https://${gitApiKey}@github.ibm.com/integrationsquad/test.git
cd /workspace/$TEST_NAMESPACE/test

echo "*************************************" 
echo "* Build the testcases               *"
echo "*************************************"
mvn clean install -e -Dip.fhir=$FHIR_IP -Dport.fhir=$FHIR_PORT -Dip.fhir.proxy=$FHIR_PROXY_IP -Dport.fhir.proxy=$FHIR__PROXY_PORT -Dip.fhir.deid=$FHIR_DEID_IP -Dport.fhir.deid=$FHIR_DEID_PORT -Dip.fhir.deid.proxy=$FHIR_DEID_PROXY_IP -Dport.fhir.deid.proxy=$FHIR_DEID_PROXY_PORT -Dip.nifi=$NIFI_IP -Dport.nifi=$NIFI_PORT -Dip.nifi.api=$NIFI_API_IP -Dport.nifi.api=$NIFI_API_PORT -Dip.kafka=$KAFKA_IP -Dport.nifi.api=$NIFI_API_PORT -Dip.deid=$DEID_IP -Dport.deid=$DEID_PORT  -Dip.expkafka=$EXP_KAFKA_IP -Dport.expkafka=$EXP_KAFKA_PORT -Dpw=$DEFAULT_PASSWORD

echo "*************************************" 
echo "* Initialize the testcases          *"
echo "*************************************"
mvn -e -DskipTests=false -Dtest=BasicClinicalIngestionInitTests test

echo "*************************************" 
echo "* Execute the testcases             *"
echo "*************************************"
mvn  -e -DskipTests=false -Dtest=FHIRProxyClinicalIngestionFlowTests test
mvn  -e -DskipTests=false -Dtest=BasicClinicalIngestionFlowTests test
mvn  -e -DskipTests=false -Dtest=DeIDClinicalIngestionFlowTests test
mvn  -e -DskipTests=false -Dtest=ASCVDClinicalIngestionFlowTests test

echo "**************************************" 
echo "* What SSL/TSL Versions we are using *"
echo "**************************************"
openssl ciphers -v | awk '{print $2}' | sort | uniq 

# JUNIT execution reports available in the below folder
ls -lrt target/surefire-reports
cat target/surefire-reports/integration.categories.FHIRProxyClinicalIngestionFlowTests.txt
cat target/surefire-reports/integration.categories.BasicClinicalIngestionInitTests.txt
cat target/surefire-reports/integration.categories.BasicClinicalIngestionFlowTests.txt
cat target/surefire-reports/integration.categories.DeIDClinicalIngestionFlowTests.txt
cat target/surefire-reports/integration.categories.ASCVDClinicalIngestionFlowTests.txt

echo "*************************************" 
echo "* Report Test Results to Insights   *"
echo "*************************************"
echo "<testsuites>" > /workspace/clinical-ingestion/e2e-tests/ivttest.xml
cat target/surefire-reports/*.xml >> /workspace/clinical-ingestion/e2e-tests/ivttest.xml
echo "</testsuites>" >> /workspace/clinical-ingestion/e2e-tests/ivttest.xml

ls -lrt /workspace/clinical-ingestion/e2e-tests

# then clean up
echo "*************************************"
echo "* Delete the Deployment & Namespace *"
echo "*************************************"
helm3 delete $HELM_RELEASE
kubectl delete namespace $TEST_NAMESPACE
