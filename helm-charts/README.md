# Health Patterns Helm Charts

## Introduction

This directory contains the [Helm](https://github.com/kubernetes/helm) charts used to install the Alvearie Health Patterns in a Kubernetes cluster.

The main chart in this directory is:

- [Health Patterns](./health-patterns): Chart used to install the entire Alvearie Health Patterns flow

That main chart has many dependent sub-charts.  These are referenced via their Helm repository locations, but a few do not currently have supported Helm charts so we have created them in this folder for our use. They can also be used as standalone charts.

- [FHIR Chart](./fhir): Chart used to install a FHIR server
- [NiFi Registry Chart](./nifi-registry): Chart used to install a [NiFi Registry](https://nifi.apache.org/registry.html)
- [DeID Service Chart](./deid): Chart used to install a [De-Identification Service](https://github.com/Alvearie/de-identification)

## Updating

The sub-charts maintained here are source-only.  The main chart references the packaged version of these, hosted in the helm repo located [here](../../docs/charts).  Whenever any of these sub-charts are updated, the following steps are required:

1. Navigate to the Helm repo folder: `cd health-patterns/docs/charts`
2. Run: `helm package ../../helm-charts/<chart_folder>`
3. Update the index: `helm repo index .`
4. Deliver any updated artifacts back to Git. This is where the Helm repo serves the charts to requests.

## Contributing

Feel free to contribute by making a [pull request](https://github.com/Alvearie/health-patterns/pull/new/master).

Please review the [Contributing Guide](/CONTRIBUTING.md) for information on how to get started contributing to the project.

### Running Github Chart Linting Locally

This notes describe the necessary steps to lint a chart in a local dev env.

There is a Github Action that will automatically lint the Alvearie Health Patterns charts when a corresponding PR is created, however it is convenient to have a way to reproduce that process locally to avoid having to push a PR just to be able to run the official linting process.

The chart linting process is done using a Github Action called *helm/chart-testing-action@v2.0.1*. That action runs a docker image that contains the chart-testing tool and runs the chart through the tool. 

You can reproduce that process locally by running that same Docker image as follows:

- Create the chart-testing container (save the returned container ID from the following command):

```
cd ~/git/health-patterns
docker container run --interactive --tty --detach --volume "$(pwd):/workdir" --workdir /workdir "quay.io/helmpack/chart-testing:latest"
```

- Run the `ct lint` command in the container:

```
docker exec <conatiner-id> ct lint --chart-dirs helm-charts --target-branch main --validate-maintainers=false --debug 
```

`ct lint` runs:
- chart version check
- yamale for Chart validation by schema of Chart.yaml
- yamllint (not so much syntax but more cosmetic and conventional) for  Chart.yaml and values.yaml
- maintainers check (names need to match a github username) (disabled)
- helm lint

## License
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
