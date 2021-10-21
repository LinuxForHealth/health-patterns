#!/bin/bash

# Common toolchain setup code for smoketests, fvttests, and ivttest scripts
# Input is test type (smoke, fvt, or ivt)

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
export TEST_NAMESPACE=$CLUSTER_NAMESPACE"-"$1

#This is for VPC cluster health-patterns-1
export INGRESS_SUBDOMAIN=wh-health-patterns.dev.watson-health.ibm.com 

# Set the deploymemt-specific variables/values
if [ $CLUSTER_NAMESPACE = "enrich" ]
then
   export HELM_RELEASE=enrich
   export deploywait=240
elif [ $CLUSTER_NAMESPACE = "ingest" ] 
then
   export HELM_RELEASE=ingestion
   export deploywait=360
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
echo "* Fetch the Code from Repo          *"
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
