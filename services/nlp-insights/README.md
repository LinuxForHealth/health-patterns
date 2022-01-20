# NLP Insights
A Rest service for updating bundles of FHIR resources with discovered insights.
The service is implemented as a Flask API within a docker container.

## Purpose
The primary purpose of the discover insights API is to accept a bundle of FHIR resources and to return an updated bundle that includes discovered insights.
* Resources in the bundle may have been enriched by adding additional codes. 
  - For example an AllergyIntolerance resource for a peanut allergy might have UMLS code C0559470 or SNOMED-CT code 91935009 added to it.
* New resources may have been derived from unstructured text (such as clinical notes) contained within the bundle's resources. 
  - For example a DiagnosticReport that says *the patient had a myocardial infarction* might result in a derived Condition resource being added to the bundle.


## Supported NLP Engines
The nlp-insights service requires an NLP engine service to perform NLP related tasks. We support two NLP services.

* IBM's [Annotator for Clinical Data (ACD)](https://www.ibm.com/cloud/watson-annotator-for-clinical-data) and 
* Open-source [QuickUMLS](https://github.com/Georgetown-IR-Lab/QuickUMLS)


## Quick Start
Our tutorials describe how to setup and configure nlp-insights with a supported NLP service. They also provide extensive description of how resources are derived and enriched:

* [Tutorial for using the nlp-insights service with QuickUMLS](./doc/examples/quickumls/quickumls_tutorial.md)
* [Tutorial for using the nlp-insights service with ACD](./doc/examples/acd/acd_tutorial.md)


## Running the service locally
The docker image for the container has been published, and you can pull it from [here](https://hub.docker.com/r/alvearie/nlp-insights).

Developers that have cloned the repo should follow the instructions for starting the service that are documented [here](./doc/examples/setup/start_nlp_insights.md).

Although discouraged, it is possible to [run the service outside of a docker container](./doc/developer/run_service_no_docker.md).

## Kubernetes
The nlp-insights service is designed to be part of a larger health-patterns ingestion and enrichment pipeline. Helm charts are included so that the service can be deployed to kubernetes. The deployed service can then be integrated into a pipeline.

More details on deployment and configuration in a k8s environment are discussed [here](./doc/developer/kubernetes.md)

## HTTP Endpoints
The HTTP APIs for the service are described [here](./doc/developer/http_endpoints.md).
These APIs allow you to:

* Define the connection to the NLP engine service(s),
* Select the default NLP engine that will be used for insight discovery
* Discover insights
* Override the default engine and use a different NLP engine for one or more resource types

## Build
We use gradle for all build and test related tasks. The important features are documented [here](./doc/developer/gradle_tasks.md).

## Contributing
We welcome contributions! Please look at our [contributing guide](./doc/developer/CONTRIBUTING.md) for details on how to begin.


## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 