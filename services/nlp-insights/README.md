NLP Text Analytics
-------------------------------
A flask API for applying NLP-powered text analytics to FHIR resources.  

### Currently supported resource types:

Allergy Intolerance --> Adds an extension to the resource containing diseases/syndromes, symptoms, and pathologic
functions and their codes inferred from the resource.

Immunization --> Adds an extension to the resource containing immunizations/immunologic factors and their codes inferred from the resource.

Diagnostic Report --> Creates Condition and/or Medication Statement resources generated from the diagnostic report

### Running the service
To run the app on its own, fill in `text_analytics/acd/acd_config.ini` and `text_analytics/quickUMLS/quickumls_config.ini` with your config information for each service.

Then from the root directory execute the following:
```bash
export FLASK_APP=text_analytics/app.py
gradle clean build
source build/venv/bin/activate
pip install .
flask run
```

#### Docker:
To build the image locally, run `gradle docker`

Then to run on localhost:5000, run `gradle dockerRun`

To push the docker image and deploy on a kubernetes cluster, first replace the field `<replace with docker user id>` with your docker id
in both `kubernetes.yml` and `gradle.properties`
Then run `gradle dockerPush` to push the image 'nlp-insights' to your repository.
To deploy, run `kubectl apply -f kubernetes.yml` to deploy both the service and the persistent volume/claim needed to persist configurations.
If deploying on a cluster where the service is already deployed in another namespace, change the name of the persistent volume to something unique to avoid conflicts.


### Using the service
The app currently supports running two different NLP engine types: IBM's Annotator for Clinical Data (ACD) and the
open-source QuickUMLS.  It is possible to configure as many different instances of these two engines as needed with different configuration details.  Configuation jsons require a `name`, an `nlpServiceType` (either `acd` or `quickumls`), and config details specific to that type.
For quickumls, an `endpoint` is required. For ACD, an `endpoint`, an `apikey`, and a `flow`.

#### HTTP Endpoints

| Action | Method | Endpoint | Body | Returns on Success |
|:------:|:------:|:---------|:----:|:-------:|
| Apply NLP | `POST` | `/discoverInsights` | FHIR bundle or resource | Object annotated with NLP insights |
| Get All Configs | `GET` | `/all_configs` | | Newline-delimited list of config names |
| Add Named Config  | `PUT/POST` | `/config/definition` | Config (json) contains `name` | Status `200`
| Get Current Active Config | `GET` | `/config` | | Currently active config |
| Get Config Details | `GET` | `/config/{configName}` | | Config named `configName` |
| Delete Config | `DELETE` | `/config/{configName}` | | Status `200` |
| Make config active | `POST/PUT` | `/config/{configName}` | | Status `200` |
| Get all active overrides | `GET` | `/config/resource` | | dictionary-Status `200` |
| Get the active override for a resource | `GET` | `/config/resource/{resource}` | | String-Status `200` |
| Add resource override | `POST/PUT` | `/config/resource/{resourcetype}/{configName}` | | Status `200` |
| Delete a resource override | `DELETE` | `/config/resource/{resourcetype}` | | Status `200` |
| Delete all resource overrides | `DELETE` | `/config/resource` | | Status `200` |

#### Example Resources

Example json FHIR that can be processed by the service can be found in text_analytics/test/resources

##### Example config jsons:
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
