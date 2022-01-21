# Kubernetes
The nlp-insights service comes with helm charts so that it can be deployed to a k8s environment.

## Deploy the docker image to a kubernetes cluster
These instructions assume that the developer has built a new image and wants to deploy it. However you can also use an image already published, and then it would not be necessary to push a new image to the cloud's container registry.

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

## Additonal information
Additional information can be found in the [README](../../chart/README.md) for the helm charts.

## Configuring the server at deploy time

It is possible to provide an initial (deploy time) named configuration for quickulms and/or acd. This is especially important in a k8s environment, as the service may scale up or down transparently to the user.


This is done by modifying the `values.yaml` file before deployment.  In the nlp-insights chart, the following configuration values are defined:

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