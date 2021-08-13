# DEID Prep Service

REST API for communicating with a de-identification service and FHIR server.

> This project is built with Quarkus; to deploy changes, ensure that
> `quarkus.container-image.group` in `/src/main/resources/application.properties`
> is set to your DockerHub username, then run `./mvnw package`. The new yml
> file will be located in `/target/kubernetes/`.

## Configuration

These values are stored in ConfigMap `deid-config`.

| Key | Description | Default Value |
|:----|:------------|:-------------|
| `service.url` | URL of the deidentification service | `http://ingestion-deid:8080/api/v1` |
| `fhirserver.url` | URL of the deid FHIR server | `http://ingestion-fhir-deid/fhir-server/api/v4` |
| `fhirserver.username` | Username for the deid FHIR server | `fhiruser` |
| `fhirserver.password` | Password for the deid FHIR server | `integrati0n` |
| `pv.path` | Mount path for the persistent volume | `/mnt/data/` |

## Installation

```shell
kubectl apply -f kubernetes.yml
```
> **_NOTE:_**  If multiple instances will be deployed on a single cluster, each instance's
> persistent volume must have a unique name. The helm chart in `../../helm-charts/health-patterns/`
> does this automatically, but for a manual install you must change "`deid-config-pv`" in
> the `PersistentVolume` definition in `kubernetes.yml` to some unique name for each instance.

## Usage

The service listens on port 8080. Configs tell the deid service which fields to deidentify;
the default config can be found at `/src/main/resources/de-id-config.json`.

| Action | Method | Endpoint | Body | Parameters | Returns on Success |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Deidentify | `POST` | `/` | FHIR bundle or resource | `configName`: Name of config to use *(optional, default: "default")* </br> `pushToFHIR`: (true/false) Whether to push the deidentified object to the FHIR server *(optional, default: true)* | Deidentified object |
| Add Config (will overwrite) | `PUT` | `/config/{configName}` | Config (json) | | Status `200` |
| Add Config (will not overwrite) | `POST` | `/config/{configName}` | Config (json) | | Status `200` |
| Get Configs | `GET` | `/config` | | | Newline-delimited list of config names |
| Get Config | `GET` | `/config/{configName}` | | | Config named `configName` |
| Delete Config | `DELETE` | `/config/{configName}` | | | Status `200` |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK </br> Status `500` if errors |