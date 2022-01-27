# UNDER CONSTRUCTION.......


# Example queries over an nlp-insights response bundle
This tutorial provides example queries over a response bundle.

Although this example uses an ACD configuration, the queries will work when configured for QuickUMLS as well as ACD.
All NLP configurations result in FHIR resources consistient with the Alvearie data model.

## Configure nlp-insights to use ACD for NLP
These examples assume that nlp-insights is configured for ACD.
If the nlp-insights service has not been configured to use ACD by default, follow the steps [here](./configure_acd.md).

## Retrieve a response bundle with discovered insights
This example creates a bundle with several resources for the nlp-insights service to discover insights from.

* A diagnostic report resource that mentions both a condition and a medication for the patient.
* A condition resource for diabetes.
* An allergy intolerance resource for a food allergy (peanuts).
* An allergy intolerance resource for a medication (amoxicillin).

The condition and allergy intolerance resources do not have any coding values associated with them.

**The unstructured text that will be stored in the diagnostic report must be base64 encoded:** <br/>
`B64_REPORT_TEXT=$(echo 'The patient had a myocardial infarction in 2015 and was prescribed Losartan. The patient reports no side effects from Losartan.' | base64 -w 0)`

This curl command sends a bundle with resources to nlp-insights. The resources have ids that are more descriptive than than what would be assigned by a FHIR server. These example ids will help make the examples easier to follow.

The curl is written to store the response bundle from the server in /tmp/output.json. We'll reference this json file in future examples.

```
curl  -w "\n%{http_code}\n" -s -o /tmp/output.json -XPOST localhost:5000/discoverInsights  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
    "resourceType": "Bundle",
    "id": "abc",
    "type": "transaction",
    "entry": [
        {
            "resource": {
                "id": "DiagnosticReport-MI-Losartan",
                "status": "final",
                "code": {
                    "text": "Chief complaint Narrative - Reported"
                },
                "presentedForm": [
                    {
                        "contentType": "text",
                        "language": "en",
                        "data": "$B64_REPORT_TEXT",
                        "title": "ER VISIT",
                        "creation": "2020-08-02T12:44:55+08:00"
                    }
                ],
                "resourceType": "DiagnosticReport"
            },
            "request": {
                "method": "POST",
                "url": "DiagnosticReport"
            }
        },
        
        {
            "resource": {
                "id": "Condition-Diabetes",
                "code": {
                    "text": "diabetes"
                },
                "subject": {
                    "reference": "Patient/97b51b8d-1d1b-497f-866c-8df5d6cc05a7"
                },
                "resourceType": "Condition"
            },
            "request": {
                "method": "POST",
                "url": "Condition"
            }
        },
        
        {
            "resource": {
                "id": "AllergyIntolerance-Peanut",
                "code": {
                    "text": "peanut"
                },
                "patient": {
                    "reference": "Patient/97b51b8d-1d1b-497f-866c-8df5d6cc05a7"
                },
                "resourceType": "AllergyIntolerance"
            },
            "request": {
                "method": "POST",
                "url": "AllergyIntolerancePeanut"
            }
        },
        
        {
            "resource": {
                "id": "AllergyIntolerance-Amoxicillin",
                "code": {
                    "text": "amoxicillin"
                },
                "patient": {
                    "reference": "Patient/97b51b8d-1d1b-497f-866c-8df5d6cc05a7"
                },
                "resourceType": "AllergyIntolerance"
            },
            "request": {
                "method": "POST",
                "url": "AllergyIntoleranceAmoxicillin"
            }
        }   
    ]
}
EOF

```

The server will response with status code `200`.

## Complete response bundle
The complete bundle returned from the nlp-insights service is stored in /tmp/output.json.

The formatted json can be viewed using `jq . /tmp/output.json`

The formatted response bundle is very large, and has not been included here. In the following sections we will extract interesting data and present it as tables.

## Returned Resources
Our first task is to determine which entries & resources are in the returned bundle.

*Bash command to extract bundle entries with resource ids as a table*<br/>

```
jq -r '["Method", "Resource Type", "Resource Id"], 
       ["---",    "---",           "---"], 
   (.entry[] | 
       [.request.method, .resource.resourceType, .resource.id]
   ) 
   | @tsv' \
 /tmp/output.json | column -t -o '|' -s $'\t'
```

The query shows us that five resources were returned in the bundle.

