#!/bin/bash

# Common toolchain setup code for smoketests, fvttests, and ivttest scripts
# Input is test type (smoke, fvt, or ivt)
#
# Environment Variables passed in from the toolchain:
# HELM_RELEASE - deployment release name: ingestion or enrich
# GIT_BRANCH - alvearie repo branch for git clone operation of the alvearie repo
# CLUSTER_NAMESPACE - base name to use when build the TEST_NAMEPSACE name
# DEPLOY_WAIT - the time in seconds to wait for the deployment to be operational after the helm install completes
# HELM_WAIT - the timeout time for the HELM command when using the --wait --timeout MmSs options (where M=minutes and S=seconds)
# ENV_CLEAN_UP - flag to indicate to clean up the test environment at the end
# INGRESS_SUBDOMAIN - ingress subdomain for the deployment
# LOGLEVEL - test execution logging level (logback-test) ERROR, WARNING, or INFO
# DEPLOY_NIFIKOP - true to configure/deploy nifikop, false to skip nifikop deployment

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
sed -i -e "s/alvearie-nifi-headless.alvearie.svc/alvearie-nifi-headless."$TEST_NAMESPACE".svc/g" values.yaml
cat values.yaml | grep $TEST_NAMESPACE

# Add namespace to internalHostName in values.yaml
sed -i -e "s/\&hostname replace-me/\&hostname $TEST_NAMESPACE.$INGRESS_SUBDOMAIN/g" values.yaml
cat values.yaml | grep $TEST_NAMESPACE.$INGRESS_SUBDOMAIN

# setup all the env vars for input to maven
# FHIR Using INGRESS
export FHIR_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir
echo "*************************************"
echo FHIR server: $FHIR_IP
echo "*************************************"

# FHIR PROXY Using INGRESS
export FHIR_PROXY_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir-proxy
echo "*************************************"
echo FHIR Proxy server: $FHIR_PROXY_IP
echo "*************************************"

# FHIR DEID - using INGRESS
export FHIR_DEID_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir-deid
echo "*************************************"
echo FHIR DEID server: $FHIR_DEID_IP
echo "*************************************"

# FHIR DEID PROXY- using INGRESS
export FHIR_DEID_PROXY_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/fhir-deid-proxy
echo "*************************************"
echo FHIR DEID PROXY server: $FHIR_DEID_PROXY_IP
echo "*************************************"

# DEID - using INGRESS
export DEID_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/deid
echo "*************************************"
echo DEID server: $DEID_IP
echo "*************************************"

# NIFI - using INGRESS
export NIFI_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/
echo "*************************************"
echo NIFI server: $NIFI_IP
echo "*************************************"

# EXPOSE KAFKA Service using INGRESS
export EXP_KAFKA_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/expose-kafka
echo "*************************************"
echo EXPOSE KAFKA Service: $EXP_KAFKA_IP
echo "*************************************"

# DEID Prep - using INGRESS
export DEID_PREP_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/deid-prep
echo "*************************************"
echo DEID-PREP server: $DEID_PREP_IP
echo "*************************************"

# TERM Services Prep - using INGRESS
export TERM_PREP_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/term-services-prep
echo "*************************************"
echo TERM-SERVICES-PREP server: $TERM_PREP_IP
echo "*************************************"

# ASCVD From FHIR Service - using INGRESS
export ASCVD_FROM_FHIR_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/ascvd-from-fhir
echo "*************************************"
echo ASCVD-FROM-FHIR server: $ASCVD_FROM_FHIR_IP
echo "*************************************"

# NLP Insights Service - using INGRESS
export NLP_INSIGHTS_IP=$TEST_NAMESPACE.$INGRESS_SUBDOMAIN/nlp-insights
echo "*************************************"
echo NLP Insights server: $NLP_INSIGHTS_IP
echo "*************************************"
