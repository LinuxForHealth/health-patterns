#!/bin/bash

scripts/wait-for-nifi.sh $INTERNAL_HOSTNAME $HTTPS_PORT

scripts/initialize-reporting-task.sh $INTERNAL_HOSTNAME $HTTPS_PORT

if [ "$ADD_CLINICAL_INGESTION" = true ] ; then
python /scripts/loadHealthPatternsFlows.py \
  --baseUrl=https://$INTERNAL_HOSTNAME:$HTTPS_PORT/ \
  --reg=$NIFI_REGISTRY \
  --bucket=Health_Patterns \
  --flowName="Clinical Ingestion"
fi

if [ "$ADD_CLINICAL_ENRICHMENT" = true ] ; then
python /scripts/loadHealthPatternsFlows.py \
  --baseUrl=https://$INTERNAL_HOSTNAME:$HTTPS_PORT/ \
  --reg=$NIFI_REGISTRY \
  --bucket=Health_Patterns \
  --flowName="FHIR Bundle Enrichment" \
  --x=0.0 \
  --y=200.0
fi

python /scripts/startHealthPatternsFlow.py \
  --baseUrl=https://$INTERNAL_HOSTNAME:$HTTPS_PORT/ \
  --fhir_pw=$FHIR_PW \
  --kafka_pw=$KAFKA_PW \
  --addNLPInsights=$ADD_NLP_INSIGHTS \
  --runASCVD=$RUN_ASCVD \
  --deidentifyData=$DEIDENTIFY_DATA \
  --resolveTerminology=$RESOLVE_TERMINOLOGY \
  --releaseName=$RELEASE_NAME \
  --deidConfigName=$DEID_CONFIG_NAME \
  --deidPushToFhir=$DEID_PUSH_TO_FHIR \
  --runFHIRDataQuality=$RUN_FHIR_DATA_QUALITY
  

if [ $? -eq 0 ] ; then
    echo "NiFi canvas setup was successful!"
    echo "starting wait loop so container does not exit"
    sleep infinity
else
    echo "NiFi canvas setup failed"
    exit 1
fi
