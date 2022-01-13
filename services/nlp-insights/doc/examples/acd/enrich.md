# OUTPUT OBSOLETE

# Enrich FHIR resources with nlp-insights and ACD
The nlp-insights service supports enrichment of the following types of FHIR resources:

* Condition
* AllergyIntolerance

A resource is enriched by adding industry standard codes to the resource. These standard codes are derived from a resource's coding text using NLP. This particularly useful when a FHIR resource has a text description of the code, but does not contain industry standard codes such as SNOMED, ICD-9, ICD-10, etc.

This tutorial provides examples of enrichment.

## Configure nlp-insights to use ACD for NLP
If the nlp-insights service has not been configured to use ACD by default, follow the steps [here](./configure_acd.md).

## Enrich a Condition

In this example, the nlp-insights service is sent a bundle that contains a single condition. The condition has a code with text "myocardial infarction", but no coding values. The service will add coding values to the code. This curl command is written to store the response in a file /tmp/output for later analysis.

```
curl  -w "\n%{http_code}\n" -s -o /tmp/output -XPOST localhost:5000/discoverInsights  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
    "resourceType": "Bundle",
    "id": "abc",
    "type": "transaction",
    "entry": [
        {
            "resource": {
                "id": "abcefg-1234567890",
                "code": {
                    "text": "myocardial infarction"
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
        }
    ]
}
EOF
```

<details><summary>output</summary>

200

</details>

### Enriched condition
The response from the service is a bundle with the enriched condition.

`cat /tmp/output | jq`

<details><summary>Returned Bundle</summary>

