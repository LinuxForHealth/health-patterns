# Tutorial
----------------------------------------------
## QuickUMLS


### Prereqs
* You must have access to a deployed QuickUMLS service to complete this tutorial.
* You must have a container runtime installed on your machine
* This tutorial uses curl to submit REST requests to the service

### Start the nlp-insights service
Start the service in a docker container on port 5000. `<user-id>` should be the user id for your local repository.
Windows users should use ./gradlew.bat instead of ./gradlew

`./gradlew checkSource dockerStop dockerRemoveContainer dockerRun -PdockerUser=<user-id> -PdockerLocalPort=5000`

The tasks run in left to right order:

- `checkSource` performs unit tests and static source code checks on the source. It is optional when not making changes.
- `dockerStop` stops the container if it is running. This may be necessary if you want to restart the service.
- `dockerRemoveContainer` removes the container from your container registry. This may be necessary if you want to restart the service.
- `dockerRun` starts the container

The `dockerUser` property should be your docker user id.
The `dockerLocalPort` is the port the service runs on. The default is 5000, but you can change this if you have other local services already running on port 5000.

<details><summary>output</summary>

```
> Task :dockerRunStatus
Docker container 'nlp-insights' is RUNNING.

BUILD SUCCESSFUL in 1m 16s
```

</details>

The service will now be running on port 5000.

`docker container ls`

<details><summary>output</summary>

```
CONTAINER ID  IMAGE                             COMMAND               CREATED        STATUS            PORTS                   NAMES

592aeac44fca  localhost/ntl/nlp-insights:0.0.2  python3 -m flask ...  2 minutes ago  Up 2 minutes ago  0.0.0.0:5000->5000/tcp  nlp-insights
```

</details>

### Create a configuration for quickumls
The first step is to create the definition for the quickUMLS service. Replace `<service_url_here>` with your endpoint.

```
curl -w "%{http_code}\n" -o - -XPOST localhost:5000/config/definition  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
  "name": "quickconfig1",
  "nlpServiceType": "quickumls",
  "config": {
    "endpoint": "https://<service_url_here>/match"
  }
}
EOF
```

<details><summary>output</summary>

200

</details>


### Set QuickUmls as the default configuration
Now the definition of the QuickUMLS service exists, we can set it as the default service. You should  be aware that this operation
affects all users of the nlp-insights service.

```
curl -w "\n%{http_code}\n" -o - -XPOST localhost:5000/config/setDefault?name=quickconfig1
```

<details><summary>output</summary>

Default config set to: quickconfig1

200

</details>

### Enrich a Condition

In this example, the nlp-insights service is sent a bundle that contains a single condition. The condition has a code with text "Heart Attack", but no coding values. The service will add coding values to the code.

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

A bundle with the enriched condition is returned from the service. The additional codings have been added. QuickUMLS does not have logic built into it to return the best UMLS cui, but it does give us many possible matching CUIs in the response.

`cat /tmp/output | jq`

<details><summary>output</summary>

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
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDQyODk1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0Il0sIGZhbHNlXSwgWyJDMjkyNjA2MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMCwgMjEsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlhZ25vc3RpY1Byb2NlZHVyZSJdLCBmYWxzZV0sIFsiQzAwMjcwNTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMCwgMjEsICJteW9jYXJkaWFsIGluZmFyY3Rpb25zIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAiZWNnIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0Il0sIGZhbHNlXSwgWyJDMDQ4OTU3NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiBhZ2UiLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzNjQwOTExIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiAobWkpIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgInBhc3QgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDQyODk1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uLCAobWkpIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDE1NTYyNiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgImFjdXRlIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM1NDE5NTAiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMCwgMjEsICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMCwgMjEsICJteW9jYXJkaWFsIGluZmFyY3Rpb24gYWN1dGUiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODI5OTEwIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAiaGFkIGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMwNzQ2NzI3IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMCwgMjEsICJzZXB0YWwgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkZpbmRpbmciXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAiaGVhbGVkIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAzNDAzMjQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMCwgMjEsICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgInR5cGUgNSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU2IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAidHlwZSAzIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMCwgMjEsICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDAsIDIxLCAidHlwZSAxIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMjgyNTE1OSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgImRhdGUgb2YgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkNsaW5pY2FsQXR0cmlidXRlIl0sIGZhbHNlXSwgWyJDMzg0NTUwMiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgInR5cGUgNGMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgInR5cGUgNGIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAwLCAyMSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXV1d"
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
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "display": "myocardial infarctions",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C0155668",
              "display": "old myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "display": "myocardial infarction (mi)",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C0155668",
              "display": "past myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "display": "myocardial infarction, (mi)",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C0155626",
              "display": "acute myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C0155626",
              "display": "myocardial infarction acute",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C0746727",
              "display": "septal myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C0155668",
              "display": "healed myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C0340324",
              "display": "silent myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C3898652",
              "display": "type 5 myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C3898656",
              "display": "type 3 myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C3845502",
              "display": "myocardial infarction, stroke",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C3898653",
              "display": "type 4c myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C3898654",
              "display": "type 4b myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                      "valueIdentifier": {
                        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
              "code": "C3898655",
              "display": "type 4a myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
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

