# Deid Prep Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs an instance of the Alvearie De-identification Prep service in a Kubernetes cluster.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+

###Required environment variables

This chart requires that you provide a De-Identification server URL, as well as a URL, username, and password for your target FHIR server in order to work properly. You can pre-define these as environment variables using:

```
export DEID_SERVICE_URL=<<DEID_SERVICE_URL>>
export DEID_FHIR_SERVER_URL=<<DEID_FHIR_SERVER_URL>>
export DEID_FHIR_SERVER_USERNAME=<<DEID_FHIR_SERVER_USERNAME>>
export DEID_FHIR_SERVER_PASSWORD=<<DEID_FHIR_SERVER_PASSWORD>>
```

Specifying your preferred values for the variables in `<<>>`

## Installation

Add Alvearie Health Patterns Helm repo to your local Helm environment:

```
helm add repo health-patterns https://alvearie.io/health-patterns/charts
```

Install the helm chart using:

```bash
helm install <<RELEASE_NAME>> health-patterns/deid-prep \
     --set DEID_SERVICE_URL=$DEID_SERVICE_URL \
     --set DEID_FHIR_SERVER_URL=$DEID_FHIR_SERVER_URL \
     --set DEID_FHIR_SERVER_USERNAME=$DEID_FHIR_SERVER_USERNAME \
     --set DEID_FHIR_SERVER_PASSWORD=$DEID_FHIR_SERVER_PASSWORD
```

### Using the Chart

See [Deid Prep](../README.md) for information about calling the deployed API.

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
