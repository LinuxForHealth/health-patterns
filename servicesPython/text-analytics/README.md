NLP Text Analytics
-------------------------------
A flask API for applying NLP-powered text analytics to FHIR resources.  

### Currently supported resource types:
Allergy Intolerance  //TODO fill in overview of how resource is augmented

Immunization

Diagnostic Report

### Running the service
To run the app on its own, from the root directory execute the following:
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
Then run `gradle dockerPush` to push the image 'cdp-text-analytics-service' to your repository.
To deploy, run `kubectl apply -f kubernetes.yml` to deploy both the service and the persistent volume/claim needed to persist configurations.
If deploying on a cluster where the service is already deployed in another namespace, change the name of the persistent volume to something unique to avoid conflicts.


### Using the service
The app currently supports running NLP via two different services, IBM's Annotator for Clinical Data (ACD) and the 
open-source QuickUMLS.  

#### HTTP Endpoints

| Action | Method | Endpoint | Body | Parameters | Returns on Success |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Apply Analytics | `POST` | `/process` | FHIR bundle or resource | | Object annotated with NLP insights |
| Add Config (will not overwrite) | `POST` | `/config/{configName}` | Config (json) | | Status `200` |
| Add Config (will overwrite) | `PUT` | `/config/{configName}` | Config (json) | | Status `200`
| Get Configs | `GET` | `/config` | | | Newline-delimited list of config names |
| Get Config | `GET` | `/config/{configName}` | | | Config named `configName` |
| Delete Config | `DELETE` | `/config/{configName}` | | | Status `200` |
| Set up NLP with specified config | `POST` | `/setup/{configName}` | | | Status `200` |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK </br> Status `500` if errors |

#### Example Resources

##### FHIR bundle:
//todo
##### Config json:
{ "nlpService": "quickUMLS" }
{ "nlpService": "ACD" }