```json
{
  "entry": [
    {
      "request": {
        "method": "PUT",
        "url": "Condition/abcefg-1234567890"
      },
      "resource": {
        "id": "abcefg-1234567890",
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                    "value": "f5d5c76179f75f1883c92a6ef73d6cd9a103673518cabe2b38b7a180"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition.code.coding"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "Condition/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "Condition.code.text"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDAsICJlbmQiOiAyMSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJwcmVmZXJyZWROYW1lIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJ2YWx1ZXMiOiBbeyJ2YWx1ZSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24ifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA1fSwgIm5hbWUiOiAiRGlhZ25vc2lzIiwgImljZDlDb2RlIjogIjQxMC45MCIsICJpY2QxMENvZGUiOiAiSTIxLjkiLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjkxNywgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDgsICJkaXNjdXNzZWRTY29yZSI6IDAuMDc1fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wOTIsICJzeW1wdG9tU2NvcmUiOiAwLjAsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX0sICJjY3NDb2RlIjogIjEwMCIsICJoY2NDb2RlIjogIjg2In1dLCAiY29uY2VwdHMiOiBbeyJ0eXBlIjogInVtbHMuRmluZGluZyIsICJiZWdpbiI6IDAsICJlbmQiOiAyMSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzQ1NTI5NTkiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24sIENUQ0FFIiwgInNlbWFudGljVHlwZSI6ICJmbmRnIiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzE0MzY5MSIsICJ2b2NhYnMiOiAiTVRILE5DSV9DVENBRV81LE5DSSJ9LCB7InR5cGUiOiAidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0IiwgInVpZCI6IDMsICJiZWdpbiI6IDAsICJlbmQiOiAyMSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzA0Mjg5NTMiLCAicHJlZmVycmVkTmFtZSI6ICJFbGVjdHJvY2FyZGlvZ3JhbTogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIChmaW5kaW5nKSIsICJzZW1hbnRpY1R5cGUiOiAibGJ0ciIsICJzb3VyY2UiOiAidW1scyIsICJzb3VyY2VWZXJzaW9uIjogIjIwMjBBQSIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIklOVkFMSUQifSwgImljZDEwQ29kZSI6ICJJMjEuNCxJMjEuMjksSTIxLjA5LEkyMS4xOSxSOTQuMzEsSTI1LjIsSTIxLjkiLCAibmNpQ29kZSI6ICJDMTAxNTg5IiwgInNub21lZENvbmNlcHRJZCI6ICIxNjQ4NjUwMDUiLCAidm9jYWJzIjogIkNIVixNVEgsTkNJX0NESVNDLE5DSSxTTk9NRURDVF9VUyJ9LCB7InR5cGUiOiAidW1scy5EaXNlYXNlT3JTeW5kcm9tZSIsICJ1aWQiOiAyLCAiYmVnaW4iOiAwLCAiZW5kIjogMjEsICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMDI3MDUxIiwgInByZWZlcnJlZE5hbWUiOiAiTXlvY2FyZGlhbCBJbmZhcmN0aW9uIiwgInNlbWFudGljVHlwZSI6ICJkc3luIiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgImljZDEwQ29kZSI6ICJJMjEuOSIsICJuY2lDb2RlIjogIkMyNzk5NiIsICJzbm9tZWRDb25jZXB0SWQiOiAiMjIyOTgwMDYiLCAibWVzaElkIjogIk0wMDE0MzQwIiwgImxvaW5jSWQiOiAiTVRIVTAzNTU1MSxMQTE0Mjc0LTcsTFA5ODg4NC03LExBMTYyODYtOSIsICJ2b2NhYnMiOiAiTkNJX05JQ0hELE1USCxMTkMsQ1NQLE1TSCxDU1QsSFBPLE9NSU0sTkNJX0NUQ0FFLENPU1RBUixBSVIsQ0hWLE5DSV9GREEsTUVETElORVBMVVMsTkNJLExDSF9OVyxBT0QsU05PTUVEQ1RfVVMsRFhQIiwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjkxNywgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDgsICJkaXNjdXNzZWRTY29yZSI6IDAuMDc1fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wOTIsICJzeW1wdG9tU2NvcmUiOiAwLjAsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAwLCAiZW5kIjogMjEsICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMDI3MDUxIiwgInByZWZlcnJlZE5hbWUiOiAiTXlvY2FyZGlhbCBJbmZhcmN0aW9uIiwgInNvdXJjZSI6ICJDbGluaWNhbCBJbnNpZ2h0cyAtIERlcml2ZWQgQ29uY2VwdHMiLCAic291cmNlVmVyc2lvbiI6ICJ2MS4wIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImljZDEwQ29kZSI6ICJJMjEuOSIsICJuY2lDb2RlIjogIkMyNzk5NiIsICJzbm9tZWRDb25jZXB0SWQiOiAiMjIyOTgwMDYiLCAibWVzaElkIjogIk0wMDE0MzQwIiwgImxvaW5jSWQiOiAiTVRIVTAzNTU1MSxMQTE0Mjc0LTcsTFA5ODg4NC03LExBMTYyODYtOSIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC45MTcsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA4LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA3NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMDkyLCAic3ltcHRvbVNjb3JlIjogMC4wLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjAwM319LCAicnVsZUlkIjogIjY5OGYyYjE5LTI3YjYtNGRhYi05MTUwLTdkN2VmM2IwM2E1YyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDJ9XX0sIHsidHlwZSI6ICJJQ05vcm1hbGl0eSIsICJiZWdpbiI6IDAsICJlbmQiOiAyMSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzA0Mjg5NTMiLCAicHJlZmVycmVkTmFtZSI6ICJFbGVjdHJvY2FyZGlvZ3JhbTogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIChmaW5kaW5nKSIsICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBEZXJpdmVkIENvbmNlcHRzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIklOVkFMSUQifSwgInJ1bGVJZCI6ICJjMWU4ZDdkNC03ZDM2LTQyM2ItYjM5ZC00ZWJiNWViNjViMGMiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAzfV19XSwgIlN5bXB0b21EaXNlYXNlSW5kIjogW3sidHlwZSI6ICJhY2kuU3ltcHRvbURpc2Vhc2VJbmQiLCAidWlkIjogNSwgImJlZ2luIjogMCwgImVuZCI6IDIxLCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibW9kYWxpdHkiOiAicG9zaXRpdmUiLCAic3ltcHRvbURpc2Vhc2VTdXJmYWNlRm9ybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgImNjc0NvZGUiOiAiMTAwIiwgInN5bXB0b21EaXNlYXNlTm9ybWFsaXplZE5hbWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgImljZDlDb2RlIjogIjQxMC45MCIsICJoY2NDb2RlIjogIjg2IiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjkxNywgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDgsICJkaXNjdXNzZWRTY29yZSI6IDAuMDc1fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wOTIsICJzeW1wdG9tU2NvcmUiOiAwLjAsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX19XSwgInNwZWxsQ29ycmVjdGVkVGV4dCI6IFt7ImNvcnJlY3RlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn1dfQ=="
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "code": {
          "coding": [
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "f5d5c76179f75f1883c92a6ef73d6cd9a103673518cabe2b38b7a180"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "C0027051",
              "display": "myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "f5d5c76179f75f1883c92a6ef73d6cd9a103673518cabe2b38b7a180"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "22298006",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "f5d5c76179f75f1883c92a6ef73d6cd9a103673518cabe2b38b7a180"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "410.90",
              "system": "http://hl7.org/fhir/sid/icd-9-cm"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "f5d5c76179f75f1883c92a6ef73d6cd9a103673518cabe2b38b7a180"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "I21.9",
              "system": "http://hl7.org/fhir/sid/icd-10-cm"
            }
          ],
          "text": "myocardial infarction"
        },
        "subject": {
          "reference": "Patient/97b51b8d-1d1b-497f-866c-8df5d6cc05a7"
        },
        "resourceType": "Condition"
      }
    }
  ],
  "type": "transaction",
  "resourceType": "Bundle"
}
```
</details>

