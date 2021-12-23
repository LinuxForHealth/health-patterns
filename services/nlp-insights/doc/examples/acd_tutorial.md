# Tutorial
----------------------------------------------
## ACD
The IBM Watson Annotator for Clinical Data (ACD) service is a medical domain NLP service featuring a variety of annotators. More information is available [here](https://www.ibm.com/cloud/watson-annotator-for-clinical-data).

The nlp-insights service has been designed to use ACD for concept detection and extraction to derive and enrich FHIR resources.

### Prereqs
* You must have access to an ACD service to complete this tutorial. You can view plans (including a free trial plan) [here](https://cloud.ibm.com/catalog/services/annotator-for-clinical-data).
* You must have a container runtime installed on your machine
* You must have a python 3.9 and pip distribution
* This tutorial uses curl to submit REST requests to the service

### Start the nlp-insights service
Start the service in a docker container on port 5000. `<user-id>` should be the user id for your local repository.
Windows users should use ./gradlew.bat instead of ./gradlew

`./gradlew checkSource dockerStop dockerRemoveContainer dockerRun -PdockerUser=<user-id> -PdockerLocalPort=5000`

The tasks run in left to right order:

- `checkSource` performs unit tests and static source code checks on the source. It is optional when not making changes.
- `dockerStop` stops the container if it is running. This is necessary if the service is already started.
- `dockerRemoveContainer` removes the container from your container registry. This is necessary if container has been previously registered.
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

### Create a configuration for ACD
The first step is to create the definition for the ACD service. Replace `<your_api_key_here>` with the key for your instance. You can find the api key by opening your service from the IBM Cloud resource list and navigating to "service credentials". The nlp-insights service only needs "reader" authority.

Check that the endpoint is correct for your service.

The nlp-insights service is designed for the out of the box wh_acd.ibm_clinical_insights_v1.0_standard_flow. Customized flows may require modification of the source code in order to fully leverage the customizations.

```
curl -w "%{http_code}\n" -o - -XPOST localhost:5000/config/definition  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
  "name": "acdconfig1",
  "nlpServiceType": "acd",
  "config": {
    "apikey": <your-api-key-here>,
    "endpoint": "https://us-east.wh-acd.cloud.ibm.com/wh-acd/api",
    "flow": "wh_acd.ibm_clinical_insights_v1.0_standard_flow"
  }
}
EOF
```

<details><summary>output</summary>

200

</details>


### Set ACD as the default configuration
Now the definition of the ACD service exists, we can set it as the default service. You should  be aware that this operation affects all users of the nlp-insights service.

```
curl -w "\n%{http_code}\n" -o - -XPOST localhost:5000/config/setDefault?name=acdconfig1
```

<details><summary>output</summary>

Default config set to: acdconfig1

200

</details>

### Enrich a Condition

In this example, the nlp-insights service is sent a bundle that contains a single condition. The condition has a code with text "myocardial infarction", but no coding values. The service will add coding values to the code.

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

A bundle with the enriched condition is returned from the service. ACD has knowledge of a wide variety of code systems. As a result SNOMED, ICD-9 and ICD-10 codes are returned in addition to the UMLS concept id.

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

### Enrich an allergy intolerance
In this example, a bundle with two allergy intolerance resources is sent to the nlp insights server. The first has a code with text "peanut", and the second resource has a code with text "amoxicillin".

Both resources contain only text and do not contain any codes for the allergy. The nlp-insights service will enrich the resources with UMLS, snomed, icd-9 and icd-10 codes.

```
curl  -w "\n%{http_code}\n" -s -o /tmp/output -XPOST localhost:5000/discoverInsights  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
{
    "resourceType": "Bundle",
    "id": "abc",
    "type": "transaction",
    "entry": [
        {
            "resource": {
                "id": "wxyz-123",
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
                "id": "qrstuv-123",
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

A bundle containing the enriched allergy intolerance resources is returned. Each resource now contains additional derived code values.

`cat /tmp/output | jq`

<details><summary>output</summary>

```
{
  "entry": [
    {
      "request": {
        "method": "PUT",
        "url": "AllergyIntolerance/wxyz-123"
      },
      "resource": {
        "id": "wxyz-123",
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                    "value": "afb140bbd89d857d4da07c2b0a8ebdda96d7462a1afdf39d37604f24"
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
                        "reference": "AllergyIntolerance/wxyz-123"
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
                        "value": "afb140bbd89d857d4da07c2b0a8ebdda96d7462a1afdf39d37604f24"
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
                        "value": "afb140bbd89d857d4da07c2b0a8ebdda96d7462a1afdf39d37604f24"
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
                        "value": "afb140bbd89d857d4da07c2b0a8ebdda96d7462a1afdf39d37604f24"
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
                        "value": "afb140bbd89d857d4da07c2b0a8ebdda96d7462a1afdf39d37604f24"
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
                        "value": "afb140bbd89d857d4da07c2b0a8ebdda96d7462a1afdf39d37604f24"
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
        "url": "AllergyIntolerance/qrstuv-123"
      },
      "resource": {
        "id": "qrstuv-123",
        "meta": {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                  "valueIdentifier": {
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
                    "value": "d8fdcd1d0735807892562c20de5c81db5550d6509452269e0cf4cb9c"
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
                        "reference": "AllergyIntolerance/qrstuv-123"
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
                        "value": "d8fdcd1d0735807892562c20de5c81db5550d6509452269e0cf4cb9c"
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
                        "value": "d8fdcd1d0735807892562c20de5c81db5550d6509452269e0cf4cb9c"
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
                        "value": "d8fdcd1d0735807892562c20de5c81db5550d6509452269e0cf4cb9c"
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
                        "value": "d8fdcd1d0735807892562c20de5c81db5550d6509452269e0cf4cb9c"
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
                        "value": "d8fdcd1d0735807892562c20de5c81db5550d6509452269e0cf4cb9c"
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

The returned bundle has a derived condition resource (myocardial infarction), and also a derived medication resource (for Losartan). Each resource has an insight detail extension that provides the evidence that was used to derive these resources. The Condition resource includes SNOMED, icd-9 and icd-10 codes. The medication statement resource includes an rxnorm code.

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
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
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
                        "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAicHJlZmVycmVkTmFtZSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn1dLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gQXR0cmlidXRlcyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiY29uY2VwdCI6IHsidWlkIjogOH0sICJuYW1lIjogIkRpYWdub3NpcyIsICJpY2Q5Q29kZSI6ICI0MTAuOTAiLCAiaWNkMTBDb2RlIjogIkkyMS45IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC45OTQsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDAzLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAwNH0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMDIxLCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMH19LCAiY2NzQ29kZSI6ICIxMDAiLCAiaGNjQ29kZSI6ICI4NiIsICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7ImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibG9zYXJ0YW4ifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA3fSwgIm5hbWUiOiAiUHJlc2NyaWJlZE1lZGljYXRpb24iLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgInN0YXJ0ZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiYWR2ZXJzZUV2ZW50IjogeyJzY29yZSI6IDAuMCwgImFsbGVyZ3lTY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19fV0sICJjb25jZXB0cyI6IFt7InR5cGUiOiAidW1scy5GaW5kaW5nIiwgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzQ1NTI5NTkiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24sIENUQ0FFIiwgInNlbWFudGljVHlwZSI6ICJmbmRnIiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzE0MzY5MSIsICJ2b2NhYnMiOiAiTVRILE5DSV9DVENBRV81LE5DSSJ9LCB7InR5cGUiOiAidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0IiwgInVpZCI6IDQsICJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwNDI4OTUzIiwgInByZWZlcnJlZE5hbWUiOiAiRWxlY3Ryb2NhcmRpb2dyYW06IG15b2NhcmRpYWwgaW5mYXJjdGlvbiAoZmluZGluZykiLCAic2VtYW50aWNUeXBlIjogImxidHIiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJJTlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjQsSTIxLjI5LEkyMS4wOSxJMjEuMTksUjk0LjMxLEkyNS4yLEkyMS45IiwgIm5jaUNvZGUiOiAiQzEwMTU4OSIsICJzbm9tZWRDb25jZXB0SWQiOiAiMTY0ODY1MDA1IiwgInZvY2FicyI6ICJDSFYsTVRILE5DSV9DRElTQyxOQ0ksU05PTUVEQ1RfVVMifSwgeyJ0eXBlIjogInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiLCAidWlkIjogMywgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzAwMjcwNTEiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24iLCAic2VtYW50aWNUeXBlIjogImRzeW4iLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAiaWNkMTBDb2RlIjogIkkyMS45IiwgIm5jaUNvZGUiOiAiQzI3OTk2IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJtZXNoSWQiOiAiTTAwMTQzNDAiLCAibG9pbmNJZCI6ICJNVEhVMDM1NTUxLExBMTQyNzQtNyxMUDk4ODg0LTcsTEExNjI4Ni05IiwgInZvY2FicyI6ICJOQ0lfTklDSEQsTVRILExOQyxDU1AsTVNILENTVCxIUE8sT01JTSxOQ0lfQ1RDQUUsQ09TVEFSLEFJUixDSFYsTkNJX0ZEQSxNRURMSU5FUExVUyxOQ0ksTENIX05XLEFPRCxTTk9NRURDVF9VUyxEWFAiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInRlbXBvcmFsIjogW3siYmVnaW4iOiA0MywgImVuZCI6IDQ3LCAiY292ZXJlZFRleHQiOiAiMjAxNSIsICJ0ZW1wb3JhbFR5cGUiOiB7ImRhdGVTY29yZSI6IDEuMCwgInJlbGF0aXZlU2NvcmUiOiAwLjB9LCAicmVsYXRpb25UeXBlcyI6IHsib3ZlcmxhcHNTY29yZSI6IDAuOTk4LCAiZHVyYXRpb25TY29yZSI6IDAuMH19XX0sIHsidHlwZSI6ICJ1bWxzLkhlYWx0aENhcmVBY3Rpdml0eSIsICJiZWdpbiI6IDU2LCAiZW5kIjogNjYsICJjb3ZlcmVkVGV4dCI6ICJwcmVzY3JpYmVkIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDI3ODMyOSIsICJwcmVmZXJyZWROYW1lIjogIlByZXNjcmliZWQiLCAic2VtYW50aWNUeXBlIjogImhsY2EiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAidm9jYWJzIjogIk1USCxDSFYsTENIIn0sIHsidHlwZSI6ICJ1bWxzLk9yZ2FuaWNDaGVtaWNhbCIsICJ1aWQiOiA1LCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic2VtYW50aWNUeXBlIjogIm9yY2giLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInZvY2FicyI6ICJNVEgsTE5DLENTUCxNU0gsTVRIU1BMLFJYTk9STSxOQ0lfTkNJLUdMT1NTLENIVixBVEMsTkNJX0NUUlAsTkNJX0ZEQSxOQ0ksQU9ELFNOT01FRENUX1VTLERSVUdCQU5LLFZBTkRGIn0sIHsidHlwZSI6ICJ1bWxzLlBoYXJtYWNvbG9naWNTdWJzdGFuY2UiLCAidWlkIjogMiwgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJwcmVmZXJyZWROYW1lIjogImxvc2FydGFuIiwgInNlbWFudGljVHlwZSI6ICJwaHN1IiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzY2ODY5IiwgInNub21lZENvbmNlcHRJZCI6ICI5NjMwOTAwMCwzNzM1NjcwMDIiLCAibWVzaElkIjogIk0wMDI5NDAwIiwgInJ4Tm9ybUlkIjogIjUyMTc1IiwgImxvaW5jSWQiOiAiTFAxNzE2MTktMiIsICJ2b2NhYnMiOiAiTVRILExOQyxDU1AsTVNILE1USFNQTCxSWE5PUk0sTkNJX05DSS1HTE9TUyxDSFYsQVRDLE5DSV9DVFJQLE5DSV9GREEsTkNJLEFPRCxTTk9NRURDVF9VUyxEUlVHQkFOSyxWQU5ERiIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJtZWRpY2F0aW9uIjogeyJ1c2FnZSI6IHsidGFrZW5TY29yZSI6IDEuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMCwgImxhYk1lYXN1cmVtZW50U2NvcmUiOiAwLjB9LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJkb3NlQ2hhbmdlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJhZHZlcnNlRXZlbnQiOiB7InNjb3JlIjogMC4wLCAiYWxsZXJneVNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0b3BwZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19fX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJwcmVmZXJyZWROYW1lIjogIk15b2NhcmRpYWwgSW5mYXJjdGlvbiIsICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBEZXJpdmVkIENvbmNlcHRzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibmNpQ29kZSI6ICJDMjc5OTYiLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgIm1lc2hJZCI6ICJNMDAxNDM0MCIsICJsb2luY0lkIjogIk1USFUwMzU1NTEsTEExNDI3NC03LExQOTg4ODQtNyxMQTE2Mjg2LTkiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInJ1bGVJZCI6ICI2OThmMmIxOS0yN2I2LTRkYWItOTE1MC03ZDdlZjNiMDNhNWMiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAzfV0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDQyODk1MyIsICJwcmVmZXJyZWROYW1lIjogIkVsZWN0cm9jYXJkaW9ncmFtOiBteW9jYXJkaWFsIGluZmFyY3Rpb24gKGZpbmRpbmcpIiwgInNvdXJjZSI6ICJDbGluaWNhbCBJbnNpZ2h0cyAtIERlcml2ZWQgQ29uY2VwdHMiLCAic291cmNlVmVyc2lvbiI6ICJ2MS4wIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiSU5WQUxJRCJ9LCAicnVsZUlkIjogImMxZThkN2Q0LTdkMzYtNDIzYi1iMzlkLTRlYmI1ZWI2NWIwYyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDR9XX0sIHsidHlwZSI6ICJJQ01lZGljYXRpb24iLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgImluc2lnaHRNb2RlbERhdGEiOiB7Im1lZGljYXRpb24iOiB7InVzYWdlIjogeyJ0YWtlblNjb3JlIjogMS4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wLCAibGFiTWVhc3VyZW1lbnRTY29yZSI6IDAuMH0sICJzdGFydGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgImRvc2VDaGFuZ2VkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RvcHBlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX19fSwgInJ1bGVJZCI6ICI3ODYxYzAyNC1hZDFjLTQ3ZTYtYjQwZS1jOTBjYjdiMTllMjYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInJ1bGVJZCI6ICJkMDA0ZGY2Mi1hNjVkLTQxMzYtYWEzMi0xNjFhNDNlYjk1MDYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAicnVsZUlkIjogIjM0M2U2MTU4LTJjMzAtNDcyNi1iZTcxLTMzYTU3MGIyODcwMyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDV9XX1dLCAiTWVkaWNhdGlvbkluZCI6IFt7InR5cGUiOiAiYWNpLk1lZGljYXRpb25JbmQiLCAidWlkIjogNywgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnIjogW3siY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAiY3VpIjogIkMwMTI2MTc0IiwgImNvbXBsZXgiOiAiZmFsc2UiLCAiZW5kIjogNzUsICJ0eXBlIjogImFjaS5JbmRfRHJ1ZyIsICJuYW1lMSI6IFt7InJ4Tm9ybUlEIjogIjUyMTc1IiwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnU3VyZmFjZUZvcm0iOiAiTG9zYXJ0YW4iLCAiZHJ1Z05vcm1hbGl6ZWROYW1lIjogImxvc2FydGFuIiwgImVuZCI6IDc1LCAidHlwZSI6ICJhY2kuRHJ1Z05hbWUiLCAiYmVnaW4iOiA2N31dLCAiYmVnaW4iOiA2N31dLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgInN0YXJ0ZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiYWR2ZXJzZUV2ZW50IjogeyJzY29yZSI6IDAuMCwgImFsbGVyZ3lTY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19LCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCIsICJjb21tZW50IjogIm1hcmtlZCBWQUxJRCBieSBjbGluaWNhbCBpbnNpZ2h0IG1vZGVscy4ifX1dLCAiU3ltcHRvbURpc2Vhc2VJbmQiOiBbeyJ0eXBlIjogImFjaS5TeW1wdG9tRGlzZWFzZUluZCIsICJ1aWQiOiA4LCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibW9kYWxpdHkiOiAicG9zaXRpdmUiLCAic3ltcHRvbURpc2Vhc2VTdXJmYWNlRm9ybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgImNjc0NvZGUiOiAiMTAwIiwgInN5bXB0b21EaXNlYXNlTm9ybWFsaXplZE5hbWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgImljZDlDb2RlIjogIjQxMC45MCIsICJoY2NDb2RlIjogIjg2IiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjk5NCwgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDMsICJkaXNjdXNzZWRTY29yZSI6IDAuMDA0fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wMjEsICJzeW1wdG9tU2NvcmUiOiAwLjAwMSwgInRyYXVtYVNjb3JlIjogMC4wLCAiZmFtaWx5SGlzdG9yeVNjb3JlIjogMC4wfX0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19XSwgInNwZWxsQ29ycmVjdGVkVGV4dCI6IFt7ImNvcnJlY3RlZFRleHQiOiAiVGhlIHBhdGllbnQgaGFkIGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIGluIDIwMTUgYW5kIHdhcyBwcmVzY3JpYmVkIExvc2FydGFuLlxuIn1dLCAidGVtcG9yYWxTcGFucyI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfX1dfQ=="
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
                            },
                            {
                              "extension": [
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/method",
                                  "valueCodeableConcept": {
                                    "coding": [
                                      {
                                        "code": "Diagnosis_Explicit_Score",
                                        "system": "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method"
                                      }
                                    ]
                                  }
                                },
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
                                  "valueDecimal": 0.994
                                },
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
                                  "valueString": "Explicit Score"
                                }
                              ],
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
                            },
                            {
                              "extension": [
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/method",
                                  "valueCodeableConcept": {
                                    "coding": [
                                      {
                                        "code": "Diagnosis_Patient_Reported_Score",
                                        "system": "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method"
                                      }
                                    ]
                                  }
                                },
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
                                  "valueDecimal": 0.003
                                },
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
                                  "valueString": "Patient Reported Score"
                                }
                              ],
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
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
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
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
              "display": "myocardial infarction",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "code": "22298006",
              "system": "http://snomed.info/sct"
            },
            {
              "code": "410.90",
              "system": "http://hl7.org/fhir/sid/icd-9-cm"
            },
            {
              "code": "I21.9",
              "system": "http://hl7.org/fhir/sid/icd-10-cm"
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
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
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
                        "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAicHJlZmVycmVkTmFtZSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn1dLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gQXR0cmlidXRlcyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiY29uY2VwdCI6IHsidWlkIjogOH0sICJuYW1lIjogIkRpYWdub3NpcyIsICJpY2Q5Q29kZSI6ICI0MTAuOTAiLCAiaWNkMTBDb2RlIjogIkkyMS45IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC45OTQsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDAzLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAwNH0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMDIxLCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMH19LCAiY2NzQ29kZSI6ICIxMDAiLCAiaGNjQ29kZSI6ICI4NiIsICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7ImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibG9zYXJ0YW4ifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA3fSwgIm5hbWUiOiAiUHJlc2NyaWJlZE1lZGljYXRpb24iLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgInN0YXJ0ZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiYWR2ZXJzZUV2ZW50IjogeyJzY29yZSI6IDAuMCwgImFsbGVyZ3lTY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19fV0sICJjb25jZXB0cyI6IFt7InR5cGUiOiAidW1scy5GaW5kaW5nIiwgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzQ1NTI5NTkiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24sIENUQ0FFIiwgInNlbWFudGljVHlwZSI6ICJmbmRnIiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzE0MzY5MSIsICJ2b2NhYnMiOiAiTVRILE5DSV9DVENBRV81LE5DSSJ9LCB7InR5cGUiOiAidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0IiwgInVpZCI6IDQsICJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwNDI4OTUzIiwgInByZWZlcnJlZE5hbWUiOiAiRWxlY3Ryb2NhcmRpb2dyYW06IG15b2NhcmRpYWwgaW5mYXJjdGlvbiAoZmluZGluZykiLCAic2VtYW50aWNUeXBlIjogImxidHIiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJJTlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjQsSTIxLjI5LEkyMS4wOSxJMjEuMTksUjk0LjMxLEkyNS4yLEkyMS45IiwgIm5jaUNvZGUiOiAiQzEwMTU4OSIsICJzbm9tZWRDb25jZXB0SWQiOiAiMTY0ODY1MDA1IiwgInZvY2FicyI6ICJDSFYsTVRILE5DSV9DRElTQyxOQ0ksU05PTUVEQ1RfVVMifSwgeyJ0eXBlIjogInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiLCAidWlkIjogMywgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzAwMjcwNTEiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24iLCAic2VtYW50aWNUeXBlIjogImRzeW4iLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAiaWNkMTBDb2RlIjogIkkyMS45IiwgIm5jaUNvZGUiOiAiQzI3OTk2IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJtZXNoSWQiOiAiTTAwMTQzNDAiLCAibG9pbmNJZCI6ICJNVEhVMDM1NTUxLExBMTQyNzQtNyxMUDk4ODg0LTcsTEExNjI4Ni05IiwgInZvY2FicyI6ICJOQ0lfTklDSEQsTVRILExOQyxDU1AsTVNILENTVCxIUE8sT01JTSxOQ0lfQ1RDQUUsQ09TVEFSLEFJUixDSFYsTkNJX0ZEQSxNRURMSU5FUExVUyxOQ0ksTENIX05XLEFPRCxTTk9NRURDVF9VUyxEWFAiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInRlbXBvcmFsIjogW3siYmVnaW4iOiA0MywgImVuZCI6IDQ3LCAiY292ZXJlZFRleHQiOiAiMjAxNSIsICJ0ZW1wb3JhbFR5cGUiOiB7ImRhdGVTY29yZSI6IDEuMCwgInJlbGF0aXZlU2NvcmUiOiAwLjB9LCAicmVsYXRpb25UeXBlcyI6IHsib3ZlcmxhcHNTY29yZSI6IDAuOTk4LCAiZHVyYXRpb25TY29yZSI6IDAuMH19XX0sIHsidHlwZSI6ICJ1bWxzLkhlYWx0aENhcmVBY3Rpdml0eSIsICJiZWdpbiI6IDU2LCAiZW5kIjogNjYsICJjb3ZlcmVkVGV4dCI6ICJwcmVzY3JpYmVkIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDI3ODMyOSIsICJwcmVmZXJyZWROYW1lIjogIlByZXNjcmliZWQiLCAic2VtYW50aWNUeXBlIjogImhsY2EiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAidm9jYWJzIjogIk1USCxDSFYsTENIIn0sIHsidHlwZSI6ICJ1bWxzLk9yZ2FuaWNDaGVtaWNhbCIsICJ1aWQiOiA1LCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic2VtYW50aWNUeXBlIjogIm9yY2giLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInZvY2FicyI6ICJNVEgsTE5DLENTUCxNU0gsTVRIU1BMLFJYTk9STSxOQ0lfTkNJLUdMT1NTLENIVixBVEMsTkNJX0NUUlAsTkNJX0ZEQSxOQ0ksQU9ELFNOT01FRENUX1VTLERSVUdCQU5LLFZBTkRGIn0sIHsidHlwZSI6ICJ1bWxzLlBoYXJtYWNvbG9naWNTdWJzdGFuY2UiLCAidWlkIjogMiwgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJwcmVmZXJyZWROYW1lIjogImxvc2FydGFuIiwgInNlbWFudGljVHlwZSI6ICJwaHN1IiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzY2ODY5IiwgInNub21lZENvbmNlcHRJZCI6ICI5NjMwOTAwMCwzNzM1NjcwMDIiLCAibWVzaElkIjogIk0wMDI5NDAwIiwgInJ4Tm9ybUlkIjogIjUyMTc1IiwgImxvaW5jSWQiOiAiTFAxNzE2MTktMiIsICJ2b2NhYnMiOiAiTVRILExOQyxDU1AsTVNILE1USFNQTCxSWE5PUk0sTkNJX05DSS1HTE9TUyxDSFYsQVRDLE5DSV9DVFJQLE5DSV9GREEsTkNJLEFPRCxTTk9NRURDVF9VUyxEUlVHQkFOSyxWQU5ERiIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJtZWRpY2F0aW9uIjogeyJ1c2FnZSI6IHsidGFrZW5TY29yZSI6IDEuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMCwgImxhYk1lYXN1cmVtZW50U2NvcmUiOiAwLjB9LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJkb3NlQ2hhbmdlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJhZHZlcnNlRXZlbnQiOiB7InNjb3JlIjogMC4wLCAiYWxsZXJneVNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0b3BwZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19fX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJwcmVmZXJyZWROYW1lIjogIk15b2NhcmRpYWwgSW5mYXJjdGlvbiIsICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBEZXJpdmVkIENvbmNlcHRzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibmNpQ29kZSI6ICJDMjc5OTYiLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgIm1lc2hJZCI6ICJNMDAxNDM0MCIsICJsb2luY0lkIjogIk1USFUwMzU1NTEsTEExNDI3NC03LExQOTg4ODQtNyxMQTE2Mjg2LTkiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInJ1bGVJZCI6ICI2OThmMmIxOS0yN2I2LTRkYWItOTE1MC03ZDdlZjNiMDNhNWMiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAzfV0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDQyODk1MyIsICJwcmVmZXJyZWROYW1lIjogIkVsZWN0cm9jYXJkaW9ncmFtOiBteW9jYXJkaWFsIGluZmFyY3Rpb24gKGZpbmRpbmcpIiwgInNvdXJjZSI6ICJDbGluaWNhbCBJbnNpZ2h0cyAtIERlcml2ZWQgQ29uY2VwdHMiLCAic291cmNlVmVyc2lvbiI6ICJ2MS4wIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiSU5WQUxJRCJ9LCAicnVsZUlkIjogImMxZThkN2Q0LTdkMzYtNDIzYi1iMzlkLTRlYmI1ZWI2NWIwYyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDR9XX0sIHsidHlwZSI6ICJJQ01lZGljYXRpb24iLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgImluc2lnaHRNb2RlbERhdGEiOiB7Im1lZGljYXRpb24iOiB7InVzYWdlIjogeyJ0YWtlblNjb3JlIjogMS4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wLCAibGFiTWVhc3VyZW1lbnRTY29yZSI6IDAuMH0sICJzdGFydGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgImRvc2VDaGFuZ2VkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RvcHBlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX19fSwgInJ1bGVJZCI6ICI3ODYxYzAyNC1hZDFjLTQ3ZTYtYjQwZS1jOTBjYjdiMTllMjYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInJ1bGVJZCI6ICJkMDA0ZGY2Mi1hNjVkLTQxMzYtYWEzMi0xNjFhNDNlYjk1MDYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAicnVsZUlkIjogIjM0M2U2MTU4LTJjMzAtNDcyNi1iZTcxLTMzYTU3MGIyODcwMyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDV9XX1dLCAiTWVkaWNhdGlvbkluZCI6IFt7InR5cGUiOiAiYWNpLk1lZGljYXRpb25JbmQiLCAidWlkIjogNywgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnIjogW3siY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAiY3VpIjogIkMwMTI2MTc0IiwgImNvbXBsZXgiOiAiZmFsc2UiLCAiZW5kIjogNzUsICJ0eXBlIjogImFjaS5JbmRfRHJ1ZyIsICJuYW1lMSI6IFt7InJ4Tm9ybUlEIjogIjUyMTc1IiwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnU3VyZmFjZUZvcm0iOiAiTG9zYXJ0YW4iLCAiZHJ1Z05vcm1hbGl6ZWROYW1lIjogImxvc2FydGFuIiwgImVuZCI6IDc1LCAidHlwZSI6ICJhY2kuRHJ1Z05hbWUiLCAiYmVnaW4iOiA2N31dLCAiYmVnaW4iOiA2N31dLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgInN0YXJ0ZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiYWR2ZXJzZUV2ZW50IjogeyJzY29yZSI6IDAuMCwgImFsbGVyZ3lTY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19LCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCIsICJjb21tZW50IjogIm1hcmtlZCBWQUxJRCBieSBjbGluaWNhbCBpbnNpZ2h0IG1vZGVscy4ifX1dLCAiU3ltcHRvbURpc2Vhc2VJbmQiOiBbeyJ0eXBlIjogImFjaS5TeW1wdG9tRGlzZWFzZUluZCIsICJ1aWQiOiA4LCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibW9kYWxpdHkiOiAicG9zaXRpdmUiLCAic3ltcHRvbURpc2Vhc2VTdXJmYWNlRm9ybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgImNjc0NvZGUiOiAiMTAwIiwgInN5bXB0b21EaXNlYXNlTm9ybWFsaXplZE5hbWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgImljZDlDb2RlIjogIjQxMC45MCIsICJoY2NDb2RlIjogIjg2IiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjk5NCwgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDMsICJkaXNjdXNzZWRTY29yZSI6IDAuMDA0fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wMjEsICJzeW1wdG9tU2NvcmUiOiAwLjAwMSwgInRyYXVtYVNjb3JlIjogMC4wLCAiZmFtaWx5SGlzdG9yeVNjb3JlIjogMC4wfX0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19XSwgInNwZWxsQ29ycmVjdGVkVGV4dCI6IFt7ImNvcnJlY3RlZFRleHQiOiAiVGhlIHBhdGllbnQgaGFkIGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIGluIDIwMTUgYW5kIHdhcyBwcmVzY3JpYmVkIExvc2FydGFuLlxuIn1dLCAidGVtcG9yYWxTcGFucyI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfX1dfQ=="
                      }
                    },
                    {
                      "extension": [
                        {
                          "extension": [
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                              "valueString": "Losartan"
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                              "valueInteger": 67
                            },
                            {
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                              "valueInteger": 75
                            },
                            {
                              "extension": [
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/method",
                                  "valueCodeableConcept": {
                                    "coding": [
                                      {
                                        "code": "Medication_Taken_Score",
                                        "system": "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method"
                                      }
                                    ]
                                  }
                                },
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
                                  "valueDecimal": 1
                                },
                                {
                                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
                                  "valueString": "Medication Taken Score"
                                }
                              ],
                              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
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
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/acd",
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
              "display": "Losartan",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
            },
            {
              "code": "52175",
              "system": "http://www.nlm.nih.gov/research/umls/rxnorm"
            }
          ],
          "text": "Losartan"
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
