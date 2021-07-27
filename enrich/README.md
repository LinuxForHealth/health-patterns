# Enrichment

# Table of Contents
- [Welcome to health-patterns](#enrich-overview)
- [How to deploy](#how-to-deploy)
- [Using the pattern](#using-the-pattern)
- [Options](#options)
- [Advanced topics](#advanced-topics)

## Welcome to health-patterns

health-patterns is a place to find cloud reference implementations for the overall Alvearie architecture (https://alvearie.io/architecture) that incorporate best practices using open technologies. Each pattern incorporates parts of [Alvearie](https://alvearie.io/) along with other open technologies that can be used to start building your own healthcare solutions using a common base of proven technology.


#### Enrichment Pattern Overview

The **Enrichment** health pattern is a reference implementation of a clinical data enrichment process. It allows medical data to be enriched using various components, such as de-identification, terminology normalization, and the [ASCVD](https://github.com/Alvearie/health-analytics/tree/main/ascvd) analytic evaluation.

The Enrichment Flow is designed to read medical data (in FHIR format) from a configured [Kafka](https://kafka.apache.org) topic. As the data is processed, any errors that are detected are logged and posted to target kafka topics (if configured). Once complete, the updated FHIR data is posted back to a Kafka topic for further use.

The current flow is designed to operate on FHIR resources only.  Currently, for any FHIR data that enters the pipeline, we support the following enrichment steps:

  - FHIR Terminology Service - This step will update the clinical data by adding/updating values to adhere to the terminology service configuration. The configuration mapping rules are currently static and can be found [here](https://github.com/Alvearie/health-patterns/tree/main/services/term-services-prep/src/main/resources/defaultMappings)

  - [De-Identification](https://github.com/Alvearie/de-identification) Service - This step will de-identify the clinical data flowing through the pipeline and store the de-identified version in a separate FHIR server. The de-identification rules are currently static and can be found here.

  - [Million Hearts ASCVD Model](https://github.com/Alvearie/health-analytics/tree/main/ascvd): This step will calculate a ten-year risk of cardiovascular disease using the Million Hearts ASCVD Model.

## How to deploy
Note: Although the Enrichment pattern can be deployed on its own by following these steps, it will also be deployed as part of the default Ingestion pattern deployment [see Ingestion](../ingest/README.md).

#### Prerequisites

These instructions assume that you have the following resources, tools, and configurations:

- Kubernetes cluster 1.10+
- Helm 3.0.0+
- Access to ```kubectl```, the Kubernetes command line tool
- PV provisioner support in the underlying infrastructure

#### Check out the code

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

#### Ingress parameters

We recommend exposing the services in this chart via ingress.  This provides the most robust and secure approach.  If you choose to expose services via port-forwarding, load-balancer, or other options, please be careful to ensure proper security.

In order to deploy via ingress, you will need to identify your ingress subdomain as defined by the ingress controller and cloud infrastructure. This is unique to the cloud environment you are using.  Instructions can be found [here](README_INGRESS_SUBDOMAIN.md) on how to identify your ingress subdomain.

Ingress also requires a specific ingress class to be used.  Different cloud providers rely on different ingress classes, so choose the one that matches your cloud provider.  For example,
  - IBM: public-iks-k8s-nginx
  - Azure: addon-http-application-routing
  - AWS: nginx

Once you know these values, use both of them to update and save the ```ingress_values.yaml``` file.

#### Deployment
The following Helm command will deploy the enrichment pattern.  The enrichment pipeline will be ready to accept FHIR data and run it through a series of steps producing a possibly updated FHIR bundle with resources that have been added or modified by the enrichment process.
```
helm install enrich .  -f ingress_values.yaml  -f clinical_enrichment.yaml
```
After running the command above, you will see notes that give you information about the deployment, in particular, where the important services (e.g. Nifi, expose-kafka) have been deployed.

**IMPORTANT NOTE** The release name for the enrichment pipeline must be **enrich** (see [Advanced topics](#advanced-topics) for additional information)


#### Uninstall/delete

To uninstall/delete the deployment, use:
```
helm delete enrich
```

## Using the pattern

By default, there are two important external services exposed by the Alvearie Enrichment Pattern: NiFi and Kafka via expose-kafka. Again, as mentioned above, the urls for those services are provided in the post-deployment information.  Let’s go through them one by one and discuss their corresponding functionality.

#### [NiFi](https://github.com/apache/nifi)
Let’s start with the alvearie-nifi service: `https://<<nifi-external-url>>/nifi`.
The NiFi canvas will show a pre-configured main process group called **Enrich FHIR Data** which is the entry point to the Enrichment Pattern’s NiFi components. From here you can add, remove, or modify ingestion processing elements, add new inputs or outputs, change the URLs to some of the other services, update parameter contexts, etc.

#### [Kafka](https://kafka.apache.org)
The Enrichment Pattern includes a Kafka broker that can be used to feed clinical data into the pattern

The entry point into the enrichment flow is a Kakfa topic called `patients.updated.out`.  When we place data onto that topic, it will automatically be consumed and sent through the rest of the flow.  In order to place data on a Kafka topic, we will use the expose-kafka service that was deployed as part of the install (the url is included in the deployment information).  This can be done with Postman, curl, or some other http tool.  

The example curl command below will place the contents of the file `testpatient.json` (a patient FHIR bundle) on the patients.updated.out kafka topic.  At that point, the enrichment flow is listening for messages and will immediately take the new bundle and begin to process it.  

```
curl -X POST https://<<expose-kafka-external-url>>?topic=patients.updated.out  \
   --header "Content-Type: text/plain" \
   --header "ResolveTerminology: true" \
   --header "DeidentifyData: false" \
   --header "RunASCVD: true" \
   --data-binary  @<<pathtofile/testpatient.json
```

Note that there are three headers in the above request describing which enrichment steps should or should not be performed.  

 - **ResolveTerminology** will run the bundle through the terminology normalization process.
 - **DeidentifyData** will run the de-identify logic. This will store the de-identified data to a separate FHIR server and allow the original data to continue through the flow.
 - **RunASCVD** will run the FHIR bundle through the ASCVD service. This will calculate a ten-year risk of cardiovascular disease and store the result as an attribute in the flow file. Use of the attribute is left up to the user of the Clinical Ingestion pipeline to determine.

When the Enrichment process is complete, the updated FHIR result will be placed on a different Kafka topic called `patient.enriched.out`.  From there it is up to the user to decide what to do with the FHIR result.

In order to see those results, you can use the expose-kafka service and request to see all the messages on the patient.enriched.out topic.

```
curl -X GET https://<<external-expose-kafka-url>>?topic=patient.enriched.out
```


## Options

#### pushToFhir

The DeID enrichment step has the option to persist the deidentified FHIR resources to a second FHIR server.  This secondary FHIR server, known as the DeID FHIR Server, is deployed and used by default.  

If you would like to turn off that save to FHIR action, you can change the value of the `DEID_PUSH_TO_FHIR` environment variable in `clinical_enrichment.yaml` to `False`

```
- name: "DEID_PUSH_TO_FHIR"
  value: "False"
```

## Advanced topics

#### Synthetic data via Synthea

  If you don't have data, you can create some synthetic clinical data to push. Synthetic patient data can be generated using the Synthea Patient Generator.  Download Synthea and run the following command (for more information on Synthea visit their [Github page](https://github.com/synthetichealth/synthea)):

  `java -jar synthea-with-dependencies.jar -p 10`

  This command will have created FHIR bundles for 10 patients with their clinical history and their corresponding medical providers.

#### Kafka topics for the pipeline

To submit data to the Enrichment pipeline, it needs to be posted to the configured Kafka topic. The Kafka topic to target depends on the pipeline you are running and the Nifi configuration. For example, in the Enrichment pattern the topic is called `patients.updated.out` as was used above.  This can be found and/or updated in the Nifi parameter context `enrichment parameter context` under the parameter `enrich.in`.

The FHIR response with the requested modifications will be placed on a topic called `patient.enriched.out`, again found in the `enrichment parameter context` under the parameter `enrich.out`.

#### Other data formats
Currently, the enrichment pattern is designed to operate only on data in FHIR format.
Note that if the enrichment pattern is being used as part of the ingestion pattern, then HL7 data will be
converted to FHIR (by ingestion) before it is allowed to run through the enrichment pipeline.
Other data types (such as DICOM image data) are being considered but are currently not supported.

#### Alternate configuration for Helm Chart

When deploying this chart, there are many configuration parameters specified in the values.yaml file.  These can all be overridden based on individual preferences.  To do so, you can create a secondary YAML file containing your changes and specify it to the `helm install` command to override default configuration.

```
helm install <<RELEASE_NAME>> . \
    -f value_overrides.yaml \
    -f ingress_values.yaml \
    -f clinical_enrichment.yaml
```

**NOTE:** You can chain multiple override file parameters in yaml, so if you want to deploy the load balancer values as well as other overrides, just specify each using another "-f" parameter.

**NOTE:** Due to a limitation in Helm, when using the Health Patterns chart with a release name other than the defaults of `enrich`, you are required to update the corresponding values.yaml file to have the correct release name.  

For enrichment, update the `RELEASE_NAME` environment variable in the `clinical_enrichment.yaml` file.  The value should be changed from _enrich_ to whatever release name you choose.

```
env:
- name: "RELEASE_NAME"
  value: "enrich"
```

In that same file, update the line
- `bootstrapServers: "enrich-kafka:9092"` to include the correct Kafka broker, replacing _enrich_ with the correct release name.