The entry for the condition in the returned bundle has a method of *PUT*, which indicates that this resource has been enriched with additional codes.

### Condition derived codes
ACD understands a wide variety of standard code systems. As a result SNOMED, ICD-9 and ICD-10 coding values are included in the condition, in addition to the UMLS concept id.

<!--
code to generate the table

cat /tmp/output | jq -r '
["System", "Code", "Display"],
["------", "----", "----"], 
(.entry[0].resource.code.coding[] | [.system, .code, .display]) 
| @tsv' | column -t -o '|' -s $'\t'

-->

System                                    |Code    |Display
------                                    |----    |----
http://terminology.hl7.org/CodeSystem/umls|C0027051|myocardial infarction
http://snomed.info/sct                    |22298006|
http://hl7.org/fhir/sid/icd-9-cm          |410.90  |
http://hl7.org/fhir/sid/icd-10-cm         |I21.9   |


## Enrich an allergy intolerance
In this example, a bundle with two allergy intolerance resources is sent to the nlp insights server. The first has a code for a food allergy with text "peanut", and the second resource has a code for a medication allergy with text "amoxicillin".

Both resources contain only text and do not contain any codes for the allergy. The nlp-insights service will enrich the resources by adding UMLS, SNOMED, ICD-9 and ICD-10 codes.

```
curl  -w "\n%{http_code}\n" -s -o /tmp/output -XPOST localhost:5000/discoverInsights  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
    "resourceType": "Bundle",
    "id": "abc",
    "type": "transaction",
    "entry": [
        {
            "resource": {
                "id": "pnt123",
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
                "url": "Condition"
            }
        },
        {
            "resource": {
                "id": "amx123",
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
                "url": "Condition"
            }
        }

    ]
}
EOF
```

<details><summary>output</summary>

200

</details>

A bundle is returned that contains the enriched allergy intolerance resources. Both entries in the bundle have method *PUT*, indicating that these contain enriched resources. Each resource now contains the additional derived code values.

`cat /tmp/output | jq`

<details><summary>Returned bundle</summary>

