# microservices/terminology

REST API for translating FHIR objects

## Configuration

These values are stored in ConfigMap `terminology-config`.

| Key | Description | Default Value |
|-----|-------------|---------------|
| `fhirserver.url` | URL of the FHIR server | `"http://ingestion-fhir/fhir-server/api/v4"` |
| `fhirserver.username` | Username for the FHIR server | `fhiruser` |
| `fhirserver.password` | Password for the FHIR server | `integrati0n` |

## Installation

```shell
kubectl apply -f kubernetes.yml
```
> **_NOTE:_**  If multiple instances will be deployed on a single cluster, each instance's
> persistent volume must have a unique name. The helm chart in ~/.../alvearie-ingestion/
> does this automatically, but for a manual install you must change "`deid-config-pv`" in
> `kubernetes.yml` to some unique name for each instance.

## Usage
| Action | Method | Endpoint | Body | Parameters | Returns on Success |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Translate | `POST` | `/` | FHIR bundle or resource | | Translated object |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK </br> Status `500` if errors | |