Method|Resource Type      |Resource Id
---   |---                |---
POST  |Condition          |
POST  |MedicationStatement|
PUT   |Condition          |Condition-Diabetes
PUT   |AllergyIntolerance |AllergyIntolerance-Peanut
PUT   |AllergyIntolerance |AllergyIntolerance-Amoxicillin


The resources within entries that have a method of "POST" have no resource id. This is because these resources were derived by the nlp-insights service. The resource id will be assigned by a FHIR server when it receives this bundle.

The resources within entries that have a method of "PUT" have been "enriched" by the nlp-insights service. The resource ids of these resources matches resources that were sent to nlp-insights for analysis. The nlp-insights service has added additional codes to these resources.

## Assign resource ids
The FHIR server will assign id values to the dervied resources, but for these examples we will use jq to assign id values to these resources ourselves. This will make it easier to understand future examples, and does not require a FHIR server, however the FHIR server should be used to assign ids in normal uses.

We'll store the modified json in a new file /tmp/output_with_ids.json so there is no confusion later.

```
jq '.entry = [
                foreach .entry[] as $entry (0; . + 1;  . as $counter | $entry | 
                  if  ($entry.resource | has("id")) 
                  then . 
                  else (.resource.id = ("Derived-Resource-" + ($counter | tostring))) end  )
             ]' /tmp/output.json  > /tmp/output_with_ids.json
```

We've now assigned resource ids to make our example queries easier.

```
jq -r '["Method", "Resource Type", "Resource Id"], 
       ["---",    "---",           "---"], 
   (.entry[] | 
       [.request.method, .resource.resourceType, .resource.id]
   ) 
   | @tsv' \
 /tmp/output_with_ids.json | column -t -o '|' -s $'\t'
```

The above query shows the new ids:

Method|Resource Type      |Resource Id
---   |---                |---
POST  |Condition          |Derived-Resource-1
POST  |MedicationStatement|Derived-Resource-2
PUT   |Condition          |Condition-Diabetes
PUT   |AllergyIntolerance |AllergyIntolerance-Peanut
PUT   |AllergyIntolerance |AllergyIntolerance-Amoxicillin

