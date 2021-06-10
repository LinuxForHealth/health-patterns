# microservices/deid

REST API for communicating with a deidentification service and FHIR server

## Configuration

TODO

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