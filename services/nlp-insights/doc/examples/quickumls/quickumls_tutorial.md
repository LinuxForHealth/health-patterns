# Using nlp-insights with QuickUMLS
QuickUMLS is a service designed for fast, unsupervised concept extraction from medical text. The code base and documentation is located [here](https://github.com/Georgetown-IR-Lab/QuickUMLS#readme). Another great article on the technology can be found [here](https://towardsdatascience.com/doing-almost-as-much-with-much-less-a-case-study-in-biomedical-named-entity-recognition-efa4abe18ed).

The nlp-insights service has been designed to interact with QuickUMLS for detecting medical concepts within FHIR resources.


## Prereqs
* You must have access to a deployed QuickUMLS service to complete this tutorial. Instructions to start a server on your local machine are described [here:](https://github.com/Georgetown-IR-Lab/QuickUMLS#server--client-support)
* You must have a container runtime installed on your machine
* You must have a python 3.9 and pip distribution
* This tutorial uses curl to submit REST requests to the service

## Start the nlp-insights service
If the nlp-insights service has not been started, start the service in a local container by following the instructions [here](../setup/start_nlp_insights.md).

## Configure nlp-insights to use quickumls for NLP
The nlp-insights service must be configured to use QuickUMLS prior to using the service to obtain insights. The steps to configure the service are described [here](./configure_quickumls.md).

## Enrich FHIR resources with additional codings
The nlp-insights service can use QuickUMLS to derive additional coding values in FHIR resources. Learn how [here](./enrich.md)

## Derive new FHIR resources from unstructured content
The nlp-insights service can use QuickUMLS to derive new FHIR resources from clinical notes embedded in other FHIR resources. Learn how [here](./derive_new_resources.md)

## FHIR Integration
 The nlp-insights service is designed to enrich a bundle prior to posting that bundle to a FHIR server. Learn how to to work with derived data that is stored in a FHIR server [here](../fhir_integration/fhir_integration_tutorial.ipynb) You will need a viewer for jupyter-notebooks to view the tutorial.