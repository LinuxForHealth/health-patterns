# OUTPUT OBSOLETE

# Context awareness with ACD

A significant advantage of configuring nlp insights with ACD is that in addition to simple concept detection, the context of the concept is considered.

This allows nlp-insights to avoid creating resources for concepts that do not apply to the patient.

Some example phrases with concepts that will not result in derived resources.

* The patient does not have a myocardial infarction
* The patient's mother had a myocardial infarction last year
* The patient is concerned that he may have had a myocardial infarction

The nlp-insights service takes advantage of ACD attributes for improved handling of these scenarios.

# Example
This example creates a diagnostic report where the text mentions a myocardial infarction that is not for the patient.

## Configure nlp-insights to use ACD for NLP
If the nlp-insights service has not been configured to use ACD by default, follow the steps [here](./configure_acd.md).

## Send the example diagnostic report to the nlp-insights service
The Text data in a diagnostic report must be base64 encoded, which can be done with the base64 command in bash.

```
B64_REPORT_TEXT=$(echo "The patient's mother had a myocardial infarction last year." | base64 -w 0)
```

The text can now be included in a diagnostic report and sent to the nlp-insights service.

```
curl -XPOST localhost:5000/discoverInsights  -H 'Content-Type: application/json; charset=utf-8' --data-binary @- << EOF
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

## Inspect the response bundle
Although the input text mentions a condition, a resource is not created because the condition is not for the patient.

```json
{
  "entry": [],
  "type": "transaction",
  "resourceType": "Bundle"
}
```
