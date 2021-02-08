# FHIR Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs an [IBM FHIR Server](https://github.com/IBM/FHIR) in a Kubernetes cluster.

## Pre-Requisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+
- PV provisioner support in the underlying infrastructure.

## Installation

### Checkout the Code

Git clone this repository and `cd` into this directory.

```bash
git clone https://github.com/Alvearie/health-patterns.git
cd health-patterns/clinical-ingestion/helm-charts/fhir
```

### Install the Chart

Install the helm chart with a release name `fhir`:

```bash
helm install fhir .
```

### Using the Chart

Access your FHIR server at: `http://<external-ip>/fhir-server/api/v4`

Credentials:

```bash
# Get the ID of the fhir pod and replace it in <pod-id> in the next command
kubectl get pods
kubectl exec <pod-id> -c server -- cat server.xml | grep -A2 BasicRealm
```

The chart also installs an unauthenticated FHIR Server proxy on port 81: `http://<external-ip>:81/fhir-server/api/v4`

## Uninstallation

To uninstall/delete the `fhir` deployment:

```bash
helm delete fhir
```

Deleting the charts doesn't cascade to deleting associated `PersistedVolume`s and `PersistedVolumeClains`s. 
If FHIR persistence was used, to delete them:

```bash
kubectl delete pvc -l release=fhir
kubectl delete pv -l release=fhir
```

## Configuration

Each requirement is configured with the options provided by that Chart.
Please consult the relevant charts for their configuration options.

See `values.yaml`.

## Contributing

Feel free to contribute by making a [pull request](https://github.com/Alvearie/health-patterns/pull/new/master).

Please review the [Contributing Guide](https://github.com/Alvearie/health-patterns/blob/main/CONTRIBUTING.md) for information on how to get started contributing to the project.

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
