# Alvearie Health Patterns Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart deploys Alvearie Health Patterns in a Kubernetes cluster.

Alvearie Health Patterns is comprised of multiple components described in more detail [here](README.md), and using this Helm chart you can optionally enable/disable components of that pattern.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+
- PV provisioner support in the underlying infrastructure

**Note:** If you don't have access to a kubernetes cluster, this pattern can also be [deployed to minikube](README_minikube.md).

## Installation

#### Checkout the Code

```
git clone https://github.com/Alvearie/health-patterns.git
cd health-patterns/helm-charts/health-patterns
helm dependency update
```

Note: by changing the directory as shown above, you will be in the right place for future file access.

#### Create a new namespace

Please note that although this is step is optional, it is highly recommended that you create a new namespace in your Kubernetes cluster before installing the pattern.  This will help prevent the various artifacts it will install from mixing with other artifacts that might already be present in your Kubernetes cluster.  To create a new namespace called ```alvearie``` and make it your default for future commands:

```bash
kubectl create namespace alvearie
kubectl config set-context --current --namespace=alvearie
```

**NOTE:** The length of a namespace name must be less than or equal to **20 characters**.  Using a name that is longer than 20 characters will result in a failure to deploy the Nifi pod due to a certificate issue (the error will be visible in the NifiKop log).

### Configure Nifikop

