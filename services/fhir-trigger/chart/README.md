# FHIR Trigger Helm Chart

## Introduction

This [Helm](https://github.com/kubernetes/helm) chart installs an instance of the Alvearie FHIR Trigger service in a Kubernetes cluster.

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
helm install <<RELEASE_NAME>> health-patterns/fhir-trigger
```

You can augment this install with the following configuration parameters:

`trigger_type`: See [TRIGGERTYPE](../README.md#triggertype) (Default: `history`)

`resources_list`: See [RESOURCESLIST](../README.md#resourceslist) (Default: `[Patient, Observation, Condition]`)

`max_iterations`: See [MAXITERATIONS](../README.md#maxiterations) (Default: `15`)

`alarm_minutes`: See [ALARMMINUTES](../README.md#alarmminutes) (Default: `10`)

`chunk_size`: See [CHUNKSIZE](../README.md#chunksize) (Default: `200`)

`sleep_seconds`: See [SLEEPSECONDS](../README.md#sleepseconds) (Default: `60`)

`kafka.username`: See [KAFKAUSER](../README.md#kafkauser) (Default: `token`)

`kafka.password`: See [KAFKAPW](../README.md#kafkapw) (Default: `integrati0n`)

`kafka.producer_topic`: See [PRODUCERTOPIC](../README.md#producertopic) (Default: `enrich.topic.in`)

`kafka.consumer_topic`: See [CONSUMERTOPIC](../README.md#consumertopic) (Default: `fhir.notification`)

`kafka.bootstrap`: See [KAFKABOOTSTRAP](../README.md#kafkabootstrap) (Default: generated based on the release name provided to the install)

`fhir.endpoint`: See [FHIRENDPOINT](../README.md#fhirendpoint) (Default: generated based on the release name provided to the install)

`fhir.username`: See [FHIRUSERNAME](../README.md#fhirusername) (Default: `fhiruser`)

`fhir.password`: See [FHIRPW](../README.md#fhirpw) (Default: `integrati0n`)

### Using the Chart

See [FHIR Trigger](../README.md) for information about calling the deployed API.

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
