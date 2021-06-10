# microservices/terminology

REST API for translating FHIR objects

## Configuration

TODO

## Usage
| Action | Method | Endpoint | Body | Parameters | Returns |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Translate | `POST` | `/` | FHIR bundle or resource | | Translated object |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK | |