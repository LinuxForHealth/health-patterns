# NLP Insights
A Rest service for discovering insights within FHIR resources.
The service is implemented as a Flask API within a docker container.

## Purpose
The primary purpose of the discover insights API is to accept a bundle of FHIR resources and to return a bundle that contains:
* Resources from the input bundle that have been enriched with additional codes.
* New resources that have been derived from resources in the input bundle


## Resources that are enriched
Existing codes and text are used to derive additional codes for these resource elements:

* Allergy Intolerance
    * AllergyIntolerance.code    
* Condition
    * Condition.code
    
## New resources that are derived from input resources
The service will derive the following FHIR resources from unstructured text:
* MedicationStatement
* Condition

The source text used to derive these new resources is found in the following resource elements:

* DiagnosticReport
    * DiagnosticReport.presentedForm[].data
* DocumentReference
    * DocumentReference.content[].attachment.data
    



## Quick Start
See our quick start guides:
* [Tutorial for using the nlp-insights service with QuickUMLS](./doc/examples/quickumls/quickumls_tutorial.md)
* [Tutorial for using the nlp-insights service with ACD](./doc/examples/acd/acd_tutorial.md)

# Running the service
It is recommended that the service be deployed as a docker container, however you can run it outside of docker if necessary.

We use gradle as our build framework. It is recommended that you use the wrapper that is included in this git repo for build related activities. If you are using windows, use `gradlew.bat` instead of `gradlew`, `gradlew` is used in these directions.

A prerequisite to these directions is python 3.9 and pip. Docker builds will also require a container runtime.

These instructions assume that build properties are set via the command line, however you can set 
defaults for them by modifying `gradle.properties`.

## Running the service outside of a docker container
1. Build and install nlp-insights to a virtual environment  
    `./gradlew install`
   
1. Switch to the [virtual env](https://docs.python.org/3/library/venv.html) where nlp-insights is installed  
   `source ./build/venv/bin/activate`  
   
1. Set the FLASK_APP environment variable to the installed package  
    `export FLASK_APP=nlp_insights.app`
    
1. Start the service (5000 is the default port, however this value can be changed to suit your needs)  
   `python -m flask run --port=5000`

## Running the service locally as a docker container
**Start the container**  
    `./gradlew dockerRun -PdockerUser=<your_user_id> -PdockerLocalPort=<port>`  

The server is now running on the selected port.
If you omit the dockerLocalPort property, 5000 is the default port.  
The dockerRun task will also perform the following dependent build tasks:  
* nlp-insights will be built and installed to the virtual environment
* the docker image will be built
* unit tests will run
    
### Other useful commands for locally working with containers:
1. Stop a running nlp-insights container  
    `./gradlew dockerStop -PdockerUser=<your_user_id> -PdockerLocalPort=<port>`
1. Remove a container from your local repo  
    `./gradlew dockerRemoveContainer -PdockerUser=<your_user_id> -PdockerLocalPort=<port>`
    
## Deploy the docker image to a kubernetes cluster
1. Log into your cloud provider and container registry. The commands to do this depend on your cloud provider.
1. Push the docker image to the remote repository
    `./gradlew dockerPush -PdockerUser=<docker_user_id>`
1. Install the helm charts (The version that was used to tag the docker image is defined in gradle.properties)  
   `helm install nlp-insights chart --set image.repository=<docker_user_id>/nlp-insights --set image.tag=<version>`  
1. Wait for the pod to start running
    `kubectl get pods`
    (look for "nlp-insights-*")
1. Connect to the pod's port 5000
    `kubectl port-forward nlp-insights-xxxxxx-xxxx <local-port>:5000`
    
You can now connect to the service via localhost:<local-port>

Be aware that some cloud providers may require additional configuration in order for the deployment to work.
For example you may need to create a pull secret. Consult your provider's documentation for details.


# Using the service
The app currently supports running two different NLP engine types: 
* [IBM's Annotator for Clinical Data (ACD)](https://www.ibm.com/cloud/watson-annotator-for-clinical-data) and 
* [open-source QuickUMLS](https://github.com/Georgetown-IR-Lab/QuickUMLS)

It is possible to configure as many different instances of these two engines as needed with different configuration details.  Configuation jsons require a `name`, an `nlpServiceType` (either `acd` or `quickumls`), and config details specific to that type.
For quickumls, an `endpoint` is required. For ACD, an `endpoint`, an `apikey`, and a `flow`.

## HTTP Endpoints

| Action | Method | Endpoint | Body | Returns on Success |
|:------:|:------:|:---------|:----:|:-------:|
| Get All Configs | `GET` | `/all_configs` | | Newline-delimited list of config names |
| Add Named Config  | `PUT/POST` | `/config/definition` | Config (json) contains `name` | Status `200`
| Get Current Default Config | `GET` | `/config` | | Current default `configName` |
| Get Config Details | `GET` | `/config/{configName}` | | Config details named `configName` |
| Delete Config | `DELETE` | `/config/{configName}` | | Status `200` |
| Make Config default | `POST/PUT` | `/config/setDefault?name={configName}` | | Status `200` |
| Clear default config | `POST/PUT` | `/config/clearDefault` | | Status `200` |
| Apply NLP | `POST` | `/discoverInsights` | FHIR bundle or resource | Object annotated with NLP insights |
| Get all active overrides | `GET` | `/config/resource` | | dictionary-Status `200` |
| Get the active override for a resource | `GET` | `/config/resource/{resource}` | | `configName`-Status `200` |
| Add resource override | `POST/PUT` | `/config/resource/{resourcetype}/{configName}` | | Status `200` |
| Delete a resource override | `DELETE` | `/config/resource/{resourcetype}` | | Status `200` |
| Delete all resource overrides | `DELETE` | `/config/resource` | | Status `200` |
## Configuring at deploy time

It is possible to provide an initial (deploy time) named configuration for quickulms and/or acd.  This is done by modifying the `values.yaml` file before deployment.  In the nlp-insights chart, the following configuration values are defined:

```
nlpservice:
  quickumls:
    enableconfig: false
    name:
    endpoint:
  acd:
    enableconfig: false
    name:
    endpoint:
    apikey:
    flow:
  default:
  ```

By setting the appropriate `enableconfig` flag to true and providing the `name` of the config as well as the details (dependent on the type of the nlp engine), an initial named configuration will be created.  In addition, the configuration can be made the default by setting the `default` value to one of the previously defined names.


### Example config jsons:
```
{
  "name": "quickconfig1",
  "nlpServiceType": "quickumls",
  "config": {
    "endpoint": "https://quickumlsEndpointURL/match"
  }
}
```

```
{
  "name": "acdconfig1",
  "nlpServiceType": "acd",
  "config": {
    "apikey": "apikeyxxxxxxxxx",
    "endpoint": "https://acdEndpointURL/api",
    "flow": "acd_standard_flow"
  }
}
```
# Coding style guidlines
This project makes use of several coding conventions and tools.


## Formatting
The project is formatted using [Black](https://black.readthedocs.io/en/stable/)


## Unit tests
Unit tests and Doc tests are part of the build process  
`./gradlew test`


## Static code checking
The project uses a combination of flake8, pylint, and mypy to detect static code problems. The configuration is defined in `setup.cfg`. These checks can be run as a build task (this will also run unit tests).  
`./gradlew checkSource`
