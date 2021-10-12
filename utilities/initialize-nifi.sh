#!/bin/bash

scripts/wait-for-nifi.sh $HOSTNAME 8080

scripts/initialize-reporting-task.sh $HOSTNAME 8080

if [ "$ADD_CLINICAL_INGESTION" = true ] ; then
python /scripts/loadHealthPatternsFlows.py \
  --baseUrl=http://$HOSTNAME:8080/ \
  --reg=$NIFI_REGISTRY \
  --bucket=Health_Patterns \
  --flowName="Clinical Ingestion" \
  --version=34
  --baseUrl=http://$HOSTNAME:8080/
fi

if [ "$ADD_CLINICAL_ENRICHMENT" = true ] ; then
python /scripts/loadHealthPatternsFlows.py \
  --baseUrl=http://$HOSTNAME:8080/ \
  --reg=$NIFI_REGISTRY \
  --bucket=Health_Patterns \
  --flowName="FHIR Bundle Enrichment" \
  --version=11
  --baseUrl=http://$HOSTNAME:8080/ \
  --x=0.0 \
  --y=200.0
fi

python /scripts/startHealthPatternsFlow.py \
  --baseUrl=http://$HOSTNAME:8080/ \
  --fhir_pw=$FHIR_PW \
  --kafka_pw=$KAFKA_PW \
  --addNLPInsights=$ADD_NLP_INSIGHTS \
  --runASCVD=$RUN_ASCVD \
  --deidentifyData=$DEIDENTIFY_DATA \
  --resolveTerminology=$RESOLVE_TERMINOLOGY \
  --releaseName=$RELEASE_NAME \
  --deidConfigName=$DEID_CONFIG_NAME \
  --deidPushToFhir=$DEID_PUSH_TO_FHIR

if [ $? -eq 0 ] ; then
    echo "NiFi canvas setup was successful!"
    echo "starting wait loop so container does not exit"
    sleep infinity
else
    echo "NiFi canvas setup failed"
    exit 1
fi
