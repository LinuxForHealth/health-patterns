# Cohort

# Table of Contents
- [Welcome to health-patterns](#cohort-overview)
- [How to deploy](#how-to-deploy)
- [Using the pattern](#using-the-pattern)
- [Advanced topics](#advanced-topics)

## Welcome to health-patterns

health-patterns is a place to find cloud reference implementations for the overall Alvearie architecture (https://alvearie.io/architecture) that incorporate best practices using open technologies.  Each pattern incorporates parts of [Alvearie](https://alvearie.io/) along with other open technologies that can be used to start building your own healthcare solutions using a common base of proven technology.


#### Cohort Service Overview

The **Cohort** service application is a Java cloud application built using [Spring](https://spring.io/) that uses the [quality-measure-and-cohort-service](https://github.com/Alvearie/quality-measure-and-cohort-service) to execute CQL libraries against patients in a [FHIR server](https://ibm.github.io/FHIR/). The application is comprised of multiple REST API endpoints that allow users to:

  - Configure a FHIR connection
  - Manage CQL libraries (including all CRUD operations) that specify [Clinical Quality Measures](http://build.fhir.org/ig/HL7/cqf-measures/measure-conformance.html)
  - Run those CQL libraries against all or subset of patients in the FHIR server




## How to deploy

The cohort service can be deployed as part of the [Ingestion](../ingest/README.md) pattern by turning on an enable flag during the ingestion deployment.  By doing this, you get all of the useful features of ingestion as well as the ability to manage and execute cql.

#### Prerequisites

These instructions assume that you have the following resources, tools, and configurations:

- Kubernetes cluster 1.10+
- Helm 3.0.0+
- Access to ```kubectl```, the Kubernetes command line tool
- PV provisioner support in the underlying infrastructure

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


#### KEY STEP...Enable the cohort service

The only configuration change that needs to be made is to enable the cohort service.  This is done by changing the `enabled` flag in the `cohort-service` section of the `values.yaml` file as shown below.

```
cohort-service:
  enabled: true
```
#### Deployment

The following Helm command will deploy the ingestion pattern including the initiation of the cohort service.
```
helm install ingestion .
```
After running the command above, you will see notes that give you information about the deployment, in particular, where the important services (e.g. cohort-service) have been deployed.

**IMPORTANT NOTE** The release name for the ingestion pipeline must be **ingestion** (see [Advanced topics](#advanced-topics) for additional information)

#### Uninstall/delete

To uninstall/delete the deployment, use:
```
helm delete ingestion
```


## Using the pattern
Assuming you have used the Ingestion pattern or some other means to populate the FHIR server with patient data, you are ready to use the cohorting service.  In order to use the cohorting service you must first upload a cql libary. In its simplest form, a cql library has a name, a version, and a definition that describes how to identify patients in a specific population.  For example, the following cql defines a way to extract patients who are female and then only those that are older than 25.

```
library "FemalePatientsOver25" version '1.0.1'

// Female patients older than 25

using FHIR version '4.0.1'

include "FHIRHelpers" version '4.0.1' called FHIRHelpers

context Patient

define "Patient is Female":
   Patient.gender.value = 'female'

define "Initial Population":
   "Patient is Female"

define "Denominator":
   "Initial Population"

define "Numerator":
   AgeInYears() >= 25
```

To upload this cql, simply POST it to the cohort service `libraries` endpoint.

```
https://<<external-hostname>>/cohort-service/libraries
```

After adding a new library, it is possible to list the current libraries by doing a GET request to the same endpoint.  In order to run the cql against the current FHIR server, note the name and version number for the cql.  A GET request to the endpoint formed by `libaryname`-`version` using the `patientIds` function will return all the patient ids that match the criteria from the cql.  For example,

```
https://<<external-hostname>>/cohort-service/libraries/FemalePatientsOver25-1.0.1/patientIds
```

## Advanced topics

#### Synthetic data via Synthea

  If you don't have data, you can create some synthetic clinical data to push. Synthetic patient data can be generated using the Synthea Patient Generator.  Download Synthea and run the following command (for more information on Synthea visit their [Github page](https://github.com/synthetichealth/synthea)):

  `java -jar synthea-with-dependencies.jar -p 10`

  This command will have created FHIR bundles for 10 patients with their clinical history and their corresponding medical providers.

### Changing the release name

The `values.yaml` file contains a  `releaseName` variable that can be set to values other than the default of `ingestion`.

```
releaseName: &releaseName <<your new release name>>
```

If you choose to change the default then be sure to also use the new release name in the helm install command.

```
helm install <<your new release name>> .
```
