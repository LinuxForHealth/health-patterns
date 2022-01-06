# Enrich FHIR resources with nlp-insights and QuickUMLS
--------------------------------------
The nlp-insights service supports enrichment of the following types of FHIR resources:

* Condition
* AllergyIntolerance

A resource is enriched by adding UMLS codes for detected concepts.

This tutorial provides examples of enrichment.

## Configure nlp-insights to use QuickUMLS for NLP
If the nlp-insights service has not been configured to use QuickUMLS by default, follow the steps [here](./configure_quickumls.md).

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
A bundle with the enriched condition is returned from the service.

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

The entry for the condition in the returned bundle has a method of *PUT*, which indicates that this resource has been enriched with an additional code.

### Condition derived codes
Quick UMLS understands UMLS concept codes. As a result a code has been added to the resource.

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


## Enrich an allergy intolerance
In this example, a bundle with two allergy intolreance resources is sent to the nlp insights server. The first has a code with text "peanut", and the second resource has a code with text "amoxicillin".

Both resources contain only text and do not contain any codes for the allergy. The nlp-insights service will enrich the resources with a UMLS code for the provided text.

As in the prior example, the returned bundle is saved in a file /tmp/output for later analysis.

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

### Enriched Allergy Intolerance resources
A bundle is returned that contains the enriched allergy intolerance resources. Both entries in the bundle have method *PUT*, indicating that these contain enriched resources. Each resource now contains the additional derived code values.

`cat /tmp/output | jq`

<details><summary>Returned Bundle</summary>

```json
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

### Allergy Intolerance derived codes
The food allergy resource has been enriched with a new code.

<!--
code to generate the table

cat /tmp/output | jq -r '["System", "Code", "Display"], ["---", "---", "---"], (.entry[].resource | select(.id == "wxyz-123") | .code.coding[] | [.system,  .code, .display]) | @tsv' | column -t -s $'\t' -o "|"
-->

System                                    |Code    |Display
---                                       |---     |---
http://terminology.hl7.org/CodeSystem/umls|C0559470|peanut allergy



In a similar way, the medication allergy resource has been enriched with a new code.

<!--
code to generate table

cat /tmp/output | jq -r '["System", "Code", "Display"], ["---", "---", "---"], (.entry[].resource | select(.id == "qrstuv-123") | .code.coding[] | [.system,  .code, .display]) | @tsv' | column -t -s $'\t' -o "|"

-->

System                                    |Code    |Display
---                                       |---     |---
http://terminology.hl7.org/CodeSystem/umls|C0571417|amoxicillin allergy

## Evidence
nlp-insights enriches resources according to the [Alvearie FHIR IG](https://alvearie.io/alvearie-fhir-ig/index.html).

The nlp-insights service adds detailed information to the enriched resource to explain what caused the additional codes to be added.

### Insight Summary
Each coding that has been derived by NLP contains an insight summary extension that can be examined to determine which insight derived the code.

For example consider the UMLS code C0559470 that was added to the allergy intolerance resource wxyz-123.

```
cat /tmp/output | jq -r '
.entry[].resource | 
select(.id == "wxyz-123") |
.code.coding[] | 
select(.code == "C0559470" and .system == "http://terminology.hl7.org/CodeSystem/umls")'
```

<details><summary>C0559470 coding in AllergyIntolerance wxyz-123</summary>

```json
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
```

</details><BR/>

The summary extension has been added to the coding. The summary has an insight id and category.
The insight id has a system and identifier that together identify the insight. In this example, the system tells us that the insight was discovered using QuickUMLS. The identifier value is unique (within the system) to this insight, and may be used to find the insight extension for the insight in the resource meta.

When nlp-insights derives codes, it will create one insight for all derived codes that are created from the same text. It is common for all summary extensions to refer to the same insight id.

The category tells us that the coding was derived using Natural Language Processing.

### Insight Extension in Resource Meta
The insight identified by the summary extension has an insight extension in the resource's meta. The insight extension contains lots of details about what the insight applies to and why it was created. 


<!-- 
 jq code to extract the extension
 
cat /tmp/output | jq -r ' .entry[].resource | select(.id == "wxyz-123").meta.extension[0]'

-->

<details><summary>Insight extension in the meta for AllergyIntolerance wxyz-123</summary>

```json
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


