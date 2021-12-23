# Tutorial
----------------------------------------------
## QuickUMLS
QuickUMLS is a service designed for fast, unsupervised concept extraction from medical text. The code base and documentation is located [here](https://github.com/Georgetown-IR-Lab/QuickUMLS#readme). Another great article on the technology can be found [here](https://towardsdatascience.com/doing-almost-as-much-with-much-less-a-case-study-in-biomedical-named-entity-recognition-efa4abe18ed).

The nlp-insights service has been designed to allow QuickUMLS to be utilized for concept detection and extraction of text within FHIR resources.


### Prereqs
* You must have access to a deployed QuickUMLS service to complete this tutorial. Instructions to start a server on your local machine are described [here:](https://github.com/Georgetown-IR-Lab/QuickUMLS#server--client-support)
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
                        "data": "W3siY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwNDI4OTUzIiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDAzNCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFsiMjYwNzM1NTAxMCIsICIxMDgzMTkwMTkiLCAiMjU2NDYwMDExIiwgIjUyMDg4ODAxMiIsICIyMjQzNjgwMTkiLCAiMjI0MzYxMDEzIiwgIjUyMDg4MDAxNyIsICIyNTY0NTIwMTAiLCAiMzMwMDM3NTAxNCIsICIzMzAwMzc2MDEwIiwgIjMzMDAzNzcwMTgiLCAiNTQ2MjQ4MDExIiwgIjI3NDg4NzgwMTAiLCAiNTQ2MjQwMDE2IiwgIjI3MzA3NTgwMTAiLCAiODA0NjU2MDE3IiwgIjI2MDczNjIwMTgiLCAiMjYxOTIyMTAxNCIsICIyNjE5MjE0MDE0IiwgIjI2MTI0OTcwMTUiLCAiMjYyMDk3NzAxMiIsICIyNjkzMTU5MDE0Il0sICJzdGFydCI6IDAsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMjkyNjA2MyIsICJlbmQiOiAyMSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQyMDEiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODEwODE0IiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA2MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAwLCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAwMjcwNTEiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC45NSwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9ucyJ9LCB7ImN1aSI6ICJDMDE1NTY2OCIsICJlbmQiOiAyMSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjgyNjA4Njk1NjUyMTczOTEsICJzbm9tZWRfY3QiOiBbIjI0MTc5ODAxNiIsICIyOTk3NTIwMTgiLCAiNDAzMTAxMSIsICI1MzU2MjEwMTIiLCAiMjk5NzUxMDEzIiwgIjQwMzIwMTYiLCAiMTIyMTU2NDAxMCIsICIyNzQwOTk0MDE3IiwgIjc0NDg2ODAxMyIsICI1Nzg4NTcwMTAiLCAiMjk5NzU0MDE3IiwgIjI5OTc1MzAxMSIsICIyNzQ4ODU0MDE3Il0sICJzdGFydCI6IDAsICJ0ZXJtIjogIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0Mjg5NTMiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDM0Il0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogWyIyNjA3MzU1MDEwIiwgIjEwODMxOTAxOSIsICIyNTY0NjAwMTEiLCAiNTIwODg4MDEyIiwgIjIyNDM2ODAxOSIsICIyMjQzNjEwMTMiLCAiNTIwODgwMDE3IiwgIjI1NjQ1MjAxMCIsICIzMzAwMzc1MDE0IiwgIjMzMDAzNzYwMTAiLCAiMzMwMDM3NzAxOCIsICI1NDYyNDgwMTEiLCAiMjc0ODg3ODAxMCIsICI1NDYyNDAwMTYiLCAiMjczMDc1ODAxMCIsICI4MDQ2NTYwMTciLCAiMjYwNzM2MjAxOCIsICIyNjE5MjIxMDE0IiwgIjI2MTkyMTQwMTQiLCAiMjYxMjQ5NzAxNSIsICIyNjIwOTc3MDEyIiwgIjI2OTMxNTkwMTQiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAiZWNnIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQ4OTU3NyIsICJlbmQiOiAyMSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQyMDEiXSwgInNpbWlsYXJpdHkiOiAwLjgyNjA4Njk1NjUyMTczOTEsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFnZSJ9LCB7ImN1aSI6ICJDMzY0MDkxMSIsICJlbmQiOiAyMSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjgyNjA4Njk1NjUyMTczOTEsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDAyNzA1MSIsICJlbmQiOiAyMSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDAsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiAobWkpIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzkxNjY2NjY2NjY2NjY2NiwgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMCwgInRlcm0iOiAicGFzdCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0Mjg5NTMiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDM0Il0sICJzaW1pbGFyaXR5IjogMC43OTE2NjY2NjY2NjY2NjY2LCAic25vbWVkX2N0IjogWyIyNjA3MzU1MDEwIiwgIjEwODMxOTAxOSIsICIyNTY0NjAwMTEiLCAiNTIwODg4MDEyIiwgIjIyNDM2ODAxOSIsICIyMjQzNjEwMTMiLCAiNTIwODgwMDE3IiwgIjI1NjQ1MjAxMCIsICIzMzAwMzc1MDE0IiwgIjMzMDAzNzYwMTAiLCAiMzMwMDM3NzAxOCIsICI1NDYyNDgwMTEiLCAiMjc0ODg3ODAxMCIsICI1NDYyNDAwMTYiLCAiMjczMDc1ODAxMCIsICI4MDQ2NTYwMTciLCAiMjYwNzM2MjAxOCIsICIyNjE5MjIxMDE0IiwgIjI2MTkyMTQwMTQiLCAiMjYxMjQ5NzAxNSIsICIyNjIwOTc3MDEyIiwgIjI2OTMxNTkwMTQiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAiZWNnOiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAwMjcwNTEiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uLCAobWkpIn0sIHsiY3VpIjogIkMwMTU1NjI2IiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbIjI0MTc5NTAxOCIsICIzOTU4NTgwMTkiLCAiMjk5NzAyMDEwIiwgIjk0ODg0MDE3IiwgIjk0ODg1MDE2IiwgIjI5OTcyMTAxOSIsICIxMjMxNjc4MDExIiwgIjI5OTY5OTAxNSIsICIzOTU4NjIwMTMiLCAiMjQxNzkzMDEzIiwgIjI0MTc5NDAxOSIsICIzOTU4NTcwMTIiLCAiMjk5NzA1MDEyIiwgIjc5NTYzNDAxMyIsICI1Nzg4MzgwMTgiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzNTQxOTUwIiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDAzMyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjI2IiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbIjI0MTc5NTAxOCIsICIzOTU4NTgwMTkiLCAiMjk5NzAyMDEwIiwgIjk0ODg0MDE3IiwgIjk0ODg1MDE2IiwgIjI5OTcyMTAxOSIsICIxMjMxNjc4MDExIiwgIjI5OTY5OTAxNSIsICIzOTU4NjIwMTMiLCAiMjQxNzkzMDEzIiwgIjI0MTc5NDAxOSIsICIzOTU4NTcwMTIiLCAiMjk5NzA1MDEyIiwgIjc5NTYzNDAxMyIsICI1Nzg4MzgwMTgiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIGFjdXRlIn0sIHsiY3VpIjogIkMzODI5OTEwIiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDE3MCJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAiaGFkIGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwNzQ2NzI3IiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMjM0ODM2MiIsICJlbmQiOiAyMSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDAsICJ0ZXJtIjogInNlcHRhbCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAxNTU2NjgiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogWyIyNDE3OTgwMTYiLCAiMjk5NzUyMDE4IiwgIjQwMzEwMTEiLCAiNTM1NjIxMDEyIiwgIjI5OTc1MTAxMyIsICI0MDMyMDE2IiwgIjEyMjE1NjQwMTAiLCAiMjc0MDk5NDAxNyIsICI3NDQ4NjgwMTMiLCAiNTc4ODU3MDEwIiwgIjI5OTc1NDAxNyIsICIyOTk3NTMwMTEiLCAiMjc0ODg1NDAxNyJdLCAic3RhcnQiOiAwLCAidGVybSI6ICJoZWFsZWQgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMzQwMzI0IiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFsiMjk5Njk4MDExIiwgIjM1MDM3NjAxNCIsICIzNTAzNzcwMTciLCAiNjIyMDgzMDEzIl0sICJzdGFydCI6IDAsICJ0ZXJtIjogInNpbGVudCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTIiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDAsICJ0ZXJtIjogInR5cGUgNSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTYiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDAsICJ0ZXJtIjogInR5cGUgMyBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTciLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMTcwIl0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDAsICJ0ZXJtIjogInR5cGUgMiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTgiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDAsICJ0ZXJtIjogInR5cGUgMSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzI4MjUxNTkiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMjAxIl0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDAsICJ0ZXJtIjogImRhdGUgb2YgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODQ1NTAyIiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAwLCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24sIHN0cm9rZSJ9LCB7ImN1aSI6ICJDMzg5ODY1MyIsICJlbmQiOiAyMSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjcwMzcwMzcwMzcwMzcwMzcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAidHlwZSA0YyBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTQiLCAiZW5kIjogMjEsICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDAsICJ0ZXJtIjogInR5cGUgNGIgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU1IiwgImVuZCI6IDIxLCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAwLCAidGVybSI6ICJ0eXBlIDRhIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9XQ=="
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
In this example, a bundle with two allergy intolreance resources is sent to the nlp insights server. The first has a code with text "peanut", and the second resource has a code with text "amoxicillin".

Both resources contain only text and do not contain any codes for the allergy. The nlp-insights service will enrich the resources with a UMLS code for the provided text.

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
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
                        "data": "W3siY3VpIjogIkMwNTU5NDcwIiwgImVuZCI6IDE0LCAibmdyYW0iOiAicGVhbnV0IGFsbGVyZ3kiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogWyIxNTIzMDYwMTgiLCAiNTk4OTIwMDEyIiwgIjMyNDc3ODAxNyIsICI4MzUzNTMwMTQiXSwgInN0YXJ0IjogMCwgInRlcm0iOiAicGVhbnV0IGFsbGVyZ3kifSwgeyJjdWkiOiAiQzA5MTc5MTgiLCAiZW5kIjogMTQsICJuZ3JhbSI6ICJwZWFudXQgYWxsZXJneSIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjgsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMCwgInRlcm0iOiAiaHgtcGVhbnV0IGFsbGVyZ3kifSwgeyJjdWkiOiAiQzA1Nzc2MjAiLCAiZW5kIjogMTQsICJuZ3JhbSI6ICJwZWFudXQgYWxsZXJneSIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc1LCAic25vbWVkX2N0IjogWyIxNDg5MzExMDE4IiwgIjE0Njk1OTQwMTkiLCAiMTIzNTcxNDAxOSIsICIxNTIzMDUwMTkiLCAiMzI4NjEwNTAxMyIsICIzMjg2MDc0MDEwIiwgIjMwODQ1MzAwMTciLCAiODM1MzUyMDE2Il0sICJzdGFydCI6IDAsICJ0ZXJtIjogIm51dCBhbGxlcmd5In1d"
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
              "display": "peanut allergy",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
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
                    "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
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
                        "data": "W3siY3VpIjogIkMwNTcxNDE3IiwgImVuZCI6IDE5LCAibmdyYW0iOiAiYW1veGljaWxsaW4gYWxsZXJneSIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjI0NzYzMDkwMTYiLCAiNDM0NzgyMDEwIiwgIjI5NTk3NTgwMTQiLCAiNjg5NTEzMDE2Il0sICJzdGFydCI6IDAsICJ0ZXJtIjogImFtb3hpY2lsbGluIGFsbGVyZ3kifV0="
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
              "display": "amoxicillin allergy",
              "system": "http://terminology.hl7.org/CodeSystem/umls"
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

The returned bundle has a derived condition resource (myocardial infarction), and also a derived medication resource (for Losartan). Each resource has an insight detail extension that provides the evidence that was used to derive these resources.

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
                        "data": "W3siY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyOTI2MDYzIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODEwODE0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA2MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuOTUsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb25zIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0Mjg5NTMiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDM0Il0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogWyIyNjA3MzU1MDEwIiwgIjEwODMxOTAxOSIsICIyNTY0NjAwMTEiLCAiNTIwODg4MDEyIiwgIjIyNDM2ODAxOSIsICIyMjQzNjEwMTMiLCAiNTIwODgwMDE3IiwgIjI1NjQ1MjAxMCIsICIzMzAwMzc1MDE0IiwgIjMzMDAzNzYwMTAiLCAiMzMwMDM3NzAxOCIsICI1NDYyNDgwMTEiLCAiMjc0ODg3ODAxMCIsICI1NDYyNDAwMTYiLCAiMjczMDc1ODAxMCIsICI4MDQ2NTYwMTciLCAiMjYwNzM2MjAxOCIsICIyNjE5MjIxMDE0IiwgIjI2MTkyMTQwMTQiLCAiMjYxMjQ5NzAxNSIsICIyNjIwOTc3MDEyIiwgIjI2OTMxNTkwMTQiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0ODk1NzciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMjAxIl0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gYWdlIn0sIHsiY3VpIjogIkMzNjQwOTExIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDAzMyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDAyNzA1MSIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTY2OCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI0MTc5ODAxNiIsICIyOTk3NTIwMTgiLCAiNDAzMTAxMSIsICI1MzU2MjEwMTIiLCAiMjk5NzUxMDEzIiwgIjQwMzIwMTYiLCAiMTIyMTU2NDAxMCIsICIyNzQwOTk0MDE3IiwgIjc0NDg2ODAxMyIsICI1Nzg4NTcwMTAiLCAiMjk5NzU0MDE3IiwgIjI5OTc1MzAxMSIsICIyNzQ4ODU0MDE3Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJwYXN0IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZWNnOiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAwMjcwNTEiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTYyNiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogWyIyNDE3OTUwMTgiLCAiMzk1ODU4MDE5IiwgIjI5OTcwMjAxMCIsICI5NDg4NDAxNyIsICI5NDg4NTAxNiIsICIyOTk3MjEwMTkiLCAiMTIzMTY3ODAxMSIsICIyOTk2OTkwMTUiLCAiMzk1ODYyMDEzIiwgIjI0MTc5MzAxMyIsICIyNDE3OTQwMTkiLCAiMzk1ODU3MDEyIiwgIjI5OTcwNTAxMiIsICI3OTU2MzQwMTMiLCAiNTc4ODM4MDE4Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM1NDE5NTAiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjI2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbIjI0MTc5NTAxOCIsICIzOTU4NTgwMTkiLCAiMjk5NzAyMDEwIiwgIjk0ODg0MDE3IiwgIjk0ODg1MDE2IiwgIjI5OTcyMTAxOSIsICIxMjMxNjc4MDExIiwgIjI5OTY5OTAxNSIsICIzOTU4NjIwMTMiLCAiMjQxNzkzMDEzIiwgIjI0MTc5NDAxOSIsICIzOTU4NTcwMTIiLCAiMjk5NzA1MDEyIiwgIjc5NTYzNDAxMyIsICI1Nzg4MzgwMTgiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiBhY3V0ZSJ9LCB7ImN1aSI6ICJDMzgyOTkxMCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA3NDY3MjciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMjM0ODM2MiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJzZXB0YWwgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImhlYWxlZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAzNDAzMjQiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogWyIyOTk2OTgwMTEiLCAiMzUwMzc2MDE0IiwgIjM1MDM3NzAxNyIsICI2MjIwODMwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInNpbGVudCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSAzIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMzg5ODY1NyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjczMDc2OTIzMDc2OTIzMDcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgMiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTgiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyODI1MTU5IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4NDU1MDIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24sIHN0cm9rZSJ9LCB7ImN1aSI6ICJDMzg5ODY1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjcwMzcwMzcwMzcwMzcwMzcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgNGMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTUiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDRhIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDI3ODMyOSIsICJlbmQiOiA2NiwgIm5ncmFtIjogInByZXNjcmliZWQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDU4Il0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDU2LCAidGVybSI6ICJwcmVzY3JpYmVkIn0sIHsiY3VpIjogIkMwMTI2MTc0IiwgImVuZCI6IDc1LCAibmdyYW0iOiAiTG9zYXJ0YW4iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMTA5IiwgIlQxMjEiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjEyMTIwMzQwMTEiLCAiMTU5NDEzMDE1IiwgIjM0ODg5OTkwMTUiLCAiMzQ5OTg4NTAxMSIsICIxMjA1NDU0MDE3IiwgIjg0MDY0NTAxNCIsICIxMTk4ODY3MDEzIl0sICJzdGFydCI6IDY3LCAidGVybSI6ICJsb3NhcnRhbiJ9LCB7ImN1aSI6ICJDMTU1MDY1NSIsICJlbmQiOiAxMSwgIm5ncmFtIjogInBhdGllbnQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMxIl0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDQsICJ0ZXJtIjogInBhdGllbnQifSwgeyJjdWkiOiAiQzE1Nzg0ODUiLCAiZW5kIjogMTEsICJuZ3JhbSI6ICJwYXRpZW50IiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDE3MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiA0LCAidGVybSI6ICJwYXRpZW50In0sIHsiY3VpIjogIkMxNTc4NDg2IiwgImVuZCI6IDExLCAibmdyYW0iOiAicGF0aWVudCIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogNCwgInRlcm0iOiAicGF0aWVudCJ9XQ=="
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
                        "data": "W3siY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyOTI2MDYzIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODEwODE0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA2MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuOTUsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb25zIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0Mjg5NTMiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDM0Il0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogWyIyNjA3MzU1MDEwIiwgIjEwODMxOTAxOSIsICIyNTY0NjAwMTEiLCAiNTIwODg4MDEyIiwgIjIyNDM2ODAxOSIsICIyMjQzNjEwMTMiLCAiNTIwODgwMDE3IiwgIjI1NjQ1MjAxMCIsICIzMzAwMzc1MDE0IiwgIjMzMDAzNzYwMTAiLCAiMzMwMDM3NzAxOCIsICI1NDYyNDgwMTEiLCAiMjc0ODg3ODAxMCIsICI1NDYyNDAwMTYiLCAiMjczMDc1ODAxMCIsICI4MDQ2NTYwMTciLCAiMjYwNzM2MjAxOCIsICIyNjE5MjIxMDE0IiwgIjI2MTkyMTQwMTQiLCAiMjYxMjQ5NzAxNSIsICIyNjIwOTc3MDEyIiwgIjI2OTMxNTkwMTQiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0ODk1NzciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMjAxIl0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gYWdlIn0sIHsiY3VpIjogIkMzNjQwOTExIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDAzMyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDAyNzA1MSIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTY2OCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI0MTc5ODAxNiIsICIyOTk3NTIwMTgiLCAiNDAzMTAxMSIsICI1MzU2MjEwMTIiLCAiMjk5NzUxMDEzIiwgIjQwMzIwMTYiLCAiMTIyMTU2NDAxMCIsICIyNzQwOTk0MDE3IiwgIjc0NDg2ODAxMyIsICI1Nzg4NTcwMTAiLCAiMjk5NzU0MDE3IiwgIjI5OTc1MzAxMSIsICIyNzQ4ODU0MDE3Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJwYXN0IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZWNnOiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAwMjcwNTEiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTYyNiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogWyIyNDE3OTUwMTgiLCAiMzk1ODU4MDE5IiwgIjI5OTcwMjAxMCIsICI5NDg4NDAxNyIsICI5NDg4NTAxNiIsICIyOTk3MjEwMTkiLCAiMTIzMTY3ODAxMSIsICIyOTk2OTkwMTUiLCAiMzk1ODYyMDEzIiwgIjI0MTc5MzAxMyIsICIyNDE3OTQwMTkiLCAiMzk1ODU3MDEyIiwgIjI5OTcwNTAxMiIsICI3OTU2MzQwMTMiLCAiNTc4ODM4MDE4Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM1NDE5NTAiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjI2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbIjI0MTc5NTAxOCIsICIzOTU4NTgwMTkiLCAiMjk5NzAyMDEwIiwgIjk0ODg0MDE3IiwgIjk0ODg1MDE2IiwgIjI5OTcyMTAxOSIsICIxMjMxNjc4MDExIiwgIjI5OTY5OTAxNSIsICIzOTU4NjIwMTMiLCAiMjQxNzkzMDEzIiwgIjI0MTc5NDAxOSIsICIzOTU4NTcwMTIiLCAiMjk5NzA1MDEyIiwgIjc5NTYzNDAxMyIsICI1Nzg4MzgwMTgiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiBhY3V0ZSJ9LCB7ImN1aSI6ICJDMzgyOTkxMCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA3NDY3MjciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMjM0ODM2MiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJzZXB0YWwgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImhlYWxlZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAzNDAzMjQiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogWyIyOTk2OTgwMTEiLCAiMzUwMzc2MDE0IiwgIjM1MDM3NzAxNyIsICI2MjIwODMwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInNpbGVudCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSAzIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMzg5ODY1NyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjczMDc2OTIzMDc2OTIzMDcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgMiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTgiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyODI1MTU5IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4NDU1MDIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24sIHN0cm9rZSJ9LCB7ImN1aSI6ICJDMzg5ODY1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjcwMzcwMzcwMzcwMzcwMzcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgNGMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTUiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDRhIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDI3ODMyOSIsICJlbmQiOiA2NiwgIm5ncmFtIjogInByZXNjcmliZWQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDU4Il0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDU2LCAidGVybSI6ICJwcmVzY3JpYmVkIn0sIHsiY3VpIjogIkMwMTI2MTc0IiwgImVuZCI6IDc1LCAibmdyYW0iOiAiTG9zYXJ0YW4iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMTA5IiwgIlQxMjEiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjEyMTIwMzQwMTEiLCAiMTU5NDEzMDE1IiwgIjM0ODg5OTkwMTUiLCAiMzQ5OTg4NTAxMSIsICIxMjA1NDU0MDE3IiwgIjg0MDY0NTAxNCIsICIxMTk4ODY3MDEzIl0sICJzdGFydCI6IDY3LCAidGVybSI6ICJsb3NhcnRhbiJ9LCB7ImN1aSI6ICJDMTU1MDY1NSIsICJlbmQiOiAxMSwgIm5ncmFtIjogInBhdGllbnQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMxIl0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDQsICJ0ZXJtIjogInBhdGllbnQifSwgeyJjdWkiOiAiQzE1Nzg0ODUiLCAiZW5kIjogMTEsICJuZ3JhbSI6ICJwYXRpZW50IiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDE3MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiA0LCAidGVybSI6ICJwYXRpZW50In0sIHsiY3VpIjogIkMxNTc4NDg2IiwgImVuZCI6IDExLCAibmdyYW0iOiAicGF0aWVudCIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogNCwgInRlcm0iOiAicGF0aWVudCJ9XQ=="
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