```
{
  "entry": [
    {
      "request": {
        "method": "PUT",
        "url": "AllergyIntolerance/pnt123"
      },
      "resource": {
        "id": "pnt123",
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                    "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "AllergyIntolerance.code.coding"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "AllergyIntolerance/pnt123"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "AllergyIntolerance.code.text"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDAsICJlbmQiOiAxNCwgImNvdmVyZWRUZXh0IjogInBlYW51dCBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgInByZWZlcnJlZE5hbWUiOiAiYWxsZXJneSB0byBwZWFudXQiLCAidmFsdWVzIjogW3sidmFsdWUiOiAiYWxsZXJneSB0byBwZWFudXQifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA0fSwgIm5hbWUiOiAiRGlhZ25vc2lzIiwgImljZDlDb2RlIjogIjk5NS4zIiwgImljZDEwQ29kZSI6ICJaOTEuMDEwLFo5MS4wIiwgInNub21lZENvbmNlcHRJZCI6ICI5MTkzNTAwOSIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC44OTYsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA5LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA5NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMTA5LCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX0sICJjY3NDb2RlIjogIjI1MyJ9XSwgImNvbmNlcHRzIjogW3sidHlwZSI6ICJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIiwgInVpZCI6IDIsICJiZWdpbiI6IDAsICJlbmQiOiAxNCwgImNvdmVyZWRUZXh0IjogInBlYW51dCBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDU1OTQ3MCIsICJwcmVmZXJyZWROYW1lIjogIkFsbGVyZ3kgdG8gcGVhbnV0cyIsICJzZW1hbnRpY1R5cGUiOiAiZHN5biIsICJzb3VyY2UiOiAidW1scyIsICJzb3VyY2VWZXJzaW9uIjogIjIwMjBBQSIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIk5PX0RFQ0lTSU9OIn0sICJpY2Q5Q29kZSI6ICI5OTUuMyIsICJpY2QxMENvZGUiOiAiWjkxLjAsWjkxLjAxMCIsICJzbm9tZWRDb25jZXB0SWQiOiAiOTE5MzUwMDkiLCAibWVzaElkIjogIk0wMzUxODM2IiwgInZvY2FicyI6ICJNVEgsQ0hWLE1TSCxNRURMSU5FUExVUyxTTk9NRURDVF9VUyIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC44OTYsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA5LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA5NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMTA5LCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAwLCAiZW5kIjogMTQsICJjb3ZlcmVkVGV4dCI6ICJwZWFudXQgYWxsZXJneSIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzA1NTk0NzAiLCAicHJlZmVycmVkTmFtZSI6ICJBbGxlcmd5IHRvIHBlYW51dHMiLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaWNkOUNvZGUiOiAiOTk1LjMiLCAiaWNkMTBDb2RlIjogIlo5MS4wLFo5MS4wMTAiLCAic25vbWVkQ29uY2VwdElkIjogIjkxOTM1MDA5IiwgIm1lc2hJZCI6ICJNMDM1MTgzNiIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC44OTYsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA5LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA5NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMTA5LCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX0sICJydWxlSWQiOiAiNjk4ZjJiMTktMjdiNi00ZGFiLTkxNTAtN2Q3ZWYzYjAzYTVjIiwgImRlcml2ZWRGcm9tIjogW3sidWlkIjogMn1dfV0sICJTeW1wdG9tRGlzZWFzZUluZCI6IFt7InR5cGUiOiAiYWNpLlN5bXB0b21EaXNlYXNlSW5kIiwgInVpZCI6IDQsICJiZWdpbiI6IDAsICJlbmQiOiAxNCwgImNvdmVyZWRUZXh0IjogInBlYW51dCBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDU1OTQ3MCIsICJpY2QxMENvZGUiOiAiWjkxLjAxMCxaOTEuMCIsICJtb2RhbGl0eSI6ICJwb3NpdGl2ZSIsICJzeW1wdG9tRGlzZWFzZVN1cmZhY2VGb3JtIjogInBlYW51dCBhbGxlcmd5IiwgInNub21lZENvbmNlcHRJZCI6ICI5MTkzNTAwOSIsICJjY3NDb2RlIjogIjI1MyIsICJzeW1wdG9tRGlzZWFzZU5vcm1hbGl6ZWROYW1lIjogImFsbGVyZ3kgdG8gcGVhbnV0IiwgImljZDlDb2RlIjogIjk5NS4zIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjg5NiwgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDksICJkaXNjdXNzZWRTY29yZSI6IDAuMDk1fSwgInN1c3BlY3RlZFNjb3JlIjogMC4xMDksICJzeW1wdG9tU2NvcmUiOiAwLjAwMSwgInRyYXVtYVNjb3JlIjogMC4wLCAiZmFtaWx5SGlzdG9yeVNjb3JlIjogMC4wMDN9fX1dLCAic3BlbGxDb3JyZWN0ZWRUZXh0IjogW3siY29ycmVjdGVkVGV4dCI6ICJwZWFudXQgYWxsZXJneSJ9XX0="
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "code": {
          "coding": [
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "C0559470",
              "display": "allergy to peanut",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "91935009",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "995.3",
              "system": "http://hl7.org/fhir/sid/icd-9-cm"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "Z91.010",
              "system": "http://hl7.org/fhir/sid/icd-10-cm"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "Z91.0",
              "system": "http://hl7.org/fhir/sid/icd-10-cm"
            }
          ],
          "text": "peanut"
        },
        "patient": {
          "reference": "Patient/97b51b8d-1d1b-497f-866c-8df5d6cc05a7"
        },
        "resourceType": "AllergyIntolerance"
      }
    },
    {
      "request": {
        "method": "PUT",
        "url": "AllergyIntolerance/amx123"
      },
      "resource": {
        "id": "amx123",
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                    "value": "eab3b2e367a16867de5b9249611542d2bd3df1f934db118237e31c2e"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "AllergyIntolerance.code.coding"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "AllergyIntolerance/amx123"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "AllergyIntolerance.code.text"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDAsICJlbmQiOiAxOSwgImNvdmVyZWRUZXh0IjogImFtb3hpY2lsbGluIGFsbGVyZ3kiLCAibmVnYXRlZCI6IGZhbHNlLCAicHJlZmVycmVkTmFtZSI6ICJhbGxlcmd5IHRvIGFtb3hpY2lsbGluIiwgInZhbHVlcyI6IFt7InZhbHVlIjogImFsbGVyZ3kgdG8gYW1veGljaWxsaW4ifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA0fSwgIm5hbWUiOiAiRGlhZ25vc2lzIiwgImljZDlDb2RlIjogIkU5MzAuMCw5OTUuMjciLCAiaWNkMTBDb2RlIjogIlo4OC4wIiwgInNub21lZENvbmNlcHRJZCI6ICIyOTQ1MDUwMDgiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTE5LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwNywgImRpc2N1c3NlZFNjb3JlIjogMC4wNzV9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjA5NiwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjAwNH19LCAiY2NzQ29kZSI6ICIyNTMifV0sICJjb25jZXB0cyI6IFt7InR5cGUiOiAidW1scy5EaXNlYXNlT3JTeW5kcm9tZSIsICJ1aWQiOiAyLCAiYmVnaW4iOiAwLCAiZW5kIjogMTksICJjb3ZlcmVkVGV4dCI6ICJhbW94aWNpbGxpbiBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDU3MTQxNyIsICJwcmVmZXJyZWROYW1lIjogIkFsbGVyZ3kgdG8gYW1veGljaWxsaW4iLCAic2VtYW50aWNUeXBlIjogImRzeW4iLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAiaWNkOUNvZGUiOiAiOTk1LjI3IiwgImljZDEwQ29kZSI6ICJaODguMCxaODguMSIsICJzbm9tZWRDb25jZXB0SWQiOiAiMjk0NTA1MDA4IiwgInZvY2FicyI6ICJDSFYsU05PTUVEQ1RfVVMiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTE5LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwNywgImRpc2N1c3NlZFNjb3JlIjogMC4wNzV9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjA5NiwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjAwNH19fSwgeyJ0eXBlIjogIklDRGlhZ25vc2lzIiwgImJlZ2luIjogMCwgImVuZCI6IDE5LCAiY292ZXJlZFRleHQiOiAiYW1veGljaWxsaW4gYWxsZXJneSIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzA1NzE0MTciLCAicHJlZmVycmVkTmFtZSI6ICJBbGxlcmd5IHRvIGFtb3hpY2lsbGluIiwgInNvdXJjZSI6ICJDbGluaWNhbCBJbnNpZ2h0cyAtIERlcml2ZWQgQ29uY2VwdHMiLCAic291cmNlVmVyc2lvbiI6ICJ2MS4wIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImljZDlDb2RlIjogIjk5NS4yNyIsICJpY2QxMENvZGUiOiAiWjg4LjAsWjg4LjEiLCAic25vbWVkQ29uY2VwdElkIjogIjI5NDUwNTAwOCIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC45MTksICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA3LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA3NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMDk2LCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDA0fX0sICJydWxlSWQiOiAiNjk4ZjJiMTktMjdiNi00ZGFiLTkxNTAtN2Q3ZWYzYjAzYTVjIiwgImRlcml2ZWRGcm9tIjogW3sidWlkIjogMn1dfV0sICJNZWRpY2F0aW9uSW5kIjogW3sidHlwZSI6ICJhY2kuTWVkaWNhdGlvbkluZCIsICJiZWdpbiI6IDAsICJlbmQiOiAxMSwgImNvdmVyZWRUZXh0IjogImFtb3hpY2lsbGluIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAwMjY0NSIsICJkcnVnIjogW3siY292ZXJlZFRleHQiOiAiYW1veGljaWxsaW4iLCAiY3VpIjogIkMwMDAyNjQ1IiwgImNvbXBsZXgiOiAiZmFsc2UiLCAiZW5kIjogMTEsICJ0eXBlIjogImFjaS5JbmRfRHJ1ZyIsICJuYW1lMSI6IFt7InJ4Tm9ybUlEIjogIjcyMyIsICJjb3ZlcmVkVGV4dCI6ICJhbW94aWNpbGxpbiIsICJjdWkiOiAiQzAwMDI2NDUiLCAiZHJ1Z1N1cmZhY2VGb3JtIjogImFtb3hpY2lsbGluIiwgImRydWdOb3JtYWxpemVkTmFtZSI6ICJhbW94aWNpbGxpbiIsICJlbmQiOiAxMSwgInR5cGUiOiAiYWNpLkRydWdOYW1lIiwgImJlZ2luIjogMH1dLCAiYmVnaW4iOiAwfV0sICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIklOVkFMSUQiLCAiY29tbWVudCI6ICJDbGluaWNhbCBJbnNpZ2h0czogVGhpcyBjb25jZXB0IHdhcyBzaG9ydGVyIHRoYW4gYW4gb3ZlcmxhcHBpbmcgY29uY2VwdC4ifX1dLCAiU3ltcHRvbURpc2Vhc2VJbmQiOiBbeyJ0eXBlIjogImFjaS5TeW1wdG9tRGlzZWFzZUluZCIsICJ1aWQiOiA0LCAiYmVnaW4iOiAwLCAiZW5kIjogMTksICJjb3ZlcmVkVGV4dCI6ICJhbW94aWNpbGxpbiBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDU3MTQxNyIsICJpY2QxMENvZGUiOiAiWjg4LjAiLCAibW9kYWxpdHkiOiAicG9zaXRpdmUiLCAic3ltcHRvbURpc2Vhc2VTdXJmYWNlRm9ybSI6ICJhbW94aWNpbGxpbiBhbGxlcmd5IiwgInNub21lZENvbmNlcHRJZCI6ICIyOTQ1MDUwMDgiLCAiY2NzQ29kZSI6ICIyNTMiLCAic3ltcHRvbURpc2Vhc2VOb3JtYWxpemVkTmFtZSI6ICJhbGxlcmd5IHRvIGFtb3hpY2lsbGluIiwgImljZDlDb2RlIjogIkU5MzAuMCw5OTUuMjciLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTE5LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwNywgImRpc2N1c3NlZFNjb3JlIjogMC4wNzV9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjA5NiwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjAwNH19fV0sICJzcGVsbENvcnJlY3RlZFRleHQiOiBbeyJjb3JyZWN0ZWRUZXh0IjogImFtb3hpY2lsbGluIGFsbGVyZ3kifV19"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "code": {
          "coding": [
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "eab3b2e367a16867de5b9249611542d2bd3df1f934db118237e31c2e"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "C0571417",
              "display": "allergy to amoxicillin",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "eab3b2e367a16867de5b9249611542d2bd3df1f934db118237e31c2e"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "294505008",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "eab3b2e367a16867de5b9249611542d2bd3df1f934db118237e31c2e"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "E930.0",
              "system": "http://hl7.org/fhir/sid/icd-9-cm"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "eab3b2e367a16867de5b9249611542d2bd3df1f934db118237e31c2e"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "995.27",
              "system": "http://hl7.org/fhir/sid/icd-9-cm"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                        "value": "eab3b2e367a16867de5b9249611542d2bd3df1f934db118237e31c2e"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
                      "valueCodeableConcept": {
                        "coding": [
                          {
                            "code": "natural-language-processing",
                            "display": "NLP",
                            "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
                          }
                        ],
                        "text": "NLP"
                      }
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
                }
              ],
              "code": "Z88.0",
              "system": "http://hl7.org/fhir/sid/icd-10-cm"
            }
          ],
          "text": "amoxicillin"
        },
        "patient": {
          "reference": "Patient/97b51b8d-1d1b-497f-866c-8df5d6cc05a7"
        },
        "resourceType": "AllergyIntolerance"
      }
    }
  ],
  "type": "transaction",
  "resourceType": "Bundle"
}
```
</details>

