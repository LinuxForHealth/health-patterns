# Alvearie Clinical Ingestion Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs the [Alvearie Clinical Ingestion pattern](https://github.com/Alvearie/health-patterns/tree/initial-charts/clinical-ingestion) in a Kubernetes cluster.

The [Alvearie Clinical Ingestion pattern](https://github.com/Alvearie/health-patterns/tree/initial-charts/clinical-ingestion) is comprised of multiple components described in more detail in the pattern's main page, and using this Helm chart you can optionally enable/disable components of that pattern.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+
- PV provisioner support in the underlying infrastructure.

## Installation

### Checkout the Code

Git clone this repository and `cd` into this directory.

```bash
git clone https://github.com/Alvearie/health-patterns.git
cd clinical-ingestion/helm-charts/alvearie-ingestion
```

### Create a new namespace (Optional)

It is recommended, though not required, that you create a namespace before installing the chart in order to prevent the various artifacts that will be installed by it from mixing from the rest of the artifacts in your Kubernetes cluster, in an effort to make it easier to manage them.

```bash
kubectl create namespace alvearie
kubectl config set-context --current --namespace=alvearie
```

### Install the Chart

Install the helm chart with a release name `ingestion`:

```bash
helm install ingestion .
```

### Using the Chart

After running the previous `helm install` command, you should get a set of instructions on how to access the various components of the chart and using the [Alvearie Clinical Ingestion pattern](clinical-ingestion).

## Uninstallation

To uninstall/delete the `ingestion` deployment:

```bash
helm delete ingestion
```

Deletion of charts doesn't cascade to deleting associated `PersistedVolume`s and `PersistedVolumeClains`s. 
To delete them:

```bash
kubectl delete pvc -l release=ingestion
kubectl delete pv -l release=ingestion
```

## Configuration

Each requirement is configured with the options provided by that Chart.
Please consult the relevant charts for their configuration options.

| Parameter                | Description                                                                                                        | Default   |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------| --------- |
| `kafka.enabled`          | Enable [Kafka](https://github.com/helm/charts/tree/master/incubator/kafka)                                         | `true`    |
| `nifi.enabled`           | Enable [Nifi](https://github.com/cetic/helm-nifi)                                                                  | `true`    |
| `nifi-registry.enabled`  | Enable [Nifi Registry](../nifi-registry)                                                                           | `true`    |
| `fhir.enabled`           | Enable [Spark](../fhir)                                                                                            | `true`    |
| `zookeeper.enabled`      | Enable [Zookeeper](https://github.com/bitnami/charts/tree/master/bitnami/zookeeper)                                | `true`    |

## Contributing

Feel free to contribute by making a [pull request](https://github.com/Alvearie/health-patterns/pull/new/master).

Please review the [Contributing Guide](https://github.com/Alvearie/health-patterns/blob/main/CONTRIBUTING.md) for information on how to get started contributing to the project.

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
