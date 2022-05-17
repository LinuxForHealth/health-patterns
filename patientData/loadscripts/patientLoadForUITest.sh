#!/bin/bash
# Prepare a FHIR Server For patient-browser testing by loading patients (assumes the ingest IVT test env with NLP configured

# This script needs the hostname of the deployment (<namespace-name-in-cluster>.<ingress-subdomain-of-cluster>)

# Set default NLP to 'default' which means quickumls
curl -X POST 'https://'$1'/nlp-insights/config/setDefault?name={default}'
sleep 60
# Load patient(s) for quickumls enrichment
./loadscripts/loadPatientsFromDirectoryAddNLP.sh $1 demo-patients-slim15
sleep 60
# Load the rest of the patients with NLP
./loadscripts/loadPatientsFromDirectoryNoNLP.sh $1 other
sleep 60
./loadscripts/loadPatientsFromDirectoryNoNLP.sh $1 breastcancer
sleep 60
./loadscripts/loadPatientsFromDirectoryNoNLP.sh $1 diabetes
sleep 60

# Set default NLP to ACD
curl -X POST 'https://'$1'/nlp-insights/config/setDefault?name={acd}'
sleep 60
# Load patient(s) for ACD enrichment
./loadscripts/loadPatientsFromDirectoryAddNLP.sh $1 patientforACD
sleep 60
# Set back to default NLP
curl -X POST 'https://'$1'/nlp-insights/config/setDefault?name={acd}'