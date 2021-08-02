# CQL BulkExport Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs an instance of the Alvearie CQL BulkExport service in a Kubernetes cluster.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+

## Installation

Add Alvearie Health Patterns Helm repo to your local Helm environment:

```
helm repo add health-patterns https://alvearie.io/health-patterns/charts
helm repo update
```

Install the helm chart using:

```bash
helm install <<RELEASE_NAME>> health-patterns/cql-bulkexport
```

You can augment this install with the following configuration parameters:

`fhir.endpoint`: Set the endpoint for the FHIR server api

`fhir.user`: Set the username used to access the FHIR server

`fhir.pw`: Set the password used to access the FHIR server

`cohort.endpoint`: Set the cohorting service endpoint

`cos.endpoint`: Set the COS endpoint that matches you credentials for your bucket

`cos.apikey`: Set the apikey for the COS bucket

`cos.instancecrn`: Set the service id crn for the COS bucket

`bucketname`: Set the name of the COS bucket

`resourcelist`: Set the resources you wish to export (default is all)

### Using the Chart

See [CQL BulkExport](../README.md) for information about calling the deployed API.

## Uninstallation

To uninstall/delete the deployment:

```bash
helm delete <<RELEASE_NAME>>
```

## Contributing

Feel free to contribute by making a [pull request](https://github.com/Alvearie/health-patterns/pull/new/master).

Please review the [Contributing Guide](https://github.com/Alvearie/health-patterns/blob/main/CONTRIBUTING.md) for information on how to get started contributing to the project.

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
