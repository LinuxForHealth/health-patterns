# Ingestion

# Table of Contents
- [Welcome to health-patterns](#ingestion-overview)
- [How to deploy](#how-to-deploy)
- [Using the pattern](#using-the-pattern)
- [Options](#options)
- [Advanced topics](#advanced-topics)

## Welcome to health-patterns

health-patterns is a place to find cloud reference implementations for the overall Alvearie architecture (https://alvearie.io/architecture) that incorporate best practices using open technologies. Each pattern incorporates parts of [Alvearie](https://alvearie.io/) along with other open technologies that can be used to start building your own healthcare solutions using a common base of proven technology.


#### Ingestion Pattern Overview

The **Ingestion** health pattern (which can optionally incorporate the [Enrichment](../enrich/README.md) pattern) is a flexible approach to processing healthcare data and storing it into a FHIR server.
At the most basic level, the Ingestion pattern will read HL7 or FHIR data from a [Kafka](https://kafka.apache.org) topic, use [NiFi](https://github.com/apache/nifi) to orchestrate any desired conversion or validation, and then store the results into a [FHIR Server](https://github.com/ibm/fhir).  In addition, it is
cloud agnostic, meaning it has been run on many different platforms including IBM Cloud, AWS, Azure, Google.

Within the [NiFi](https://github.com/apache/nifi) canvas, the Ingestion health pattern will:
  - Convert [HL7 to FHIR using technology from LinuxForHealth](https://github.com/LinuxForHealth/hl7v2-fhir-converter)
  - Validate the FHIR data without storing it in the FHIR Server
  - Put the converted/validated data on a Kafka topic for processing by the _Enrichment_ pattern
  - Store the FHIR bundle into the [FHIR Server](https://github.com/ibm/fhir)
  - Handle errors:
      - In case of errors within the bundle, individual resources are retried
      - Errors are reported back to the data integrator via a kafka topic


## How to deploy

#### Prerequisites

These instructions assume that you have the following resources, tools, and configurations:

- Kubernetes cluster 1.10+
- Helm 3.0.0+
- Access to ```kubectl```, the Kubernetes command line tool
- PV provisioner support in the underlying infrastructure

**Note:** If you don't have access to a kubernetes cluster, this pattern can also be [deployed to minikube](../helm-charts/health-patterns/README_minikube.md).


#### Check out the code

```
git clone https://github.com/LinuxForHealth/health-patterns.git
cd health-patterns/helm-charts/health-patterns
helm dependency update
```

Note: by changing the directory as shown above, you will be in the right place for future file access.

#### Create a new namespace

Please note that although this step is optional, it is highly recommended that you create a new namespace in your Kubernetes cluster before installing the pattern.  This will help prevent the various artifacts it will install from mixing with other artifacts that might already be present in your Kubernetes cluster.  To create a new namespace called ```your-namespace``` and make it your default for future commands:

```bash
kubectl create namespace your-namespace
kubectl config set-context --current --namespace=your-namespace
```

**NOTE:** The length of a namespace name must be less than or equal to **20 characters**.  Using a name that is longer than 20 characters will result in a failure to deploy the Nifi pod due to a certificate issue (the error will be visible in the NifiKop log).

#### Update the internalHostName

The internal host name used to communicate with nifi requires that you substitute your custom namespace (created above) into the value shown below.  For example, if you created a namespace called `your-namespace` then the update in the `values.yaml` file would be

```
# Update "alvearie.svc" to "<your namespace>.svc"
internalHostName: &internalHostName alvearie-nifi-0.alvearie-nifi-headless.your-namespace.svc.cluster.local
```

#### Ingress parameters

We recommend exposing the services in this chart via ingress.  This provides the most robust and secure approach.  If you choose to expose services via port-forwarding, load-balancer, or other options, please be careful to ensure proper security.

Ingress requires a specific ingress class to be used.  Different cloud providers rely on different ingress classes, so choose the one that matches your cloud provider.  For example, some possible choices might be:
  - IBM: public-iks-k8s-nginx
  - Azure: addon-http-application-routing
  - AWS: nginx

You will also need to provide a hostname for your ingress.  What this is and how it gets created will be unique to your cloud infrastructure.  

Once you know these values, use both of them to update the `ingress` section of the file ```helm-charts/health-patterns/values.yaml```  as shown below. Note that the ingress class currently defaults to `public-iks-k8s-nginx` so if that is your choice, no update to the ingress class is needed.  However, the ingress hostname **MUST** be updated.

```
ingress:
  enabled: &ingressEnabled true
  class: &ingressClass public-iks-k8s-nginx
  hostname: &hostname replace-me
```

For example, to deploy in the IBM Cloud environment, we would add

```
ingress:
  enabled: &ingressEnabled true
  class: &ingressClass public-iks-k8s-nginx
  hostname: &hostname <<your-ibm-hostname>>
```

#### Update FHIR server url for patient-browser UI

By default, a simple FHIR UI called `patient-browser` will be deployed.  In order for the UI to connect to the FHIR server, you need to provide the url in the `values.yaml` patient-browser configuration as shown below.

```
patient-browser:
  enabled: true
  ingress:
    enabled: true
    class: *ingressClass
    hostname: *hostname
  fhirServer: <<provide FHIRserver url here>>
```

For example, if you are deploying your FHIR server using this deployment with ingress, your url will use the `hostname` above as follows:

`https://<<hostname>>/fhir`

If you wish to disable the patient-browser, set the `enabled` value to `false`.


#### Deployment
The following Helm command will deploy the ingestion pattern.  The entire pipeline will be ready to normalize, validate, enrich, and finally persist FHIR data to a FHIR server.

```
helm install ingestion .
```

After running the command above, you will see notes that give you information about the deployment, in particular, where the important services (e.g. FHIR, Nifi, expose-kafka) have been deployed.

**IMPORTANT NOTE** The release name for the ingestion pipeline must be **ingestion** (see [Advanced topics](#advanced-topics) for additional information)


#### Uninstall/delete

To uninstall/delete the deployment, use:

```
helm delete ingestion
```

Deletion of charts doesn't cascade to deleting associated `PersistedVolume`s and `PersistedVolumeClaims`s.
To delete them:

```bash
kubectl delete pvc -l release=ingestion
kubectl delete pv -l release=ingestion
```

## Using the pattern

By default, there are three important external services exposed by the Ingestion Pattern: NiFi, Kafka via expose-kafka, and FHIR. Again, as mentioned above, the urls for those services are provided in the post-deployment information.  Let’s go through them one by one and discuss their corresponding functionality.

#### [NiFi](https://github.com/apache/nifi)
Let’s start with the alvearie-nifi service: `https://<<external-hostname>>/nifi`.  Once you login using the `username` / `password` defined in the nifi section of the `values.yaml` (default is **alvearie** / **wats0nHealth**) you will see the Nifi canvas.

```
singleUser:
  username: &nifiUser alvearie
  password: &nifiPassword wats0nHealth # Must to have at least 12 characters
```

The NiFi canvas will show a pre-configured main process group called **health-patterns-dataflow** which is the entry point to the Ingestion Pattern’s NiFi components. From here you can add, remove, or modify ingestion processing elements, add new inputs or outputs, change the URLs to some of the other services, update parameter contexts, etc. You will also see a second process group called **health-patterns-enrich-dataflow** that provides data enrichment functionality to the pipeline.  This is currently configured to be included automatically by the Clinical Ingestion installation but could also be deployed stand-alone by providing the appropriate helm variation [[see Enrichment]](../enrich/README.md).

#### [Kafka](https://kafka.apache.org)
The Ingestion Pattern includes a Kafka broker that can be used to feed clinical data into the pattern

The entry point into the clinical ingestion flow is a Kakfa topic called `ingest.topic.in`.  When we place data (either FHIR or HL7) onto that topic, it will automatically be consumed and sent through the rest of the flow.  In order to place data on a kafka topic, we will use the [expose-kafka](../services/expose-kafka/README.md) service that was deployed as part of the install (the url is included in the deployment information).  This can be done with Postman, curl, or some other http tool.  

For example, the curl command below will place the contents of the file `testpatient.json` (a patient FHIR bundle) on the `ingest.topic.in` kafka topic (via the query parameter `topic`).  At that point, the ingestion flow is listening for messages and will immediately take the new bundle and begin to process it.  You should see one bundle appear in the “success” state at the end of the flow.  Note that the request will return immediately even though the data may not be completely through the flow.

```
curl -X POST https://<<external-hostname>>/expose-kafka?topic=ingest.topic.in  \
   --header "Content-Type: text/plain" \
   --data-binary  @/pathtofile/testpatient.json
```


#### [FHIR](https://github.com/ibm/fhir)
After posting the patient through Kafka, if no errors have occurred, the patient will be persisted in the FHIR server. From the list of services provided after the deployment, grab the deployment base url for the FHIR server. You can then query the list of FHIR resources using your browser or an HTTP client. For instance, for querying patients you would do the following (using default credentials: _fhiruser_/_integrati0n_):

```
https://<<external-hostname>>/fhir/Patient?_format=json
```


## Options

#### Enrichment options

By default, the Ingestion pattern will also deploy the Enrichment pipeline.  It is possible to control the behavior of the enrichment steps via request headers.  For more information about these headers and examples for their use, see the [Enrichment Pattern ](../enrich/README.md) documentation.



## Advanced topics


### FHIR Server configuration
This pattern relies on a FHIR server for data persistence and retrieval.  It provides a basic configuration for the server but there are a number of advanced options that can be added or modified (for example, which backend database is used-Derby, DB2, PostgreSQL, etc.).  We suggest you consult the [FHIR documentation](https://github.com/ibm/fhir) for those options.

### Synthetic data via Synthea

  If you don't have data, you can create some synthetic clinical data to push. Synthetic patient data can be generated using the Synthea Patient Generator.  Download Synthea and run the following command (for more information on Synthea visit their [Github page](https://github.com/synthetichealth/synthea)):

  `java -jar synthea-with-dependencies.jar -p 10`

  This command will have created FHIR bundles for 10 patients with their clinical history and their corresponding medical providers.


### Advanced configuration for Helm Chart

When deploying this chart, there are many configuration parameters specified in the `values.yaml` file.  These can all be overridden based on individual preferences.  To do so, you can create a secondary YAML file containing your changes and specify it to the `helm install` command to override default configuration.

`helm install ingestion . -f value_overrides.yaml`

### Kafka topics for the pipeline

To submit data to the Ingestion pipeline, it needs to be posted to the configured Kafka topic. The Kafka topic to target depends on the pipeline you are running and the Nifi configuration. For example, in the Ingestion pattern the topic is called `ingest.topic.in` as was shown above using the query parameter `topic`.  This can be found and/or updated in the Nifi parameter context `ingestion-parameter-context` under the parameter `ingest.topic.in`.

Additional Kafka Topics

There are additional Kafka topics defined in the ingestion flow (`ingest.topic.out` and `ingest.topic.failure`).  These can be seen in the Nifi `ingestion-parameter-context` and can be used via an `expose-kafka` call similar to that shown above.  

The following example request sends two additional query parameters (`response_topic` and `failure_topic`) and the request will monitor both topics for results.  This so-called `blocking` flow will wait to return until there are results on the `response_topic` or until a timeout occurs.

```
curl -X POST https://<<external-hostname>>/expose-kafka?topic=ingest.topic.in&response_topic=ingest.topic.out&failure_topic=ingest.topic.failure  \
   --header "Content-Type: text/plain" \
   --data-binary  @/pathtofile/testpatient.json
```

Query parameters:
- `topic`: The name of the kafka topic where data will enter the flow. (required)
- `response_topic`: The response topic you wish to listen on.  The API won't return until your result is complete (or a timeout is reached).  This topic is set in the Nifi parameter context `ingestion-parameter-context` under `ingest.topic.out` and defaults to topic `ingest.topic.out`.

- `failure_topic`: The topic used to return errors occurring during the pipeline.  If `response_topic` is not set, no errors will be reported, but when both topics are specified, the request will monitor both topics for results.  This topic is set in the Nifi parameter context `ingestion-parameter-context` under `ingest.topic.failure` and defaults to topic `ingest.topic.failure`.

One other topic of note is specified by `data.quality.topic` in the Nifi parameter context `ingestion-parameter-context`.  This topic will contain the results of FHIR Data Quality checks done on each request (when configured).  You can view this topic using Expose-Kafka API's.


### Changing the release name

The `values.yaml` file contains a  `releaseName` variable that can be set to values other than the default of `ingestion`.

```
releaseName: &releaseName <<your new release name>>
```

If you choose to change the default then be sure to also use the new release name in the helm install command.

```
helm install <<your new release name>> .
```

### Deploying Nifi using Nifikop for security

The instructions listed above are the recommended steps for deploying the Health Patterns Ingestion flow. It is possible to deploy a more secure and authenticated version of the ingestion flow by using **NifiKop**.  However, it requires sufficient authority to the target cluster to deploy Custom Resource Definitions and configure an OIDC service.

**NOTE:** Given the significant differences between the Nifikop-based deployment and the default deployment, it is not feasible to maintain both approaches targeting current Nifi dataflows. Therefore, using the NifiKop deployment will result in a snapshot of these flows current as of January 13, 2022 but not updated since.

This NifiKop based configuration relies on [NifiKop](https://orange-opensource.github.io/nifikop/) to deploy Apache Nifi.  This requires a one-time setup for your cluster to install the Custom Resource Definitions properly.  See [Getting Started](https://orange-opensource.github.io/nifikop/docs/2_setup/1_getting_started) for instructions on how to setup your cluster.

In addition, using NifiKop requires a NifiKop controller to be deployed in the namespace prior to deploying the Health Patterns Helm chart.  This allows the NifiKop custom resources to be managed correctly, and by deploying separately guarantees the controller remains active when custom resources are deleted, allowing proper clean-up.

To deploy a NifiKop controller to your namespace, run the following three steps:

```
helm repo add orange-incubator https://orange-kubernetes-charts-incubator.storage.googleapis.com/

helm repo update

helm install nifikop \
    orange-incubator/nifikop \
    --namespace=<<your namespace>> \
    --version 0.7.1 \
    --set image.tag=v0.7.1-release \
    --set resources.requests.memory=256Mi \
    --set resources.requests.cpu=250m \
    --set resources.limits.memory=256Mi \
    --set resources.limits.cpu=250m \
    --set namespaces={"<<your-namespace>>"}
```

#### User Authentication - OpenID Connect

Nifikop configures a secure Nifi instance which relies on [OIDC](https://openid.net/connect/) to authenticate user access.  This requires you to separately setup an OIDC service and supply the correct configuration information to this Helm chart.  For example, [App Id](https://www.ibm.com/cloud/app-id) is available for IBM Cloud instances.

Once configured, update the values.yaml to populate the following parameters.

```
oidc:
  users - a list of identity/name values representing the user(s) you want configured for access.  The identity must match the login identity from your OIDC endpoint, and the name should be lower-case and contain no spaces.
  discovery:
    url - The URL of your OIDC discovery service
  client:
    id - The client ID of your OIDC discovery service
    secret - The client secret of your OIDC discovery service
```

**NOTE:** You will also need to register your OIDC callback (`https://<<external-hostname>>:443/nifi-api/access/oidc/callback`) with your OIDC service.  For IBM App ID, this is located under Manage Authentication->Authentication Settings->Add Web Redirect URLs.


#### Storage class
And finally, if you are deploying to a non-IBM cloud, you will need to change the storage class used by Nifi by updating the following parameter:

```
nifi2:
  storageClassName - The storage class you wish to use for persisting Nifi.
```


To complete the nifikop configuration, set up the rest of the deployment parameters as described previously-most importantly:

1. Update your ingress parameters as noted [here](#ingress-parameters).

2. Update `values.yaml` to enable NifiKop

```
nifikop:
  disabled: &nifikopDisabled false
  enabled: &nifikopEnabled true
```


Finally, to start the actual deploy run:

`helm install ingestion . `
