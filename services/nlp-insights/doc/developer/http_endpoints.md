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

It is possible to configure as many different instances of these two engines as needed with different configuration details.  Configuration jsons require a `name`, an `nlpServiceType` (either `acd` or `quickumls`), and config details specific to that type.
For quickumls, an `endpoint` is required. For ACD, an `endpoint`, an `apikey`, and a `flow`.

<table>


<tr> <th> &nbsp; </th><th> Method &<BR/> Endpoint</th><th> Body </th><th> Returns on Success </th></tr>
<tr> <td> <B>Config Definition</B> </td><td> &nbsp; </td><td> &nbsp; </td><td> &nbsp; </td><td> &nbsp; </td></tr>
<tr><td> Get All Configs </td><td> GET <BR/>/all_configs</td><td>&nbsp;</td><td> Config definition names: 

```json 
{
  "all_configs": [
    "acdconfig1",
    "quickconfig1"
  ]
}
``` 

</td></tr>

<tr><td> Add Named Config </td><td> PUT<BR/>POST <BR/>/config/definition</td><td>json config (contains name). Example:

```json
{
  "name": "quickconfig1",
  "nlpServiceType": "quickumls",
  "config": {
    "endpoint": "http://***"
  }
}
```

</td><td> Status 200</td></tr>

<tr><td> Delete Config </td><td> DELETE<BR/>/config/{configName}</td> <td> &nbsp; </td><td> Status 200 </td></tr>

<tr><td> Get Config Details </td><td> GET <BR/> /config/{configName} </td><td></td>
<td> Example Response:

```json
{
  "name": "quickconfig1",
  "nlpServiceType": "quickumls",
  "config": {
    "endpoint": "http://***"
  }
}
```
</td>
</tr>
<tr><td>&nbsp; </td><td> &nbsp; </td><td> &nbsp; <td> &nbsp; </td></tr>
<tr> <td> <B>Default NLP</B> </td><td> &nbsp; </td><td> &nbsp; </td><td> &nbsp; </td></tr>
<tr><td> Make Config default </td><td> POST<BR/>PUT <BR/>/config/setDefault?name={configName}</td><td></td><td> Status 200 </td></tr>
<tr><td> Get Current Default Config </td><td> GET <BR/> /config </td><td></td><td> Current default configName:

```json
{
  "config": "acdconfig1"
}
```


<tr><td> Clear default config </td><td> POST<BR/>PUT <BR/> /config/clearDefault</td><td> </td><td> Status 200 </td><tr>

 </td></tr>
 
 <tr><td>&nbsp; </td><td> &nbsp; </td><td> &nbsp; </td><td> &nbsp; </td></tr>
<tr> <td> <B>Override NLP Engine for a resource </B> </td><td> &nbsp; </td><td> &nbsp; </td><td> &nbsp; </td></tr>

<tr><td>  Get all active overrides </td><td> GET <BR/>/config/resource </td><td> </td><td>
Dictionary of overrides:

```json
{
  "AllergyIntolerance": "acdconfig1",
  "Condition": "acdconfig1"
}
```
</td></tr>

<tr><td>  Get the active override for a resource </td><td> GET <Br/>/config/resource/{resource} </td><td> </td><td>
Dictionary of override:

```json
{
  "resource": "Condition",
  "config": "acdconfig1"
}
```

If no override is defined:

```json
{
  "config": null,
  "resource": "Condition"
}
```

</td></tr>

<tr><td>Add resource override</td><td>POST<BR/>PUT<br/>/config/resource/{resourcetype}/{configName}</td><td></td><td> Status 200 </td></tr>
<tr><td>Delete a resource override</td><td>DELETE<BR/>/config/resource/{resourcetype}</td><td></td><td>Status 200 </td></tr>
<tr><td>Delete all resource overrides</td><td>DELETE<br/>/config/resource</td><td></td><td> Status 200</td></tr>
</table> 


# Error Responses
Responses with status codes in the 4xx range usually have a json body with a "message" property with a human readable description. Other details about the error may also be included in the structure.

## Example for invalid json sent to discoverInsights API:

```json
{
  "message": "Resource was not valid json: Expecting property name enclosed in double quotes: line 29 column 10 (char 676)"
}
```

## Example of invalid FHIR resource sent to discoverInsights API

```json
{
  "message": "Resource was not valid",
  "details": [
    {
      "loc": [
        "reaction",
        0,
        "manifestation",
        0,
        "text2"
      ],
      "msg": "extra fields not permitted",
      "type": "value_error.extra"
    }
  ]
}
```
