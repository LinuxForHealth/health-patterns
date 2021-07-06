# Terminology Services Prep Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs an instance of the Alvearie Terminology Services Prep service in a Kubernetes cluster.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+

###Required environment variables

This chart requires that you provide a server URL, username, and password to work properly. You can pre-define these as environment variables using:

```
export $FHIR_SERVER_URL=<<FHIR_SERVER_URL>>
export $FHIR_SERVER_USERNAME=<<FHIR_SERVER_USERNAME>>
export $FHIR_SERVER_PASSWORD=<<FHIR_SERVER_PASSWORD>>
```

Specifying your preferred values for the variables in `<<>>`

## Installation

Add Alvearie Health Patterns Helm repo to your local Helm environment:

```
helm repo add health-patterns https://alvearie.io/health-patterns/charts
helm repo update
```

Install the helm chart using:

```bash
helm install <<RELEASE_NAME>> health-patterns/term-services-prep \
     --set FHIR_SERVER_URL=$FHIR_SERVER_URL \
     --set FHIR_SERVER_USERNAME=$FHIR_SERVER_USERNAME \
     --set FHIR_SERVER_PASSWORD=$FHIR_SERVER_PASSWORD
```

### Using the Chart

See [Terminology Services Prep](../README.md) for information about calling the deployed API.

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