### Allergy derived codes
The food allergy resource has been enriched with new codes.

<!--
code to generate the table

cat /tmp/output | jq -r '["System", "Code", "Display"], ["---", "---", "---"], (.entry[].resource | select(.id == "pnt123") | .code.coding[] | [.system,  .code, .display]) | @tsv' | column -t -s $'\t' -o "|"
-->

System                                    |Code    |Display
---                                       |---     |---
http://terminology.hl7.org/CodeSystem/umls|C0559470|allergy to peanut
http://snomed.info/sct                    |91935009|
http://hl7.org/fhir/sid/icd-9-cm          |995.3   |
http://hl7.org/fhir/sid/icd-10-cm         |Z91.010 |
http://hl7.org/fhir/sid/icd-10-cm         |Z91.0   |

In a similar way, the medication allergy resource has been enriched with new codes.

<!--
code to generate table

cat /tmp/output | jq -r '["System", "Code", "Display"], ["---", "---", "---"], (.entry[].resource | select(.id == "amx123") | .code.coding[] | [.system,  .code, .display]) | @tsv' | column -t -s $'\t' -o "|"

-->


System                                    |Code     |Display
---                                       |---      |---
http://terminology.hl7.org/CodeSystem/umls|C0571417 |allergy to amoxicillin
http://snomed.info/sct                    |294505008|
http://hl7.org/fhir/sid/icd-9-cm          |E930.0   |
http://hl7.org/fhir/sid/icd-9-cm          |995.27   |
http://hl7.org/fhir/sid/icd-10-cm         |Z88.0    |




