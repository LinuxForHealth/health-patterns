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
                    "text": "Heart Attack"
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

A bundle with the enriched condition is returned from the service. The additional codings have been added.

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
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                  "valueString": "code.coding"
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "nlp-insight-7f11e00daea9a6fe1fc213cbb5068144af07b4887f3ed662d73855bb-1"
                  }
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                      "valueString": "code.text"
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
              "code": "C0027051",
              "display": "heart attack",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "extension": [
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
              "code": "500448019",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "350357012",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "622062019",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37436014",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37437017",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "299703017",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "241792015",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "395860017",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "500449010",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "299700019",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "395861018",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "241791010",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37443015",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37440017",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37441018",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37438010",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "241790011",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "500450010",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "395863015",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "1784873012",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37442013",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "37439019",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "500452019",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "1784872019",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "2747117014",
              "system": "http://snomed.info/sct"
            },
            {
              "extension": [
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
              "code": "751689013",
              "system": "http://snomed.info/sct"
            }
          ],
          "text": "Heart Attack"
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
B64_REPORT_TEXT=$(echo 'Patient has pneumonia and has also been diagnosed with a heart attack. Patient started taking beta blockers.' | base64 -w 0)
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

The returned bundle has a derived condition resource (heart attack), and also a derived medication resource (for beta blockers). Each resource has an insight detail extension that provides the evidence that was used to derive these resources.

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
                    "value": "nlp-insight-a26712a9ce47d4beafd3bbecf5984811b9f564d5a51c00a0ccf638c1-1"
                  }
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
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "heart attack"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 57
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 69
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
        "code": {
          "coding": [
            {
              "code": "C0027051",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "code": "500448019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "350357012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "622062019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37436014",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37437017",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "299703017",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "241792015",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "395860017",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "500449010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "299700019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "395861018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "241791010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37443015",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37440017",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37441018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37438010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "241790011",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "500450010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "395863015",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "1784873012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37442013",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "37439019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "500452019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "1784872019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "2747117014",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "751689013",
              "system": "http://snomed.info/sct"
            }
          ],
          "text": "heart attack"
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
                    "value": "nlp-insight-b95a1666c6566106bad7a163a0fb134a95444f27b73ebf4a8db9d22e-1"
                  }
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
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "pneumonia"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 12
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 21
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
            },
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
                    "value": "nlp-insight-b95a1666c6566106bad7a163a0fb134a95444f27b73ebf4a8db9d22e-2"
                  }
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
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "pneumonia"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 12
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 21
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
        "code": {
          "coding": [
            {
              "code": "C0032285",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "code": "396219014",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "242293010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "100271014",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "350049016",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "100272019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "242308013",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "409863013",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "535895010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "535901013",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "242302014",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "100274018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "799307012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "2760037018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "621810017",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "2721096015",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "2741003011",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "666821014",
              "system": "http://snomed.info/sct"
            }
          ],
          "text": "pneumonia"
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
                    "value": "nlp-insight-daf389465bf99a5820e3bbf684469b79bf4ed126fd8de3b0a28c6d1a-1"
                  }
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
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "pneumonia"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 12
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 21
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
        "code": {
          "coding": [
            {
              "code": "C3714636",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "code": "314740018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "100273012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "590574014",
              "system": "http://snomed.info/sct"
            }
          ],
          "text": "pneumonias"
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
                    "value": "nlp-insight-475fd2cfa67e031ab422d69b2e4fbeb5f88b935e775832fdbd6ab2d0-1"
                  }
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
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "beta blockers"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 94
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 107
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
        "medicationCodeableConcept": {
          "coding": [
            {
              "code": "C0001645",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "code": "55490011",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "55491010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "3299303012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "485461013",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "714657019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "462279010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "1211746018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "55488010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "55489019",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "3299819012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "485462018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "3520627012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "3520702014",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "3520874018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "1229191018",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "1192795014",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "1198551012",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "764632010",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "2741579018",
              "system": "http://snomed.info/sct"
            }
          ],
          "text": "beta blockers"
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