## Alvearie data model
The nlp-insights service uses the Alvearie FHIR IG to ensure that the returned data can be consumed by other services. The IG documentation can be found [here](https://alvearie.io/alvearie-fhir-ig/index.html).

## Insight Extension
The Alveearie IG defines an insight extension; the nlp-insights service will add this extension to the meta of each resource that is contained in the returned bundle.

The current implementation of the nlp-insights service adds only one insight per REST call, however this could change to return multiple insights in the future. It is also possible that other services add additional insights. All queries should assume that there could be more than one insight defined in the resource meta.

The definition of the structure is defined [here](https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight.html). The nlp-insights service does not provide data for all fields.

The next sections explain how to use the FHIR artificats contained within the insight extension.

### Insight ID
The insight ID extension identifies the insight. It contains to elements:

* System - the system used to produce the insight id (or the insight)
* Value - unique id for the insight (within the system)

The id is important because it differentiates the insight from other insights on this resource or other resources.

A jq filter can be used to extract the insight identifiers and convert them to a table format.

<details>
<summary>Filter to produce insight id as table (filter.jq)</summary>

```
# Returns a list of insight extensions in an element's extension list
def get_insight_exts: .extension?[]? | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight");

# Reurns a list of insight-id extensions in an element's extension list
def get_insight_id_ext: .extension?[]? | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-id");

# returns an HTML table with the specified system and value
def print_id($system; $value): "<table><thead><tr><th>System</th><th>Value</th></tr></thead>" +
                                 "<tbody> <tr><td> \($system) </td><td>\($value)</td></tr></tbody> " +
                                 "</table>";

# Header rows
["Method", "Resource Type", "Resource ID", "Insight ID"], 
["---",    "---",           "---",         "---"],

# Rows
(.entry[] | 
          [.request.method,
           .resource.resourceType,
           .resource.id,
           (.resource.meta | get_insight_exts | get_insight_id_ext | print_id(.valueIdentifier.system; .valueIdentifier.value))
           ]
       ) | @tsv
```

</details>
<br/>

The filter can be combined with other bash commands to produce github markdown to view the IDs as a [table](#table-insight-ids-in-returned-resources). 

`jq -r -f filter.jq  /tmp/output_with_ids.json | column -t -o "|" -s $'\t'`


#### Table: Insight IDs in Returned resources

Method|Resource Type      |Resource ID                   |Insight ID
---   |---                |---                           |---
POST  |Condition          |Derived-Resource-1            |<table><thead><tr><th>System</th><th>Value</th></tr></thead> <tbody> <tr><td>urn:alvearie.io/health_patterns/services/nlp_insights/acd</td><td>667127978309fa12c3bb1697a3c0ea73b25a589ece66782734b7be7b</td></tr></tbody></table>
POST  |MedicationStatement|Derived-Resource-2            |<table><thead><tr><th>System</th><th>Value</th></tr></thead> <tbody> <tr><td>urn:alvearie.io/health_patterns/services/nlp_insights/acd</td><td>310f7e69b54a711d8019f41b029cba5a03340c4ffc0f2a16c5f9f85a</td></tr></tbody></table>
PUT   |Condition          |Condition-Diabetes            |<table><thead><tr><th>System</th><th>Value</th></tr></thead> <tbody> <tr><td>urn:alvearie.io/health_patterns/services/nlp_insights/acd</td><td>f21bea30fc146536f989218626ae763ccbaacf58032dab4536d20ef7</td></tr></tbody></table>
PUT   |AllergyIntolerance |AllergyIntolerance-Peanut     |<table><thead><tr><th>System</th><th>Value</th></tr></thead> <tbody> <tr><td>urn:alvearie.io/health_patterns/services/nlp_insights/acd</td><td>7cea616a598e2c7bf9dcefe25233a19f34da47305ba8fa93676a16e7</td></tr></tbody></table>
PUT   |AllergyIntolerance |AllergyIntolerance-Amoxicillin|<table><thead><tr><th>System</th><th>Value</th></tr></thead> <tbody> <tr><td>urn:alvearie.io/health_patterns/services/nlp_insights/acd</td><td>841ef5e36b376345cf6e0cf7b39ba45667b33feda25d0903dff2631c</td></tr></tbody></table>

<br/>
The system values tell us that all of these insights were created using ACD.



### Insight Path
The insight path is a [FHIR Path](https://www.hl7.org/fhir/fhirpath.html) that explains what the insight applies to. Each insight has exactly one path associated with it.

A jq filter can be used to extract the insights' path and convert them to a table format.

<details>
<summary>Filter to produce insight path in a table (filter.jq)</summary>

```
# Returns a list of insight extensions in an element's extension list
def get_insight_exts: .extension?[]? | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight");

# Returns a list of insight-id extensions in an element's extension list
def get_insight_id_ext: .extension?[]? | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-id");

# Returns the path extension
def get_insight_path_ext: .extension?[]? | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/path");

# Formats the resource id to be shorter and easier to read
def print_id($system; $value): "***" + $value[-7:];
###
# Main Query
###

# Header rows
["Resource ID", "Insight ID", "Insight Path"], 
["---",         "---",        "----"],

# Rows
(.entry[] |
          [.resource.id,
           ((.resource.meta | get_insight_exts ) |  (get_insight_id_ext | print_id(.valueIdentifier.system; .valueIdentifier.value)),
                                                    (get_insight_path_ext.valueString)
           )
           ]
       ) | @tsv
```

</details>
<br/>

A bash command then be used to produce the table

`jq -r -f filter.jq  /tmp/output_with_ids.json | column -t -o "|" -s $'\t'`

Resource ID                   |Insight ID|Insight Path
---                           |---       |----
Derived-Resource-1            |***4b7be7b|Condition
Derived-Resource-2            |***5f9f85a|MedicationStatement
Condition-Diabetes            |***6d20ef7|Condition.code.coding
AllergyIntolerance-Peanut     |***76a16e7|AllergyIntolerance.code.coding
AllergyIntolerance-Amoxicillin|***ff2631c|AllergyIntolerance.code.coding

For Derived-Resource-1 and Derived-Resource-2, the insight applies to the entire resource. Since the other resources were enriched by the service, the path is path to the coding where additional codes were added.

### Insight Details

The details section of the insight contains information about what caused the insight to be created. The Alvearie IG allows for multiple details extensions within an insight, however the nlp-insights service creates only one. The simplify the queries, only the first details extension is
examined.

The important artifacts with the details section are:
* Reference - the resource that this insight was derived from
* Reference-path - the path within *Reference* that this insight was derived from
* Evaluated-output - attachment with the data structure that was returned from the nlp service (in base64).
* Insight-result - complex structure that contains spans and confidences

We can expand our jq query to include the reference and reference-path for the insight to our table. 