## Evidence
nlp-insights enriches resources according to the [Alvearie FHIR IG](https://alvearie.io/alvearie-fhir-ig/index.html).

The nlp-insights service adds detailed information to the enriched resource to explain what caused the additional codes to be added.

### Insight Summary
Each coding that has been derived by NLP contains an insight summary extension that can be examined to determine which insight derived the code.

For example consider the UMLS code C0559470 that was added to the allergy intolerance resource pnt123.

<!--
code to extract json object

cat /tmp/output | jq -r '
.entry[].resource | 
select(.id == "pnt123") |
.code.coding[] | 
select(.code == "C0559470" and .system == "http://terminology.hl7.org/CodeSystem/umls")`
-->

<details><summary>C0559470 coding in AllergyIntolerance pnt123</summary>

```json
{
  "extension": [
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
          "valueIdentifier": {
            "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
            "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
          }
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
          "valueCodeableConcept": {
            "coding": [
              {
                "code": "natural-language-processing",
                "display": "NLP",
                "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
              }
            ],
            "text": "NLP"
          }
        }
      ],
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
    }
  ],
  "code": "C0559470",
  "display": "allergy to peanut",
  "system": "http://terminology.hl7.org/CodeSystem/umls"
}
```

</details><BR/>

The summary extension has been added to the coding. The summary has an insight id and category.
The insight id has a system and identifier that together identify the insight. In this example, the system tells us that the insight was discovered using ACD. The identifier value is unique (within the system) to this insight, and may be used to find the insight extension for the insight in the resource meta.

When nlp-insights derives codes, it will create one insight for all derived codes that are created from the same text. It is common for all summary extensions to refer to the same insight id.

The category tells us that the coding was derived using Natural Language Processing.

### Insight Extension in Resource Meta
The insight identified by the summary extension has an insight extension in the resource's meta. The insight extension contains lots of details about what the insight applies to and why it was created. 


<!-- 
 jq code to extract the extension
 
cat /tmp/output | jq -r ' .entry[].resource | select(.id == "pnt123").meta.extension[0]'

-->

<details><summary>Insight extension in the meta for AllergyIntolerance pnt123</summary>

```json
{
  "extension": [
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
      "valueIdentifier": {
        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
        "value": "dced3e94fd2e5a77e6b6beb78019b1a89f17cb0a2731c4e31c24c5e4"
      }
    },
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
      "valueString": "AllergyIntolerance.code.coding"
    },
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
          "valueReference": {
            "reference": "AllergyIntolerance/pnt123"
          }
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
          "valueString": "AllergyIntolerance.code.text"
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
          "valueAttachment": {
            "contentType": "application/json",
            "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDAsICJlbmQiOiAxNCwgImNvdmVyZWRUZXh0IjogInBlYW51dCBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgInByZWZlcnJlZE5hbWUiOiAiYWxsZXJneSB0byBwZWFudXQiLCAidmFsdWVzIjogW3sidmFsdWUiOiAiYWxsZXJneSB0byBwZWFudXQifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA0fSwgIm5hbWUiOiAiRGlhZ25vc2lzIiwgImljZDlDb2RlIjogIjk5NS4zIiwgImljZDEwQ29kZSI6ICJaOTEuMDEwLFo5MS4wIiwgInNub21lZENvbmNlcHRJZCI6ICI5MTkzNTAwOSIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC44OTYsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA5LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA5NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMTA5LCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX0sICJjY3NDb2RlIjogIjI1MyJ9XSwgImNvbmNlcHRzIjogW3sidHlwZSI6ICJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIiwgInVpZCI6IDIsICJiZWdpbiI6IDAsICJlbmQiOiAxNCwgImNvdmVyZWRUZXh0IjogInBlYW51dCBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDU1OTQ3MCIsICJwcmVmZXJyZWROYW1lIjogIkFsbGVyZ3kgdG8gcGVhbnV0cyIsICJzZW1hbnRpY1R5cGUiOiAiZHN5biIsICJzb3VyY2UiOiAidW1scyIsICJzb3VyY2VWZXJzaW9uIjogIjIwMjBBQSIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIk5PX0RFQ0lTSU9OIn0sICJpY2Q5Q29kZSI6ICI5OTUuMyIsICJpY2QxMENvZGUiOiAiWjkxLjAsWjkxLjAxMCIsICJzbm9tZWRDb25jZXB0SWQiOiAiOTE5MzUwMDkiLCAibWVzaElkIjogIk0wMzUxODM2IiwgInZvY2FicyI6ICJNVEgsQ0hWLE1TSCxNRURMSU5FUExVUyxTTk9NRURDVF9VUyIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC44OTYsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA5LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA5NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMTA5LCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAwLCAiZW5kIjogMTQsICJjb3ZlcmVkVGV4dCI6ICJwZWFudXQgYWxsZXJneSIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzA1NTk0NzAiLCAicHJlZmVycmVkTmFtZSI6ICJBbGxlcmd5IHRvIHBlYW51dHMiLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaWNkOUNvZGUiOiAiOTk1LjMiLCAiaWNkMTBDb2RlIjogIlo5MS4wLFo5MS4wMTAiLCAic25vbWVkQ29uY2VwdElkIjogIjkxOTM1MDA5IiwgIm1lc2hJZCI6ICJNMDM1MTgzNiIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC44OTYsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDA5LCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjA5NX0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMTA5LCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMDAzfX0sICJydWxlSWQiOiAiNjk4ZjJiMTktMjdiNi00ZGFiLTkxNTAtN2Q3ZWYzYjAzYTVjIiwgImRlcml2ZWRGcm9tIjogW3sidWlkIjogMn1dfV0sICJTeW1wdG9tRGlzZWFzZUluZCI6IFt7InR5cGUiOiAiYWNpLlN5bXB0b21EaXNlYXNlSW5kIiwgInVpZCI6IDQsICJiZWdpbiI6IDAsICJlbmQiOiAxNCwgImNvdmVyZWRUZXh0IjogInBlYW51dCBhbGxlcmd5IiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDU1OTQ3MCIsICJpY2QxMENvZGUiOiAiWjkxLjAxMCxaOTEuMCIsICJtb2RhbGl0eSI6ICJwb3NpdGl2ZSIsICJzeW1wdG9tRGlzZWFzZVN1cmZhY2VGb3JtIjogInBlYW51dCBhbGxlcmd5IiwgInNub21lZENvbmNlcHRJZCI6ICI5MTkzNTAwOSIsICJjY3NDb2RlIjogIjI1MyIsICJzeW1wdG9tRGlzZWFzZU5vcm1hbGl6ZWROYW1lIjogImFsbGVyZ3kgdG8gcGVhbnV0IiwgImljZDlDb2RlIjogIjk5NS4zIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjg5NiwgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDksICJkaXNjdXNzZWRTY29yZSI6IDAuMDk1fSwgInN1c3BlY3RlZFNjb3JlIjogMC4xMDksICJzeW1wdG9tU2NvcmUiOiAwLjAwMSwgInRyYXVtYVNjb3JlIjogMC4wLCAiZmFtaWx5SGlzdG9yeVNjb3JlIjogMC4wMDN9fX1dLCAic3BlbGxDb3JyZWN0ZWRUZXh0IjogW3siY29ycmVjdGVkVGV4dCI6ICJwZWFudXQgYWxsZXJneSJ9XX0="
          }
        }
      ],
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
    }
  ],
  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
}
```

</details><br/>


The extensions of interest within the insight extension are:

extension |  purpose
--------- |-------
insight-id | identifier for the insight.
path       | HL7 FHIR Path to the part of this resource that the insight applies to. This is the location where derived codes have been added.
insight-detail | Detailed supporting evidence for the insight.


#### Insight detail
The insight detail extension provides information about why the insight got created:

Extension | Purpose
--------- | -------
reference | The resource that contained the text that was used to create the insight. For enrichment, this will always be the enriched resource, the insight is derived from the same resource that the insight pertains to.
reference-path | HL7 FHIR Path that describes the location of the text used to create the insight (within reference)
evaluated-output | base64 response from the ACD Service

