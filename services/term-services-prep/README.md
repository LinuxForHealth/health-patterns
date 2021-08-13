# Terminology Service Prep

REST API for applying FHIR Terminology Services to FHIR resources.

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

## Installing

###Local: 
From the project root, run:

```shell 
./mvnw compile quarkus:dev -DPV_PATH=./ \
      -DFHIR_SERVER_URL=<FHIR_URL> \
      -DFHIR_SERVER_PASSWORD=<FHIR_Password> \
      -DFHIR_SERVER_USERNAME=<FHIR_User> \
```

Replace FHIR_URL, FHIR_Password, and FHIR_User with the values corresponding to a test FHIR service.  

Endpoints are accessible at `localhost:8080` and the service will use the project's target directory as the mount for 
data persistence.

###Cluster:
Ensure that you are logged in to Docker and Kubernetes, and are in a kubernetes namespace that has a 
FHIR server deployed.

In `/src/main/kubernetes/kubernetes.yml`, ensure that the following have been set to the correct values for your 
FHIR server's configuration.

```yml
data:
  fhirserver.url: "http://<FHIR-SERVER>/fhir-server/api/v4"
  fhirserver.username: "<FHIR-USER>"
  fhirserver.password: "<FHIR-PASSWORD>"
  pv.path: "<Persistent volume mount path - default = /mnt/data/>"
```

If pv.path is set `""` then the service will operate in memory-only mode.

In `/src/main/resources/application.properties`, ensure that `quarkus.container-image.group` is set to your docker 
username, 'quarkus.kubernetes.name' is set to the desired service name, 
and `quarkus.kubernetes.mounts.mappings.path` is also set to the correct persistent volume path.

From the project root, run:

```shell
./mvnw package
kubectl apply -f /target/kubernetes/kubernetes.yml
```

To use curl/postman to test requests, port forward localhost:8080 to the service using 

```shell
kubectl port-forward service/<quarkus.kubernetes.name> 8080:8080
```
replacing <quarkus.kubernetes.name> with the value in the configuration file.

> **_NOTE:_**  If multiple instances will be deployed on a single cluster, each instance's
> persistent volume must have a unique name. The helm chart in `../../helm-charts/health-patterns/`
> does this automatically, but for a manual install you must change "`deid-config-pv`" in
> the `PersistentVolume` definition in `kubernetes.yml` to some unique name for each instance.

## Usage

The service listens on port 8080. The default mappings and structure definitions can be found
in `/src/main/resources/defaultMappings`.  Additional mappings can be added to the defaultMappings - if added, the 
filename must also be added to the `DEFAULT_MAPPING_RESOURCES` String array in `MappingStore.java`.  Default mappings 
are copied to the persistent volume only if the file structure has not been initialized yet, i.e. on the first run of 
the microservice with a new persistent volume.  Default mappings are also used to initialize the MappingStore when it 
cannot read/write to the disc.

When the service is first deployed and queried on a cluster, it will try to copy the default mappings and
structureDefinitions to the filesystem at the path specified in application.properties and kubernetes.yml.  The default
location is `/mnt/data/`.  To persist data, ensure that a persistent volume is mounted at the specified path.
 
The Translation action applies any of the saved Structure Definition Mappings that match the extensions of the 
given FHIR resource, if the corresponding ConceptMap is installed on the FHIR server.  Default ConceptMaps are installed
when the service is first deployed, and more can be installed using the `Add Mapping` actions.  

Deleting a mapping does not uninstall it from the FHIR server, it just prevents it from being reinstalled should the 
service be restarted.


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

## Example JSON Objects:

Structure Definition Mapping :
```
{
    "sdUri" : "https://www.exampleURI.org/FHIR/SD/exampleStructureDefinition",
    "vsUri" : "https://www.exampleURI.org/FHIR/VS/exampleValueSet" 
}
```
ConceptMap (Mapping) :

See https://www.hl7.org/fhir/valueset-examples.html