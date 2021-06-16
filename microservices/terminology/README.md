# microservices/terminology

REST API for translating FHIR objects.

> This project is built with Quarkus; to deploy changes, ensure that
> `quarkus.container-image.group` in `/src/main/resources/application.properties`
> is set to your DockerHub username, then run `./mvnw package`. The new yml
> file will be located in `/target/kubernetes/`.

## Configuration

These values are stored in ConfigMap `terminology-config`.

| Key | Description | Default Value |
|-----|-------------|---------------|
| `fhirserver.url` | URL of the FHIR server | `"http://ingestion-fhir/fhir-server/api/v4"` |
| `fhirserver.username` | Username for the FHIR server | `fhiruser` |
| `fhirserver.password` | Password for the FHIR server | `integrati0n` |
| `pv.path` | Mount path for the persistent volume | `/mnt/data/` |

## Installation

```shell
kubectl apply -f kubernetes.yml
```
> **_NOTE:_**  If multiple instances will be deployed on a single cluster, each instance's
> persistent volume must have a unique name. The helm chart in `~/.../alvearie-ingestion/`
> does this automatically, but for a manual install you must change "`deid-config-pv`" in
> the `PersistentVolume` definition in `kubernetes.yml` to some unique name for each instance.

## Usage

The service listens on port 8080.

> TODO: Add explanation of mappings / structure definitions, where to find examples, how to use

| Action | Method | Endpoint | Body | Parameters | Returns on Success |
|:------:|:------:|:---------|:----:|:-----------|:-------:|
| Translate | `POST` | `/` | FHIR bundle or resource | | Translated object |
| Add Mapping (will not overwrite) | `POST` | `/mapping/{mappingName}` | Mapping (json) | | Status `200` |
| Add Mapping (will overwrite) | `PUT` | `/mapping/{mappingName}` | Mapping (json) | | Status `200`
| Get Mappings | `GET` | `/mapping` | | | Newline-delimited list of mapping names |
| Get Mapping | `GET` | `/mapping/{mappingName}` | | | Mapping named `mappingName` |
| Delete Mapping | `DELETE` | `/mapping/{mappingName}` | | | Status `200` |
| Add Structure Definition | `POST` | `/structureDefinitions` | Structure Definition (json) | | Status `200` |
| Get Structure Definitions | `GET` | `/structureDefinitions` | | | Newline-delimited list of structure definitions |
| Delete Structure Definition | `DELETE` | `/structureDefinitions` | Structure Definition (json) | | Status `200` |
| Health Check | `GET` | `/healthCheck` | | | Status `200` if OK </br> Status `500` if errors |