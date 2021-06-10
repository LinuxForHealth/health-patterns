# microservices/terminology

REST API for translating FHIR objects

## Configuration

These values are stored in ConfigMap `terminology-config`.

| Key | Description | Default Value |
|-----|-------------|---------------|
| `fhirserver.url` | URL of the FHIR server | `"http://ingestion-fhir/fhir-server/api/v4"` |
| `fhirserver.username` | Username for the FHIR server | `fhiruser` |
| `fhirserver.password` | Password for the FHIR server | `integrati0n` |

## Usage
| Action | Method | Endpoint | Body | Parameters | Returns on Success |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Translate | `POST` | `/` | FHIR bundle or resource | | Translated object |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK </br> Status `500` if errors | |