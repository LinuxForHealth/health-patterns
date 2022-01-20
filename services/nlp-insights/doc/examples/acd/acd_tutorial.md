# Using nlp-insights with IBM Watson Annotator for Clinical Data

The IBM Watson Annotator for Clinical Data (ACD) service is a medical domain NLP service featuring a variety of annotators. More information is available [here](https://www.ibm.com/cloud/watson-annotator-for-clinical-data).

The nlp-insights service has been designed to leverage ACD capabilities NLP when deriving new FHIR resources, or enriching an existing resource.


## Prereqs
You must have access to an ACD service to complete this tutorial. You can view plans (including a free trial plan) [here](https://cloud.ibm.com/catalog/services/annotator-for-clinical-data).


## Start the nlp-insights service
If the nlp-insights service has not been started, start the service in a local container by following the instructions [here](../setup/start_nlp_insights.md).

## Configure nlp-insights to use ACD for NLP
The nlp-insights service must be configured to use ACD prior to using the service to obtain insights. The steps to configure the service are described [here](./configure_acd.md).

## Enrich FHIR resources with additional codings
The nlp-insights service can use ACD to derive additional coding values in FHIR resources. Learn how [here](./enrich.md)

## Derive new FHIR resources from unstructured content
The nlp-insights service can use ACD to derive new FHIR resources from clinical notes embedded in other FHIR resources. Learn how [here](./derive_new_resources.md)

## Context awareness
When nlp-insights is configured to use ACD, the nlp-insights service will take advantage of ACD attributes to determine the context of concepts. This avoids creating resources for the patient that are not correct. See the details [here](./context_awareness.md)

## FHIR Integration
 The nlp-insights service is designed to enrich a bundle prior to posting that bundle to a FHIR server. Learn how to to work with derived data that is stored in a FHIR server [here](../fhir_integration/fhir_integration_tutorial.ipynb) You will need a viewer for jupyter-notebooks to view the tutorial.