This chart relies on [NifiKop](https://orange-opensource.github.io/nifikop/) to deploy Apache Nifi.  This relies on a one-time setup for your cluster to install the Custom Resource Definitions properly.  See [Getting Started](https://orange-opensource.github.io/nifikop/docs/2_setup/1_getting_started) for instructions on how to setup your cluster.

In addition, using NifiKop requires a NifiKop controller to be deployed in the namespace prior to deploying the Health Patterns Helm chart.  This allows the NifiKop custom resources to be managed correctly, and by deploying separately guarantees the controller remains active when custom resources are deleted, allowing proper clean-up.

To deploy a NifiKop controller to your namespace, run:

```
helm repo add orange-incubator https://orange-kubernetes-charts-incubator.storage.googleapis.com/

helm repo update

helm install nifikop \
    orange-incubator/nifikop \
    --namespace=alvearie \
    --version 0.7.1 \
    --set image.tag=v0.7.1-release \
    --set resources.requests.memory=256Mi \
    --set resources.requests.cpu=250m \
    --set resources.limits.memory=256Mi \
    --set resources.limits.cpu=250m \
    --set namespaces={"alvearie"}
```

### User Authentication - OpenID Connect

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
  hostname: &hostname <<external-hostname>>
```

For example, to deploy in the IBM Cloud environment, we would add

```
ingress:
  enabled: &ingressEnabled true
  class: &ingressClass public-iks-k8s-nginx
  hostname: &hostname <<your-ibm-hostname>>
```


### Storage class
And finally, if you are deploying to a non-IBM cloud, you will need to change the storage class used by Nifi by updating the following parameter:

```
nifi2:
  storageClassName - The storage class you wish to use for persisting Nifi.
```

#### Deployment
The following Helm command will deploy the ingestion pattern.  The entire pipeline will be ready to normalize, validate, enrich, and finally persist FHIR data to a FHIR server.

```
helm install ingestion .
```

After running the command above, you will see notes that give you information about the deployment, in particular, where the important services (e.g. FHIR, Nifi, expose-kafka) have been deployed.

**IMPORTANT NOTE** The release name for the ingestion pipeline must be **ingestion** (see [Advanced topics](#advanced-topics) for additional information)


#### Alternative deployment instructions (insecure)

The instructions listed above are the recommended steps for deploying Health Patterns Ingestion/Enrichment flows.  However, it requires sufficient authority to the target cluster to deploy Custom Resource Definitions and configure an OIDC service.  If these authorities are not attainable it may be necessary to deploy an unsecured, non-authenticating version of Ingestion or Enrichment.  

**NOTE:** Given the significant differences between the Nifikop-based deployment and this, it is not feasible to maintain both approaches targeting current Nifi dataflows. Therefore, using the insecure deployment will result in a snapshot of these flows current as of November 2021, but not updated since.

First, setup deployment parameters:

1) Update your ingress parameters as noted [here](#ingress-parameters).

2) Update values.yaml with the following changes:

```
nifikop:
  disabled: &nifikopDisabled true
  enabled: &nifikopEnabled false
```

**NOTE:** Due to a limitation in Helm, when using the Health Patterns chart with a release name other than the defaults of `ingestion` and `enrich`, you are required to update the corresponding values.yaml file to correspond to the correct release name.  

For Clinical Ingestion, update:

```
nifi:
  extraContainers:
    - name: post-start-setup
      env:
      - name: "RELEASE_NAME"
        value: "ingest"
```

For Clinical Enrichment, update:

```
nifi:
  extraContainers:
    - name: post-start-setup
      env:
      - name: "RELEASE_NAME"
        value: "enrich"

fhir:
  notifications:
    kafka:
      bootstrapServers: "enrich-kafka:9092"
```


3) When deploying the helm chart, you will need to supply the variation.yaml (ingestion/enrichment) indicating which you wish to deploy:

`helm install ingestion . -f clinical_ingestion.yaml`
or
`helm install enrich . -f clinical_enrichment.yaml`


#### Uninstall/delete

To uninstall/delete the <<RELEASE_NAME>> deployment, use:

```
helm delete <<RELEASE_NAME>>
```

Deletion of charts doesn't cascade to deleting associated `PersistedVolume`s and `PersistedVolumeClaims`s.
To delete them:

```bash
kubectl delete pvc -l release=ingestion
kubectl delete pv -l release=ingestion
```

## Using the pattern

After running the previous `helm install` command, you should get a set of instructions on how to access the various components of the chart and using the [Alvearie Clinical Ingestion pattern](../../README.md).


### Optional: Deploy a FHIR UI

Follow the instructions for deploying the [Alvearie Patient Browser App](https://github.com/Alvearie/patient-browser/tree/master/chart#installation) if you need a FHIR UI.

When specifying the FHIR URL (fhirServer parameter) you must use an open server (not requiring authorization).  If you enable the FHIR Proxy Ingress, you can use the corresponding host name.  The proxy allows unauthenticated access to the FHIR server, so will not be enabled by default. To enable it, when deploying the Clinical Ingestion helm chart, include:

```
--set fhir.proxy.enabled=true
```

and

```
--set fhir-deid.proxy.enabled=true
```

## Configuration

Each requirement is configured with the options provided by that Chart.
Please consult the relevant charts for their configuration options.

| Parameter                | Description                                                                                                        | Default   |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------| --------- |
| `kafka.enabled`          | Enable [Kafka](https://github.com/helm/charts/tree/master/incubator/kafka)                                         | `true`    |
| `nifi.enabled`           | Enable [Nifi](https://github.com/cetic/helm-nifi)                                                                  | `true`    |
| `nifi-registry.enabled`  | Enable [Nifi Registry](../nifi-registry)                                                                           | `true`    |
| `fhir.enabled`           | Enable [FHIR](../fhir)                                                                                            | `true`    |
| `zookeeper.enabled`      | Enable [Zookeeper](https://github.com/bitnami/charts/tree/master/bitnami/zookeeper)                                | `true`    |
| `deid.enabled`      | Enable [De-Identification](https://github.com/Alvearie/de-identification)                                | `true`    |
| `ascvd.enabled`      | Enable [ASCVD](https://github.com/Alvearie/health-analytics/tree/main/ascvd)                                | `true`    |

## Monitoring

There is a grafana-based monitoring solution that has been included as part of this chart.  It is disabled by default in the chart, however, it can be enabled by setting the following options to `true` (note that they are currently all set to `false`).

```bash
kafka.metrics.kafka.enabled
kafka.metrics.jmx.enabled
kafka.metrics.serviceMonitor.enabled
kube-prometheus-stack.enabled
```

It is important to note that due to a limitation in grafana that causes multi-install collisions, only one instance of the chart should be installed when the monitoring solution is turned on.

## Bulk Export configuration

It is possible to configure the Fhir server to allow bulk export.  For this to happen, there are a number of prerequisites that must be completed.  Bulk export assumes that the export artifact will be placed in a Cloud Object Store bucket.  You will need to create a bucket and set up service credentials for access.  In addition, you will need to configure a PKCS Trust Store file to include new information for your particular cos endpoint.

### Bucket and Credentials
#### Note that these instructions target IBM Cloud Object Store but other cloud storage will work as well (details will vary)

1. Create a cloud object store resource
1. Create a new bucket for export artifacts within that resource (make a note of the `bucket name` for later)
1. Click on configuration to find the public endpoint and the location (make a note of the `endpoint` and the `location` for later)
1. Click on Service Credentials and choose New Credential. Pick a name and choose writer. Open the new credential (make a note of the `apikey` and the `iam_serviceid_crn` for later)

### Setting up the PKCS Trust Store

In the helm chart, navigate to `clinical-ingestion/helm-charts/alvearie-ingestion/charts/fhir/binaryconfig/` where you will find a file called `fhirTrustStore.p12`.  In order for fhir to communicate with cos you need to update this file with certificate information from your cos endpoint.  Execute the bash command below to get and store the cos certificate relative to your endpoint:

`echo "" | openssl s_client -showcerts -prexit -connect <YOUR ENDPOINT>:443 2> /dev/null | sed -n -e '/BEGIN CERTIFICATE/,/END CERTIFICATE/ p' > out.pem`

where `YOUR ENDPOINT` is the endpoint noted above.  The result is stored in a file called `out.pem`.  Now, we will update the p12 file with this new information.  The following command will take the contents of the `out.pem` file and add them to the `fhirTrustStore.p12` file.

```bash
keytool -importcert -noprompt \
           -keystore fhirTrustStore.p12  -storepass change-password \
           -alias my-host -file out.pem
```

After the update, delete the `out.pem` file from the `binaryconfig` directory.

### Update Chart Configuration to Setup Bulk Export

In the `values.yaml` file for the helm chart, locate the `bulkExportConfig` section under the FHIR Configuration.  Fill in the values using the the information you noted above.

  - `cosBucketName` The bucket name you chose
  - `cosLocation` The region (for example, us-east)
  - `cosEndpointInternal` The cos endpoint from the bucket config
  - `cosApikey` The api key from your service credentials
  - `cosSrvinstid` The srv instance id from your service credentials
  - `batchUserPw` The fhirAdmin user password

Save the file and you are ready to install the chart using the instructions above.

## Contributing

Feel free to contribute by making a [pull request](https://github.com/Alvearie/health-patterns/pull/new/master).

Please review the [Contributing Guide](https://github.com/Alvearie/health-patterns/blob/main/CONTRIBUTING.md) for information on how to get started contributing to the project.

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
