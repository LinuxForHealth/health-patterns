# NiFi Registry Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs an [Apache NiFi Registry](https://nifi.apache.org/registry.html) in a Kubernetes cluster.

There is an [existing NiFi Registry chart](https://github.com/dysnix/charts/tree/master/nifi-registry) used by the [cetic/nifi](https://github.com/cetic/helm-nifi) chart, for most purposes it's probably better to use that chart, however that chart currently does not support the ability to initialize the NiFi Registry so that it is connected to a Github Persistence Provider. If you need the ability to initialize the NiFi Registry from a Github repository, this chart can be used for that.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+

## Installation

### Checkout the Code

Git clone this repository and `cd` into this directory.

```bash
git clone https://github.com/Alvearie/health-patterns.git
cd health-patterns/clinical-ingestion/helm-charts/alvearie-ingestion/charts/nifi-registry
```

### Install the Chart

Install the helm chart with a release name `nifi-registry`:

```bash
helm install nifi-registry .
```

### Using the Chart

Access your NiFi Registry at: `http://<cluster-ip>/nifi-registry`

## Uninstallation

To uninstall/delete the `nifi-registry` deployment:

```bash
helm delete nifi-registry
```

## Configuration

Each requirement is configured with the options provided by that Chart.
Please consult the relevant charts for their configuration options.

| Parameter                | Description                                                                                                        | Default   |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------| --------- |
| `git.repository`          | The repository to use to initialize the GithubPersistenceFlowProvider                                         | (The alvearie releae NiFi flow repo)   |
| `service.type`           | The Kubernetes service type for this NiFi Registry                                                                  | `ClusterIP`    |

## Contributing

Feel free to contribute by making a [pull request](https://github.com/Alvearie/health-patterns/pull/new/master).

Please review the [Contributing Guide](https://github.com/Alvearie/health-patterns/blob/main/CONTRIBUTING.md) for information on how to get started contributing to the project.

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
