# microservices/terminology

REST API for translating FHIR objects

## Configuration

| Key | Description | Default Value |
|-----|-------------|---------------|
| `fhirserver.url` | URL of the FHIR server | `http://ingestion-fhir-deid/fhir-server/api/v4` |
| `fhirserver.username` | Username for the FHIR server | `fhiruser` |
| `fhirserver.password` | Password for the FHIR server | `integrati0n` |

## Usage
| Action | Method | Endpoint | Body | Parameters | Returns |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Translate | `POST` | `/` | FHIR bundle or resource | | Translated object |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK | |