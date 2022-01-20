# HTTP Endpoints

## Discover Insights
The discoverInsights API accepts an input bundle and returns an updated bundle with:
* Resources that have been enriched with additional codes
* Resources that have been derived from unstructured text (such as clinical notes) contained within the bundle's resources.

| Action | Method | Endpoint | Body | Returns on Success |
|:------:|:------:|:---------|:----:|:-------:|
| Add insights | `POST` | `/discoverInsights` | FHIR bundle | Enriched FHIR Bundle |

Derived and Enriched types are described in the tutorials.

* [Derive new resources with ACD](../examples/acd/derive_new_resources.md)
* [Enrich resources with ACD](../examples/acd/enrich.md)
* [Derive new resources with QuickUMLS](../examples/quickumls/derive_new_resources.md)
* [Enrich resources with QuickUmls](../examples/quickumls/enrich.md)

<details><summary>Experimental support for non-bundle resources</summary>

If the discoverInsights API is called with a FHIR resource that is *Not* a bundle, then the returned data depends on the input type:
 
 Body Type | Returns 
 --- | ---
 DiagnosticReport or Document Reference | A bundle of derived resources, or an empty bundle if no resources were derived.
 Condition or AllergyIntolerance | The resource is returned with additional codes, or with no additional codes if no codes were derived.

Other resource types *may* return an error.

When using this API resources __must__ have a valid identifier. Because health-patterns will invoke the service before creating resources in thie FHIR server, the identifier has not been set. The result is that this version of the API is not as useful in an ingestion pipeline, and therefore is discouraged/experimental.

The version of the API that accepts a bundle input makes use of the fullUrl property in the bundleEntry for each resource (setting the property if necessary), and this allows that variation to support the requirements of health-patterns.
</details>

## Configuration
The app currently supports running two different NLP engine types: 
* [IBM's Annotator for Clinical Data (ACD)](https://www.ibm.com/cloud/watson-annotator-for-clinical-data) and 
* [open-source QuickUMLS](https://github.com/Georgetown-IR-Lab/QuickUMLS)

It is possible to configure as many different instances of these two engines as needed with different configuration details.  Configuation jsons require a `name`, an `nlpServiceType` (either `acd` or `quickumls`), and config details specific to that type.
For quickumls, an `endpoint` is required. For ACD, an `endpoint`, an `apikey`, and a `flow`.

| &nbsp; | Method | Endpoint | Body | Returns on Success |
|:------:|:------:|:---------|:----:|:-------:|
  __Config Definition__ | &nbsp; | &nbsp; | &nbsp; | &nbsp; 
| Get All Configs | `GET` | `/all_configs` |&nbsp; | Newline-delimited list of config names |
| Add Named Config  | `PUT/POST` | `/config/definition` | Config (json) contains `name` | Status `200`
| Delete Config | `DELETE` | `/config/{configName}` | | Status `200` |
| Get Config Details | `GET` | `/config/{configName}` | | Config details named `configName` |
 &nbsp; | &nbsp; | &nbsp; | &nbsp; | &nbsp;
 __Default NLP__ | &nbsp; | &nbsp; | &nbsp; | &nbsp;
| Make Config default | `POST/PUT` | `/config/setDefault?name={configName}` | | Status `200` |
| Get Current Default Config | `GET` | `/config` | | Current default `configName` |
| Clear default config | `POST/PUT` | `/config/clearDefault` | | Status `200` |
 &nbsp; | &nbsp; | &nbsp; | &nbsp; | &nbsp;
 __Override NLP engine for a resource__ | &nbsp; | &nbsp; | &nbsp; | &nbsp;
| Get all active overrides | `GET` | `/config/resource` | | dictionary-Status `200` |
| Get the active override for a resource | `GET` | `/config/resource/{resource}` | | `configName`-Status `200` |
| Add resource override | `POST/PUT` | `/config/resource/{resourcetype}/{configName}` | | Status `200` |
| Delete a resource override | `DELETE` | `/config/resource/{resourcetype}` | | Status `200` |
| Delete all resource overrides | `DELETE` | `/config/resource` | | Status `200` |