# microservices/deid

REST API for communicating with a deidentification service and FHIR server

## Configuration

| Key | Description | Default Value |
|-----|-------------|---------------|
| `service.url` | URL of the deidentification service | `http://ingestion-deid:8080/api/v1` |
| `fhirserver.url` | URL of the deid FHIR server | `http://ingestion-fhir-deid/fhir-server/api/v4` |
| `fhirserver.username` | Username for the deid FHIR server | `fhiruser` |
| `fhirserver.password` | Password for the deid FHIR server | `integrati0n` |
| `pv.path` | Mount path for the persistent volume | `/mnt/data/` |

## Usage
| Action | Method | Endpoint | Body | Parameters | Returns |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Deidentify | `POST` | `/` | FHIR bundle or resource | `configName`: Name of config to use *(optional)* </br> `pushToFHIR`: (true/false) Whether to push the deidentified object to the FHIR server *(optional)* | Deidentified object |
| Add Config (will overwrite) | `POST` | `/config/{configName}` | Config (json) | | Status `200` if successful |
| Add Config (will not overwrite) | `PUT` | `/config/{configName}` | Config (json) | | Status `200` if successful |
| Get Configs | `GET` | `/config` | | | Newline-delimited list of config names |
| Get Config | `GET` | `/config/{configName}` | | | Config named `configName` |
| Delete Config | `DELETE` | `/config/{configName}` | | | Status `200` if successful |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK |