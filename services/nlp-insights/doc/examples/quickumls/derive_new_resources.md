# Derive New Resources with nlp-insights and QuickUMLS
Some resources such as DiagnosticReports and DocumentReferences contain clinical notes or other unstructured text. When the nlp-insights service receives one of these resources, it can derive new FHIR resources for detected concepts.

nlp-insights can derive new resources from:

* DiagnosticReport  (from the text at the path *DiagnosticReport.presentedForm[].data*)
* DocumentReference (from the text at the path *DocumentReference.content[].attachment.data*)

Two types of FHIR resources can be derived by the service:
* Condition
* MedicationStatement

## Configure nlp-insights to use QuickUMLS for NLP
If the nlp-insights service has not been configured to use QuickUMLS by default, follow the steps [here](./configure_quickumls.md).

## Derive New Resources from a Diagnostic Report

This example creates a diagnostic report where the text mentions a condition (*myocardial infarction*) and a medication (*Losartan*).

The Text data in a diagnostic report must be base64 encoded, which can be done with the base64 command in bash.

```
B64_REPORT_TEXT=$(echo 'The patient had a myocardial infarction in 2015 and was prescribed Losartan.' | base64 -w 0)
```

The text can now be included in a diagnostic report and sent to the nlp-insights service. The curl command stores the response json in a file /tmp/output for future analysis.


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

`cat /tmp/output | jq`

<details><summary>Returned Bundle</summary>

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
                    "value": "3667c29882ecfe50d9cbaf162ef5df199e406563770186c7e637c234"
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
                      "valueString": "DiagnosticReport.presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W3siY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyOTI2MDYzIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODEwODE0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA2MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuOTUsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb25zIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0Mjg5NTMiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDM0Il0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogWyIyNjA3MzU1MDEwIiwgIjEwODMxOTAxOSIsICIyNTY0NjAwMTEiLCAiNTIwODg4MDEyIiwgIjIyNDM2ODAxOSIsICIyMjQzNjEwMTMiLCAiNTIwODgwMDE3IiwgIjI1NjQ1MjAxMCIsICIzMzAwMzc1MDE0IiwgIjMzMDAzNzYwMTAiLCAiMzMwMDM3NzAxOCIsICI1NDYyNDgwMTEiLCAiMjc0ODg3ODAxMCIsICI1NDYyNDAwMTYiLCAiMjczMDc1ODAxMCIsICI4MDQ2NTYwMTciLCAiMjYwNzM2MjAxOCIsICIyNjE5MjIxMDE0IiwgIjI2MTkyMTQwMTQiLCAiMjYxMjQ5NzAxNSIsICIyNjIwOTc3MDEyIiwgIjI2OTMxNTkwMTQiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0ODk1NzciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMjAxIl0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gYWdlIn0sIHsiY3VpIjogIkMzNjQwOTExIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDAzMyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDAyNzA1MSIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTY2OCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI0MTc5ODAxNiIsICIyOTk3NTIwMTgiLCAiNDAzMTAxMSIsICI1MzU2MjEwMTIiLCAiMjk5NzUxMDEzIiwgIjQwMzIwMTYiLCAiMTIyMTU2NDAxMCIsICIyNzQwOTk0MDE3IiwgIjc0NDg2ODAxMyIsICI1Nzg4NTcwMTAiLCAiMjk5NzU0MDE3IiwgIjI5OTc1MzAxMSIsICIyNzQ4ODU0MDE3Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJwYXN0IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZWNnOiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAwMjcwNTEiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTYyNiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogWyIyNDE3OTUwMTgiLCAiMzk1ODU4MDE5IiwgIjI5OTcwMjAxMCIsICI5NDg4NDAxNyIsICI5NDg4NTAxNiIsICIyOTk3MjEwMTkiLCAiMTIzMTY3ODAxMSIsICIyOTk2OTkwMTUiLCAiMzk1ODYyMDEzIiwgIjI0MTc5MzAxMyIsICIyNDE3OTQwMTkiLCAiMzk1ODU3MDEyIiwgIjI5OTcwNTAxMiIsICI3OTU2MzQwMTMiLCAiNTc4ODM4MDE4Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM1NDE5NTAiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjI2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbIjI0MTc5NTAxOCIsICIzOTU4NTgwMTkiLCAiMjk5NzAyMDEwIiwgIjk0ODg0MDE3IiwgIjk0ODg1MDE2IiwgIjI5OTcyMTAxOSIsICIxMjMxNjc4MDExIiwgIjI5OTY5OTAxNSIsICIzOTU4NjIwMTMiLCAiMjQxNzkzMDEzIiwgIjI0MTc5NDAxOSIsICIzOTU4NTcwMTIiLCAiMjk5NzA1MDEyIiwgIjc5NTYzNDAxMyIsICI1Nzg4MzgwMTgiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiBhY3V0ZSJ9LCB7ImN1aSI6ICJDMzgyOTkxMCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA3NDY3MjciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMjM0ODM2MiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJzZXB0YWwgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImhlYWxlZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAzNDAzMjQiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogWyIyOTk2OTgwMTEiLCAiMzUwMzc2MDE0IiwgIjM1MDM3NzAxNyIsICI2MjIwODMwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInNpbGVudCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSAzIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMzg5ODY1NyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjczMDc2OTIzMDc2OTIzMDcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgMiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTgiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyODI1MTU5IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4NDU1MDIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24sIHN0cm9rZSJ9LCB7ImN1aSI6ICJDMzg5ODY1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjcwMzcwMzcwMzcwMzcwMzcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgNGMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTUiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDRhIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDI3ODMyOSIsICJlbmQiOiA2NiwgIm5ncmFtIjogInByZXNjcmliZWQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDU4Il0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDU2LCAidGVybSI6ICJwcmVzY3JpYmVkIn0sIHsiY3VpIjogIkMwMTI2MTc0IiwgImVuZCI6IDc1LCAibmdyYW0iOiAiTG9zYXJ0YW4iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMTIxIiwgIlQxMDkiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjEyMTIwMzQwMTEiLCAiMTU5NDEzMDE1IiwgIjM0ODg5OTkwMTUiLCAiMzQ5OTg4NTAxMSIsICIxMjA1NDU0MDE3IiwgIjg0MDY0NTAxNCIsICIxMTk4ODY3MDEzIl0sICJzdGFydCI6IDY3LCAidGVybSI6ICJsb3NhcnRhbiJ9LCB7ImN1aSI6ICJDMTU1MDY1NSIsICJlbmQiOiAxMSwgIm5ncmFtIjogInBhdGllbnQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMxIl0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDQsICJ0ZXJtIjogInBhdGllbnQifSwgeyJjdWkiOiAiQzE1Nzg0ODUiLCAiZW5kIjogMTEsICJuZ3JhbSI6ICJwYXRpZW50IiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDE3MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiA0LCAidGVybSI6ICJwYXRpZW50In0sIHsiY3VpIjogIkMxNTc4NDg2IiwgImVuZCI6IDExLCAibmdyYW0iOiAicGF0aWVudCIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogNCwgInRlcm0iOiAicGF0aWVudCJ9XQ=="
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
                  "value": "3667c29882ecfe50d9cbaf162ef5df199e406563770186c7e637c234"
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
                    "value": "9dec57cd4b3e8e635fd86a993edd4d40dd609200597aa0550b7d5f0f"
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
                      "valueString": "DiagnosticReport.presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "W3siY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyOTI2MDYzIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODEwODE0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA2MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuOTUsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb25zIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0Mjg5NTMiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDM0Il0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogWyIyNjA3MzU1MDEwIiwgIjEwODMxOTAxOSIsICIyNTY0NjAwMTEiLCAiNTIwODg4MDEyIiwgIjIyNDM2ODAxOSIsICIyMjQzNjEwMTMiLCAiNTIwODgwMDE3IiwgIjI1NjQ1MjAxMCIsICIzMzAwMzc1MDE0IiwgIjMzMDAzNzYwMTAiLCAiMzMwMDM3NzAxOCIsICI1NDYyNDgwMTEiLCAiMjc0ODg3ODAxMCIsICI1NDYyNDAwMTYiLCAiMjczMDc1ODAxMCIsICI4MDQ2NTYwMTciLCAiMjYwNzM2MjAxOCIsICIyNjE5MjIxMDE0IiwgIjI2MTkyMTQwMTQiLCAiMjYxMjQ5NzAxNSIsICIyNjIwOTc3MDEyIiwgIjI2OTMxNTkwMTQiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0ODk1NzciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMjAxIl0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gYWdlIn0sIHsiY3VpIjogIkMzNjQwOTExIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDAzMyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDAyNzA1MSIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTY2OCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI0MTc5ODAxNiIsICIyOTk3NTIwMTgiLCAiNDAzMTAxMSIsICI1MzU2MjEwMTIiLCAiMjk5NzUxMDEzIiwgIjQwMzIwMTYiLCAiMTIyMTU2NDAxMCIsICIyNzQwOTk0MDE3IiwgIjc0NDg2ODAxMyIsICI1Nzg4NTcwMTAiLCAiMjk5NzU0MDE3IiwgIjI5OTc1MzAxMSIsICIyNzQ4ODU0MDE3Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJwYXN0IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZWNnOiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAwMjcwNTEiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTYyNiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogWyIyNDE3OTUwMTgiLCAiMzk1ODU4MDE5IiwgIjI5OTcwMjAxMCIsICI5NDg4NDAxNyIsICI5NDg4NTAxNiIsICIyOTk3MjEwMTkiLCAiMTIzMTY3ODAxMSIsICIyOTk2OTkwMTUiLCAiMzk1ODYyMDEzIiwgIjI0MTc5MzAxMyIsICIyNDE3OTQwMTkiLCAiMzk1ODU3MDEyIiwgIjI5OTcwNTAxMiIsICI3OTU2MzQwMTMiLCAiNTc4ODM4MDE4Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM1NDE5NTAiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjI2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbIjI0MTc5NTAxOCIsICIzOTU4NTgwMTkiLCAiMjk5NzAyMDEwIiwgIjk0ODg0MDE3IiwgIjk0ODg1MDE2IiwgIjI5OTcyMTAxOSIsICIxMjMxNjc4MDExIiwgIjI5OTY5OTAxNSIsICIzOTU4NjIwMTMiLCAiMjQxNzkzMDEzIiwgIjI0MTc5NDAxOSIsICIzOTU4NTcwMTIiLCAiMjk5NzA1MDEyIiwgIjc5NTYzNDAxMyIsICI1Nzg4MzgwMTgiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiBhY3V0ZSJ9LCB7ImN1aSI6ICJDMzgyOTkxMCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA3NDY3MjciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMjM0ODM2MiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJzZXB0YWwgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImhlYWxlZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAzNDAzMjQiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogWyIyOTk2OTgwMTEiLCAiMzUwMzc2MDE0IiwgIjM1MDM3NzAxNyIsICI2MjIwODMwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInNpbGVudCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSAzIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMzg5ODY1NyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjczMDc2OTIzMDc2OTIzMDcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgMiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTgiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyODI1MTU5IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4NDU1MDIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24sIHN0cm9rZSJ9LCB7ImN1aSI6ICJDMzg5ODY1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjcwMzcwMzcwMzcwMzcwMzcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgNGMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTUiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDRhIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDI3ODMyOSIsICJlbmQiOiA2NiwgIm5ncmFtIjogInByZXNjcmliZWQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDU4Il0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDU2LCAidGVybSI6ICJwcmVzY3JpYmVkIn0sIHsiY3VpIjogIkMwMTI2MTc0IiwgImVuZCI6IDc1LCAibmdyYW0iOiAiTG9zYXJ0YW4iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMTIxIiwgIlQxMDkiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjEyMTIwMzQwMTEiLCAiMTU5NDEzMDE1IiwgIjM0ODg5OTkwMTUiLCAiMzQ5OTg4NTAxMSIsICIxMjA1NDU0MDE3IiwgIjg0MDY0NTAxNCIsICIxMTk4ODY3MDEzIl0sICJzdGFydCI6IDY3LCAidGVybSI6ICJsb3NhcnRhbiJ9LCB7ImN1aSI6ICJDMTU1MDY1NSIsICJlbmQiOiAxMSwgIm5ncmFtIjogInBhdGllbnQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMxIl0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDQsICJ0ZXJtIjogInBhdGllbnQifSwgeyJjdWkiOiAiQzE1Nzg0ODUiLCAiZW5kIjogMTEsICJuZ3JhbSI6ICJwYXRpZW50IiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDE3MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiA0LCAidGVybSI6ICJwYXRpZW50In0sIHsiY3VpIjogIkMxNTc4NDg2IiwgImVuZCI6IDExLCAibmdyYW0iOiAicGF0aWVudCIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogNCwgInRlcm0iOiAicGF0aWVudCJ9XQ=="
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
                  "value": "9dec57cd4b3e8e635fd86a993edd4d40dd609200597aa0550b7d5f0f"
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
</details><br/>

The returned bundle has two entries with resources. These entries each have method *POST*, which tells us that these resources were created by nlp-insights. 

We'll look at the codes associated with these resources independently.

<!-- 
Command pipeline to generate the table

cat /tmp/output | jq -r '
["Resource Type", "Description"], 
["---", "---"] , 
(.entry[].resource | [.resourceType, .code.text // .medicationCodeableConcept.text]) 
| @tsv' | column -t -o "|" -s $'\t' 

-->

Resource Type      |Description
---                |---
Condition          |myocardial infarction
MedicationStatement|losartan

### Derived condition codes
Included in the condition is the UMLS code that was detected by QuickUMLS.

<!-- 
Command pipeline to generate the table

cat /tmp/output | jq -r '
["System", "Code", "Display"], 
["---", "---", "---"], 
(.entry[].resource | select(.resourceType == "Condition") | .code.coding[] | [.system, .code, .display]) 
| @tsv' | column -t -o "|" -s $'\t' 

-->

System                                    |Code    |Display
---                                       |---     |---
http://terminology.hl7.org/CodeSystem/umls|C0027051|

### Derived MedicationStatement codes
The derived MedicationStatement also contains the UMLS code that was detected by QuickUMLS

<!--
Command to generate the table

 cat /tmp/output | jq -r '
 ["System", "Code", "Display"],
 ["---", "---", "---"],
 (.entry[].resource | 
  select(.resourceType == "MedicationStatement") | 
  .medicationCodeableConcept.coding[] |
  [.system, .code, .display]
 ) 
 | @tsv' | column -t -o "|" -s $'\t' 
 
 -->
 
 System                                    |Code    |Display
---                                       |---     |---
http://terminology.hl7.org/CodeSystem/umls|C0126174|
 
 
## Evidence
The structure of derived resources is based on the [Alvearie FHIR IG](https://alvearie.io/alvearie-fhir-ig/index.html).

The nlp-insights service adds detailed information to the derived resource to explain what caused the resource to be created. 

### Insight Summary
Each derived resource has an insight summary extension.

The summary extension for the derived Condition looks like this:
<!--
command to generate the json

cat /tmp/output | jq -r '.entry[].resource | select(.resourceType == "Condition") | .extension[0]'

-->

```json
{
  "extension": [
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
      "valueIdentifier": {
        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
        "value": "3667c29882ecfe50d9cbaf162ef5df199e406563770186c7e637c234"
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

```

The insight id has a system and identifier that together identify the insight. In this example, the system tells us that the insight was discovered using QuickUMLS. The identifier value is unique (within the system) to this insight.

The category tells us that the resource was created using Natural Language Processing.

### Insight Extension in Resource Meta
The insight identified by the summary extension has an insight extension in the resource's meta. The insight extension contains lots of details about what the insight applies to and why it was created. 

Although the alvearie FHIR IG supports multiple insights, nlp-insights will create a single insight in the meta when a resource is derived. Other services are able to additional insights if they choose to.

<!-- 
 jq code to extract the extension
 
 cat /tmp/output | jq -r '.entry[].resource | select(.resourceType == "Condition") | .meta.extension[0]'

-->

<details><summary>Insight extension for the derived Condition</summary>

```json
{
  "extension": [
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
      "valueIdentifier": {
        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
        "value": "3667c29882ecfe50d9cbaf162ef5df199e406563770186c7e637c234"
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
ntl:nlp-insights$ cat /tmp/output | jq -r '.entry[].resource | select(.resourceType == "Condition") | .meta.extension[0]
> '
{
  "extension": [
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
      "valueIdentifier": {
        "system": "urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
        "value": "3667c29882ecfe50d9cbaf162ef5df199e406563770186c7e637c234"
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
          "valueString": "DiagnosticReport.presentedForm[0].data"
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
          "valueAttachment": {
            "contentType": "application/json",
            "data": "W3siY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyOTI2MDYzIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODEwODE0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA2MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMDI3MDUxIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuOTUsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb25zIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm9sZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0Mjg5NTMiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDM0Il0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogWyIyNjA3MzU1MDEwIiwgIjEwODMxOTAxOSIsICIyNTY0NjAwMTEiLCAiNTIwODg4MDEyIiwgIjIyNDM2ODAxOSIsICIyMjQzNjEwMTMiLCAiNTIwODgwMDE3IiwgIjI1NjQ1MjAxMCIsICIzMzAwMzc1MDE0IiwgIjMzMDAzNzYwMTAiLCAiMzMwMDM3NzAxOCIsICI1NDYyNDgwMTEiLCAiMjc0ODg3ODAxMCIsICI1NDYyNDAwMTYiLCAiMjczMDc1ODAxMCIsICI4MDQ2NTYwMTciLCAiMjYwNzM2MjAxOCIsICIyNjE5MjIxMDE0IiwgIjI2MTkyMTQwMTQiLCAiMjYxMjQ5NzAxNSIsICIyNjIwOTc3MDEyIiwgIjI2OTMxNTkwMTQiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImVjZyBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA0ODk1NzciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMjAxIl0sICJzaW1pbGFyaXR5IjogMC44MjYwODY5NTY1MjE3MzkxLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gYWdlIn0sIHsiY3VpIjogIkMzNjQwOTExIiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDAzMyJdLCAic2ltaWxhcml0eSI6IDAuODI2MDg2OTU2NTIxNzM5MSwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAibmV3IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDAyNzA1MSIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjUwMDQ0ODAxOSIsICIzNTAzNTcwMTIiLCAiNjIyMDYyMDE5IiwgIjM3NDM2MDE0IiwgIjM3NDM3MDE3IiwgIjI5OTcwMzAxNyIsICIyNDE3OTIwMTUiLCAiMzk1ODYwMDE3IiwgIjUwMDQ0OTAxMCIsICIyOTk3MDAwMTkiLCAiMzk1ODYxMDE4IiwgIjI0MTc5MTAxMCIsICIzNzQ0MzAxNSIsICIzNzQ0MDAxNyIsICIzNzQ0MTAxOCIsICIzNzQzODAxMCIsICIyNDE3OTAwMTEiLCAiNTAwNDUwMDEwIiwgIjM5NTg2MzAxNSIsICIxNzg0ODczMDEyIiwgIjM3NDQyMDEzIiwgIjM3NDM5MDE5IiwgIjUwMDQ1MjAxOSIsICIxNzg0ODcyMDE5IiwgIjI3NDcxMTcwMTQiLCAiNzUxNjg5MDEzIl0sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24gKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTY2OCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI0MTc5ODAxNiIsICIyOTk3NTIwMTgiLCAiNDAzMTAxMSIsICI1MzU2MjEwMTIiLCAiMjk5NzUxMDEzIiwgIjQwMzIwMTYiLCAiMTIyMTU2NDAxMCIsICIyNzQwOTk0MDE3IiwgIjc0NDg2ODAxMyIsICI1Nzg4NTcwMTAiLCAiMjk5NzU0MDE3IiwgIjI5OTc1MzAxMSIsICIyNzQ4ODU0MDE3Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJwYXN0IG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDQyODk1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzQiXSwgInNpbWlsYXJpdHkiOiAwLjc5MTY2NjY2NjY2NjY2NjYsICJzbm9tZWRfY3QiOiBbIjI2MDczNTUwMTAiLCAiMTA4MzE5MDE5IiwgIjI1NjQ2MDAxMSIsICI1MjA4ODgwMTIiLCAiMjI0MzY4MDE5IiwgIjIyNDM2MTAxMyIsICI1MjA4ODAwMTciLCAiMjU2NDUyMDEwIiwgIjMzMDAzNzUwMTQiLCAiMzMwMDM3NjAxMCIsICIzMzAwMzc3MDE4IiwgIjU0NjI0ODAxMSIsICIyNzQ4ODc4MDEwIiwgIjU0NjI0MDAxNiIsICIyNzMwNzU4MDEwIiwgIjgwNDY1NjAxNyIsICIyNjA3MzYyMDE4IiwgIjI2MTkyMjEwMTQiLCAiMjYxOTIxNDAxNCIsICIyNjEyNDk3MDE1IiwgIjI2MjA5NzcwMTIiLCAiMjY5MzE1OTAxNCJdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZWNnOiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAwMjcwNTEiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFsiNTAwNDQ4MDE5IiwgIjM1MDM1NzAxMiIsICI2MjIwNjIwMTkiLCAiMzc0MzYwMTQiLCAiMzc0MzcwMTciLCAiMjk5NzAzMDE3IiwgIjI0MTc5MjAxNSIsICIzOTU4NjAwMTciLCAiNTAwNDQ5MDEwIiwgIjI5OTcwMDAxOSIsICIzOTU4NjEwMTgiLCAiMjQxNzkxMDEwIiwgIjM3NDQzMDE1IiwgIjM3NDQwMDE3IiwgIjM3NDQxMDE4IiwgIjM3NDM4MDEwIiwgIjI0MTc5MDAxMSIsICI1MDA0NTAwMTAiLCAiMzk1ODYzMDE1IiwgIjE3ODQ4NzMwMTIiLCAiMzc0NDIwMTMiLCAiMzc0MzkwMTkiLCAiNTAwNDUyMDE5IiwgIjE3ODQ4NzIwMTkiLCAiMjc0NzExNzAxNCIsICI3NTE2ODkwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiwgKG1pKSJ9LCB7ImN1aSI6ICJDMDE1NTYyNiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogWyIyNDE3OTUwMTgiLCAiMzk1ODU4MDE5IiwgIjI5OTcwMjAxMCIsICI5NDg4NDAxNyIsICI5NDg4NTAxNiIsICIyOTk3MjEwMTkiLCAiMTIzMTY3ODAxMSIsICIyOTk2OTkwMTUiLCAiMzk1ODYyMDEzIiwgIjI0MTc5MzAxMyIsICIyNDE3OTQwMTkiLCAiMzk1ODU3MDEyIiwgIjI5OTcwNTAxMiIsICI3OTU2MzQwMTMiLCAiNTc4ODM4MDE4Il0sICJzdGFydCI6IDE4LCAidGVybSI6ICJhY3V0ZSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM1NDE5NTAiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiYWN1dGUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjI2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzYsICJzbm9tZWRfY3QiOiBbIjI0MTc5NTAxOCIsICIzOTU4NTgwMTkiLCAiMjk5NzAyMDEwIiwgIjk0ODg0MDE3IiwgIjk0ODg1MDE2IiwgIjI5OTcyMTAxOSIsICIxMjMxNjc4MDExIiwgIjI5OTY5OTAxNSIsICIzOTU4NjIwMTMiLCAiMjQxNzkzMDEzIiwgIjI0MTc5NDAxOSIsICIzOTU4NTcwMTIiLCAiMjk5NzA1MDEyIiwgIjc5NTYzNDAxMyIsICI1Nzg4MzgwMTgiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiBhY3V0ZSJ9LCB7ImN1aSI6ICJDMzgyOTkxMCIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJoYWQgYSBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzA3NDY3MjciLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43NiwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAic2VwdGFsIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMjM0ODM2MiIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwMzMiXSwgInNpbWlsYXJpdHkiOiAwLjc2LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJzZXB0YWwgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMwMTU1NjY4IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFsiMjQxNzk4MDE2IiwgIjI5OTc1MjAxOCIsICI0MDMxMDExIiwgIjUzNTYyMTAxMiIsICIyOTk3NTEwMTMiLCAiNDAzMjAxNiIsICIxMjIxNTY0MDEwIiwgIjI3NDA5OTQwMTciLCAiNzQ0ODY4MDEzIiwgIjU3ODg1NzAxMCIsICIyOTk3NTQwMTciLCAiMjk5NzUzMDExIiwgIjI3NDg4NTQwMTciXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogImhlYWxlZCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzAzNDAzMjQiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogWyIyOTk2OTgwMTEiLCAiMzUwMzc2MDE0IiwgIjM1MDM3NzAxNyIsICI2MjIwODMwMTMiXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInNpbGVudCBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDUgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU2IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzMwNzY5MjMwNzY5MjMwNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSAzIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMzg5ODY1NyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAwLjczMDc2OTIzMDc2OTIzMDcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgMiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTgiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMzIl0sICJzaW1pbGFyaXR5IjogMC43MzA3NjkyMzA3NjkyMzA3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMyODI1MTU5IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDIwMSJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAiZGF0ZSBvZiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4NDU1MDIiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24sIHN0cm9rZSJ9LCB7ImN1aSI6ICJDMzg5ODY1MyIsICJlbmQiOiAzOSwgIm5ncmFtIjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQwNDciXSwgInNpbWlsYXJpdHkiOiAwLjcwMzcwMzcwMzcwMzcwMzcsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogMTgsICJ0ZXJtIjogInR5cGUgNGMgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIn0sIHsiY3VpIjogIkMzODk4NjU0IiwgImVuZCI6IDM5LCAibmdyYW0iOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDA0NyJdLCAic2ltaWxhcml0eSI6IDAuNzAzNzAzNzAzNzAzNzAzNywgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiAxOCwgInRlcm0iOiAidHlwZSA0YiBteW9jYXJkaWFsIGluZmFyY3Rpb24ifSwgeyJjdWkiOiAiQzM4OTg2NTUiLCAiZW5kIjogMzksICJuZ3JhbSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDQ3Il0sICJzaW1pbGFyaXR5IjogMC43MDM3MDM3MDM3MDM3MDM3LCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDE4LCAidGVybSI6ICJ0eXBlIDRhIG15b2NhcmRpYWwgaW5mYXJjdGlvbiJ9LCB7ImN1aSI6ICJDMDI3ODMyOSIsICJlbmQiOiA2NiwgIm5ncmFtIjogInByZXNjcmliZWQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDU4Il0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDU2LCAidGVybSI6ICJwcmVzY3JpYmVkIn0sIHsiY3VpIjogIkMwMTI2MTc0IiwgImVuZCI6IDc1LCAibmdyYW0iOiAiTG9zYXJ0YW4iLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMTIxIiwgIlQxMDkiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbIjEyMTIwMzQwMTEiLCAiMTU5NDEzMDE1IiwgIjM0ODg5OTkwMTUiLCAiMzQ5OTg4NTAxMSIsICIxMjA1NDU0MDE3IiwgIjg0MDY0NTAxNCIsICIxMTk4ODY3MDEzIl0sICJzdGFydCI6IDY3LCAidGVybSI6ICJsb3NhcnRhbiJ9LCB7ImN1aSI6ICJDMTU1MDY1NSIsICJlbmQiOiAxMSwgIm5ncmFtIjogInBhdGllbnQiLCAicHJlZmVycmVkIjogMSwgInNlbXR5cGVzIjogWyJUMDMxIl0sICJzaW1pbGFyaXR5IjogMS4wLCAic25vbWVkX2N0IjogW10sICJzdGFydCI6IDQsICJ0ZXJtIjogInBhdGllbnQifSwgeyJjdWkiOiAiQzE1Nzg0ODUiLCAiZW5kIjogMTEsICJuZ3JhbSI6ICJwYXRpZW50IiwgInByZWZlcnJlZCI6IDEsICJzZW10eXBlcyI6IFsiVDE3MCJdLCAic2ltaWxhcml0eSI6IDEuMCwgInNub21lZF9jdCI6IFtdLCAic3RhcnQiOiA0LCAidGVybSI6ICJwYXRpZW50In0sIHsiY3VpIjogIkMxNTc4NDg2IiwgImVuZCI6IDExLCAibmdyYW0iOiAicGF0aWVudCIsICJwcmVmZXJyZWQiOiAxLCAic2VtdHlwZXMiOiBbIlQxNzAiXSwgInNpbWlsYXJpdHkiOiAxLjAsICJzbm9tZWRfY3QiOiBbXSwgInN0YXJ0IjogNCwgInRlcm0iOiAicGF0aWVudCJ9XQ=="
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
```

</details>
<BR/>

The extensions of interest within the insight extension are:

extension |  purpose
--------- |-------
insight-id | identifier for the insight.
path       | HL7 FHIR Path to the part of this resource that the insight applies to. In this case this will be the root of the derived object. 
insight-detail | Detailed supporting evidence for the insight.


#### Insight detail
The insight detail extension provides information about why the insight got created:

Extension | Purpose
--------- | -------
reference | The resource that contained the text that was used to create the insight
reference-path | HL7 FHIR Path that describes the location of the text used to create the insight (within reference)
evaluated-output | base64 response from the QuickUMLS Service
insight-result | value specific results for the insight. This structure contains one or more spans within the text at *reference-path* that support the insight.

##### Spans
The insight-result contains one or more span extensions. Each span contains

Extension | Purpose
-------|-----
covered text | text that the span covers
begin | offset in the original text that begins the span
end   | offset in the original text that ends the span