### Derive New Resources
Some resources such as DiagnosticReports or DocumentReferences contain clinical notes or other unstructured text. When the nlp-insights service receives one of these resources, it can generate new FHIR resources for detected conditions and medication statements.

Text data in a diagnostic report must be base64 encoded.

```
B64_REPORT_TEXT=$(echo 'The patient had a myocardial infarction in 2015 and was prescribed Losartan.' | base64 -w 0)
```

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
        }
    ]
}
EOF

```

<details><summary>output</summary>

200

</details>

The returned bundle has a derived condition resource (myocardial infarction), and also a derived medication resource (for Losartan). Each resource has an insight detail extension that provides the evidence that was used to derive these resources. Similar to the prior example, QuickUMLS cannot determine which UMLS concept is best for "myocardial infarction", and several conditions might be created from the same span.

`cat /tmp/output | jq`

<details><summary>output</summary>

```json
{
  "entry": [
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "b57c2ab27236e620010a0e10aeadd5f69cdfbee474218c073cf07068"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        },
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        },
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        },
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "b57c2ab27236e620010a0e10aeadd5f69cdfbee474218c073cf07068"
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
        "code": {
          "coding": [
            {
              "code": "C0027051",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "7081224c189e0d348097adc50e565167de9d79dd2198a8562f73b062"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        },
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        },
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "7081224c189e0d348097adc50e565167de9d79dd2198a8562f73b062"
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
        "code": {
          "coding": [
            {
              "code": "C0155668",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "old myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "0014c8052f6845a78e2fb3d981ac2f2a258e8e0668af69da59056644"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        },
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "0014c8052f6845a78e2fb3d981ac2f2a258e8e0668af69da59056644"
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
        "code": {
          "coding": [
            {
              "code": "C0155626",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "acute myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "bae8f284741e0e1c221f0bca249450796bfb14a367705ffcbec77c9a"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "bae8f284741e0e1c221f0bca249450796bfb14a367705ffcbec77c9a"
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
        "code": {
          "coding": [
            {
              "code": "C0746727",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "septal myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "b8dccbab48faa5f61a0076a9102f796065814b1e168d201ea3b86241"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "b8dccbab48faa5f61a0076a9102f796065814b1e168d201ea3b86241"
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
        "code": {
          "coding": [
            {
              "code": "C0340324",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "silent myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "86667a460b83c06714c3cfc57b5667866f9b077692daab3f6f2fe066"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "86667a460b83c06714c3cfc57b5667866f9b077692daab3f6f2fe066"
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
        "code": {
          "coding": [
            {
              "code": "C3898652",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "type 5 myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "d294965c231a2ce7c556534e987647cf37578c8e423f816da82c5222"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "d294965c231a2ce7c556534e987647cf37578c8e423f816da82c5222"
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
        "code": {
          "coding": [
            {
              "code": "C3898656",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "type 3 myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "23310008f9fa1c0dae0944f881475ef313fc74ef91f5a9219430353f"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "23310008f9fa1c0dae0944f881475ef313fc74ef91f5a9219430353f"
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
        "code": {
          "coding": [
            {
              "code": "C3845502",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "myocardial infarction, stroke"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "f58554c55c0ee29d59c96b8eed29cb2cb25a9a131016ab25f227de4b"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "f58554c55c0ee29d59c96b8eed29cb2cb25a9a131016ab25f227de4b"
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
        "code": {
          "coding": [
            {
              "code": "C3898653",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "type 4c myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "9e6b703d06420ea4a62a4406db3407710030865b7fc359d47096c2b4"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "9e6b703d06420ea4a62a4406db3407710030865b7fc359d47096c2b4"
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
        "code": {
          "coding": [
            {
              "code": "C3898654",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "type 4b myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "Condition"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "725f519bafcaf571973e53e86d018e7a5e8d05040b6465538c90dd7e"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "Condition"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "myocardial infarction"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 18
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 39
                            }
                          ],
                          "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                        }
                      ],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "725f519bafcaf571973e53e86d018e7a5e8d05040b6465538c90dd7e"
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
        "code": {
          "coding": [
            {
              "code": "C3898655",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "type 4a myocardial infarction"
        },
        "resourceType": "Condition"
      }
    },
    {
      "request": {
        "method": "POST",
        "url": "MedicationStatement"
      },
      "resource": {
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "4201c672ebe453a613f82077770d976468dc1fb4c929008812e49166"
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "MedicationStatement"
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                      "valueReference": {
                        "reference": "DiagnosticReport/abcefg-1234567890"
                      }
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W1tbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzA0Mjg5NTMiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMyOTI2MDYzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM4MTA4MTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpYWdub3N0aWNQcm9jZWR1cmUiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbnMiLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwMTU1NjY4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuTGFib3JhdG9yeU9yVGVzdFJlc3VsdCJdLCBmYWxzZV0sIFsiQzA0ODk1NzciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSIsIFsidW1scy5DbGluaWNhbEF0dHJpYnV0ZSJdLCBmYWxzZV0sIFsiQzM2NDA5MTEiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDAyNzA1MSIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2NjgiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMwNDI4OTUzIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgImVjZzogbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkxhYm9yYXRvcnlPclRlc3RSZXN1bHQiXSwgZmFsc2VdLCBbIkMwMDI3MDUxIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzU0MTk1MCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzAxNTU2MjYiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzgyOTkxMCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV0sIFsiQzA3NDY3MjciLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzIzNDgzNjIiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5GaW5kaW5nIl0sIGZhbHNlXSwgWyJDMDE1NTY2OCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDM0MDMyNCIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJzaWxlbnQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NiIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1NyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMzODk4NjU4IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRmluZGluZyJdLCBmYWxzZV0sIFsiQzI4MjUxNTkiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuQ2xpbmljYWxBdHRyaWJ1dGUiXSwgZmFsc2VdLCBbIkMzODQ1NTAyIiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgc3Ryb2tlIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMzg5ODY1MyIsICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAxOCwgMzksICJ0eXBlIDRjIG15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIFsidW1scy5EaXNlYXNlT3JTeW5kcm9tZSJdLCBmYWxzZV0sIFsiQzM4OTg2NTQiLCAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgMTgsIDM5LCAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24iLCBbInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiXSwgZmFsc2VdLCBbIkMzODk4NjU1IiwgIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsIDE4LCAzOSwgInR5cGUgNGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgWyJ1bWxzLkRpc2Vhc2VPclN5bmRyb21lIl0sIGZhbHNlXSwgWyJDMDI3ODMyOSIsICJwcmVzY3JpYmVkIiwgNTYsIDY2LCAicHJlc2NyaWJlZCIsIFsidW1scy5IZWFsdGhDYXJlQWN0aXZpdHkiXSwgZmFsc2VdLCBbIkMwMTI2MTc0IiwgIkxvc2FydGFuIiwgNjcsIDc1LCAibG9zYXJ0YW4iLCBbInVtbHMuT3JnYW5pY0NoZW1pY2FsIiwgInVtbHMuUGhhcm1hY29sb2dpY1N1YnN0YW5jZSJdLCBmYWxzZV0sIFsiQzE1NTA2NTUiLCAicGF0aWVudCIsIDQsIDExLCAicGF0aWVudCIsIFsidW1scy5Cb2R5U3Vic3RhbmNlIl0sIGZhbHNlXSwgWyJDMTU3ODQ4NSIsICJwYXRpZW50IiwgNCwgMTEsICJwYXRpZW50IiwgWyJ1bWxzLkludGVsbGVjdHVhbFByb2R1Y3QiXSwgZmFsc2VdLCBbIkMxNTc4NDg2IiwgInBhdGllbnQiLCA0LCAxMSwgInBhdGllbnQiLCBbInVtbHMuSW50ZWxsZWN0dWFsUHJvZHVjdCJdLCBmYWxzZV1dXQ=="
                      }
                    },
                    {
                      "extension": [],
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                    }
                  ],
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
                }
              ],
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
            }
          ]
        },
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                  "value": "4201c672ebe453a613f82077770d976468dc1fb4c929008812e49166"
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
        "medicationCodeableConcept": {
          "coding": [
            {
              "code": "C0126174",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            }
          ],
          "text": "losartan"
        },
        "status": "unknown",
        "resourceType": "MedicationStatement"
      }
    }
  ],
  "type": "transaction",
  "resourceType": "Bundle"
}

```
