# Expose Kafka Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs an instance of the Alvearie Expose Kafka service in a Kubernetes cluster.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+

## Installation

Add Alvearie Health Patterns Helm repo to your local Helm environment:

```
helm add repo health-patterns https://alvearie.io/health-patterns/charts
```

Install the helm chart using:

```bash
helm install <<RELEASE_NAME>> health-patterns/expose-kafka
```

You can augment this install with the following configuration parameters:

`bootstrap`: Set the URL of the bootstrap Kafka server. If this is not provided, it will be generated based on the release name provided to the install

`username`: Set the username used to access the target Kafka server. (Default: `token`)

`password`: Set the password used to access the target Kafka server. (Default: `integrati0n`)

### Using the Chart

See [Expose Kafka](../README.md) for information about calling the deployed API.

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
