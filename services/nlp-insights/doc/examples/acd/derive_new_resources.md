# OUTPUT OBSOLETE

# Derive New Resources with nlp-insights and ACD
Some resources such as DiagnosticReports and DocumentReferences contain clinical notes or other unstructured text. When the nlp-insights service receives one of these resources, it can derive new FHIR resources for detected concepts.

nlp-insights can derive new resources from:

* DiagnosticReport  (from the text at the path *DiagnosticReport.presentedForm[].data*)
* DocumentReference (from the text at the path *DocumentReference.content[].attachment.data*)

Two types of FHIR resources can be derived by the service:
* Condition
* MedicationStatement

## Configure nlp-insights to use ACD for NLP
If the nlp-insights service has not been configured to use ACD by default, follow the steps [here](./configure_acd.md).

## Derive new resources from a diagnostic report

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
                      "valueString": "DiagnosticReport.presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAicHJlZmVycmVkTmFtZSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn1dLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gQXR0cmlidXRlcyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiY29uY2VwdCI6IHsidWlkIjogOH0sICJuYW1lIjogIkRpYWdub3NpcyIsICJpY2Q5Q29kZSI6ICI0MTAuOTAiLCAiaWNkMTBDb2RlIjogIkkyMS45IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC45OTQsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDAzLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAwNH0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMDIxLCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMH19LCAiY2NzQ29kZSI6ICIxMDAiLCAiaGNjQ29kZSI6ICI4NiIsICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7ImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibG9zYXJ0YW4ifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA3fSwgIm5hbWUiOiAiUHJlc2NyaWJlZE1lZGljYXRpb24iLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19fV0sICJjb25jZXB0cyI6IFt7InR5cGUiOiAidW1scy5GaW5kaW5nIiwgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzQ1NTI5NTkiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24sIENUQ0FFIiwgInNlbWFudGljVHlwZSI6ICJmbmRnIiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzE0MzY5MSIsICJ2b2NhYnMiOiAiTVRILE5DSV9DVENBRV81LE5DSSJ9LCB7InR5cGUiOiAidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0IiwgInVpZCI6IDQsICJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwNDI4OTUzIiwgInByZWZlcnJlZE5hbWUiOiAiRWxlY3Ryb2NhcmRpb2dyYW06IG15b2NhcmRpYWwgaW5mYXJjdGlvbiAoZmluZGluZykiLCAic2VtYW50aWNUeXBlIjogImxidHIiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJJTlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjQsSTIxLjI5LEkyMS4wOSxJMjEuMTksUjk0LjMxLEkyNS4yLEkyMS45IiwgIm5jaUNvZGUiOiAiQzEwMTU4OSIsICJzbm9tZWRDb25jZXB0SWQiOiAiMTY0ODY1MDA1IiwgInZvY2FicyI6ICJDSFYsTVRILE5DSV9DRElTQyxOQ0ksU05PTUVEQ1RfVVMifSwgeyJ0eXBlIjogInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiLCAidWlkIjogMywgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzAwMjcwNTEiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24iLCAic2VtYW50aWNUeXBlIjogImRzeW4iLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAiaWNkMTBDb2RlIjogIkkyMS45IiwgIm5jaUNvZGUiOiAiQzI3OTk2IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJtZXNoSWQiOiAiTTAwMTQzNDAiLCAibG9pbmNJZCI6ICJNVEhVMDM1NTUxLExBMTQyNzQtNyxMUDk4ODg0LTcsTEExNjI4Ni05IiwgInZvY2FicyI6ICJOQ0lfTklDSEQsTVRILExOQyxDU1AsTVNILENTVCxIUE8sT01JTSxOQ0lfQ1RDQUUsQ09TVEFSLEFJUixDSFYsTkNJX0ZEQSxNRURMSU5FUExVUyxOQ0ksTENIX05XLEFPRCxTTk9NRURDVF9VUyxEWFAiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInRlbXBvcmFsIjogW3siYmVnaW4iOiA0MywgImVuZCI6IDQ3LCAiY292ZXJlZFRleHQiOiAiMjAxNSIsICJ0ZW1wb3JhbFR5cGUiOiB7ImRhdGVTY29yZSI6IDEuMCwgInJlbGF0aXZlU2NvcmUiOiAwLjB9LCAicmVsYXRpb25UeXBlcyI6IHsib3ZlcmxhcHNTY29yZSI6IDAuOTk4LCAiZHVyYXRpb25TY29yZSI6IDAuMH19XX0sIHsidHlwZSI6ICJ1bWxzLkhlYWx0aENhcmVBY3Rpdml0eSIsICJiZWdpbiI6IDU2LCAiZW5kIjogNjYsICJjb3ZlcmVkVGV4dCI6ICJwcmVzY3JpYmVkIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDI3ODMyOSIsICJwcmVmZXJyZWROYW1lIjogIlByZXNjcmliZWQiLCAic2VtYW50aWNUeXBlIjogImhsY2EiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAidm9jYWJzIjogIk1USCxDSFYsTENIIn0sIHsidHlwZSI6ICJ1bWxzLk9yZ2FuaWNDaGVtaWNhbCIsICJ1aWQiOiA1LCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic2VtYW50aWNUeXBlIjogIm9yY2giLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInZvY2FicyI6ICJNVEgsTE5DLENTUCxNU0gsTVRIU1BMLFJYTk9STSxOQ0lfTkNJLUdMT1NTLENIVixBVEMsTkNJX0NUUlAsTkNJX0ZEQSxOQ0ksQU9ELFNOT01FRENUX1VTLERSVUdCQU5LLFZBTkRGIn0sIHsidHlwZSI6ICJ1bWxzLlBoYXJtYWNvbG9naWNTdWJzdGFuY2UiLCAidWlkIjogMiwgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJwcmVmZXJyZWROYW1lIjogImxvc2FydGFuIiwgInNlbWFudGljVHlwZSI6ICJwaHN1IiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzY2ODY5IiwgInNub21lZENvbmNlcHRJZCI6ICI5NjMwOTAwMCwzNzM1NjcwMDIiLCAibWVzaElkIjogIk0wMDI5NDAwIiwgInJ4Tm9ybUlkIjogIjUyMTc1IiwgImxvaW5jSWQiOiAiTFAxNzE2MTktMiIsICJ2b2NhYnMiOiAiTVRILExOQyxDU1AsTVNILE1USFNQTCxSWE5PUk0sTkNJX05DSS1HTE9TUyxDSFYsQVRDLE5DSV9DVFJQLE5DSV9GREEsTkNJLEFPRCxTTk9NRURDVF9VUyxEUlVHQkFOSyxWQU5ERiIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJtZWRpY2F0aW9uIjogeyJ1c2FnZSI6IHsidGFrZW5TY29yZSI6IDEuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMCwgImxhYk1lYXN1cmVtZW50U2NvcmUiOiAwLjB9LCAiYWR2ZXJzZUV2ZW50IjogeyJzY29yZSI6IDAuMCwgImFsbGVyZ3lTY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJkb3NlQ2hhbmdlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdGFydGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0b3BwZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19fX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJwcmVmZXJyZWROYW1lIjogIk15b2NhcmRpYWwgSW5mYXJjdGlvbiIsICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBEZXJpdmVkIENvbmNlcHRzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibmNpQ29kZSI6ICJDMjc5OTYiLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgIm1lc2hJZCI6ICJNMDAxNDM0MCIsICJsb2luY0lkIjogIk1USFUwMzU1NTEsTEExNDI3NC03LExQOTg4ODQtNyxMQTE2Mjg2LTkiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInJ1bGVJZCI6ICI2OThmMmIxOS0yN2I2LTRkYWItOTE1MC03ZDdlZjNiMDNhNWMiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAzfV0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDQyODk1MyIsICJwcmVmZXJyZWROYW1lIjogIkVsZWN0cm9jYXJkaW9ncmFtOiBteW9jYXJkaWFsIGluZmFyY3Rpb24gKGZpbmRpbmcpIiwgInNvdXJjZSI6ICJDbGluaWNhbCBJbnNpZ2h0cyAtIERlcml2ZWQgQ29uY2VwdHMiLCAic291cmNlVmVyc2lvbiI6ICJ2MS4wIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiSU5WQUxJRCJ9LCAicnVsZUlkIjogImMxZThkN2Q0LTdkMzYtNDIzYi1iMzlkLTRlYmI1ZWI2NWIwYyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDR9XX0sIHsidHlwZSI6ICJJQ01lZGljYXRpb24iLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgImluc2lnaHRNb2RlbERhdGEiOiB7Im1lZGljYXRpb24iOiB7InVzYWdlIjogeyJ0YWtlblNjb3JlIjogMS4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wLCAibGFiTWVhc3VyZW1lbnRTY29yZSI6IDAuMH0sICJhZHZlcnNlRXZlbnQiOiB7InNjb3JlIjogMC4wLCAiYWxsZXJneVNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgImRvc2VDaGFuZ2VkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0YXJ0ZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RvcHBlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX19fSwgInJ1bGVJZCI6ICI3ODYxYzAyNC1hZDFjLTQ3ZTYtYjQwZS1jOTBjYjdiMTllMjYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInJ1bGVJZCI6ICJkMDA0ZGY2Mi1hNjVkLTQxMzYtYWEzMi0xNjFhNDNlYjk1MDYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAicnVsZUlkIjogIjM0M2U2MTU4LTJjMzAtNDcyNi1iZTcxLTMzYTU3MGIyODcwMyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDV9XX1dLCAiTWVkaWNhdGlvbkluZCI6IFt7InR5cGUiOiAiYWNpLk1lZGljYXRpb25JbmQiLCAidWlkIjogNywgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnIjogW3siY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAiY3VpIjogIkMwMTI2MTc0IiwgImNvbXBsZXgiOiAiZmFsc2UiLCAiZW5kIjogNzUsICJ0eXBlIjogImFjaS5JbmRfRHJ1ZyIsICJuYW1lMSI6IFt7InJ4Tm9ybUlEIjogIjUyMTc1IiwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnU3VyZmFjZUZvcm0iOiAiTG9zYXJ0YW4iLCAiZHJ1Z05vcm1hbGl6ZWROYW1lIjogImxvc2FydGFuIiwgImVuZCI6IDc1LCAidHlwZSI6ICJhY2kuRHJ1Z05hbWUiLCAiYmVnaW4iOiA2N31dLCAiYmVnaW4iOiA2N31dLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19LCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCIsICJjb21tZW50IjogIm1hcmtlZCBWQUxJRCBieSBjbGluaWNhbCBpbnNpZ2h0IG1vZGVscy4ifX1dLCAiU3ltcHRvbURpc2Vhc2VJbmQiOiBbeyJ0eXBlIjogImFjaS5TeW1wdG9tRGlzZWFzZUluZCIsICJ1aWQiOiA4LCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibW9kYWxpdHkiOiAicG9zaXRpdmUiLCAic3ltcHRvbURpc2Vhc2VTdXJmYWNlRm9ybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgImNjc0NvZGUiOiAiMTAwIiwgInN5bXB0b21EaXNlYXNlTm9ybWFsaXplZE5hbWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgImljZDlDb2RlIjogIjQxMC45MCIsICJoY2NDb2RlIjogIjg2IiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjk5NCwgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDMsICJkaXNjdXNzZWRTY29yZSI6IDAuMDA0fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wMjEsICJzeW1wdG9tU2NvcmUiOiAwLjAwMSwgInRyYXVtYVNjb3JlIjogMC4wLCAiZmFtaWx5SGlzdG9yeVNjb3JlIjogMC4wfX0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19XSwgInNwZWxsQ29ycmVjdGVkVGV4dCI6IFt7ImNvcnJlY3RlZFRleHQiOiAiVGhlIHBhdGllbnQgaGFkIGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIGluIDIwMTUgYW5kIHdhcyBwcmVzY3JpYmVkIExvc2FydGFuLlxuIn1dLCAidGVtcG9yYWxTcGFucyI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfX1dfQ=="
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
                      "valueString": "DiagnosticReport.presentedForm[0].data"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                      "valueAttachment": {
                        "contentType": "application/json",
                        "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAicHJlZmVycmVkTmFtZSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn1dLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gQXR0cmlidXRlcyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiY29uY2VwdCI6IHsidWlkIjogOH0sICJuYW1lIjogIkRpYWdub3NpcyIsICJpY2Q5Q29kZSI6ICI0MTAuOTAiLCAiaWNkMTBDb2RlIjogIkkyMS45IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC45OTQsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDAzLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAwNH0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMDIxLCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMH19LCAiY2NzQ29kZSI6ICIxMDAiLCAiaGNjQ29kZSI6ICI4NiIsICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7ImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibG9zYXJ0YW4ifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA3fSwgIm5hbWUiOiAiUHJlc2NyaWJlZE1lZGljYXRpb24iLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19fV0sICJjb25jZXB0cyI6IFt7InR5cGUiOiAidW1scy5GaW5kaW5nIiwgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzQ1NTI5NTkiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24sIENUQ0FFIiwgInNlbWFudGljVHlwZSI6ICJmbmRnIiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzE0MzY5MSIsICJ2b2NhYnMiOiAiTVRILE5DSV9DVENBRV81LE5DSSJ9LCB7InR5cGUiOiAidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0IiwgInVpZCI6IDQsICJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwNDI4OTUzIiwgInByZWZlcnJlZE5hbWUiOiAiRWxlY3Ryb2NhcmRpb2dyYW06IG15b2NhcmRpYWwgaW5mYXJjdGlvbiAoZmluZGluZykiLCAic2VtYW50aWNUeXBlIjogImxidHIiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJJTlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjQsSTIxLjI5LEkyMS4wOSxJMjEuMTksUjk0LjMxLEkyNS4yLEkyMS45IiwgIm5jaUNvZGUiOiAiQzEwMTU4OSIsICJzbm9tZWRDb25jZXB0SWQiOiAiMTY0ODY1MDA1IiwgInZvY2FicyI6ICJDSFYsTVRILE5DSV9DRElTQyxOQ0ksU05PTUVEQ1RfVVMifSwgeyJ0eXBlIjogInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiLCAidWlkIjogMywgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzAwMjcwNTEiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24iLCAic2VtYW50aWNUeXBlIjogImRzeW4iLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAiaWNkMTBDb2RlIjogIkkyMS45IiwgIm5jaUNvZGUiOiAiQzI3OTk2IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJtZXNoSWQiOiAiTTAwMTQzNDAiLCAibG9pbmNJZCI6ICJNVEhVMDM1NTUxLExBMTQyNzQtNyxMUDk4ODg0LTcsTEExNjI4Ni05IiwgInZvY2FicyI6ICJOQ0lfTklDSEQsTVRILExOQyxDU1AsTVNILENTVCxIUE8sT01JTSxOQ0lfQ1RDQUUsQ09TVEFSLEFJUixDSFYsTkNJX0ZEQSxNRURMSU5FUExVUyxOQ0ksTENIX05XLEFPRCxTTk9NRURDVF9VUyxEWFAiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInRlbXBvcmFsIjogW3siYmVnaW4iOiA0MywgImVuZCI6IDQ3LCAiY292ZXJlZFRleHQiOiAiMjAxNSIsICJ0ZW1wb3JhbFR5cGUiOiB7ImRhdGVTY29yZSI6IDEuMCwgInJlbGF0aXZlU2NvcmUiOiAwLjB9LCAicmVsYXRpb25UeXBlcyI6IHsib3ZlcmxhcHNTY29yZSI6IDAuOTk4LCAiZHVyYXRpb25TY29yZSI6IDAuMH19XX0sIHsidHlwZSI6ICJ1bWxzLkhlYWx0aENhcmVBY3Rpdml0eSIsICJiZWdpbiI6IDU2LCAiZW5kIjogNjYsICJjb3ZlcmVkVGV4dCI6ICJwcmVzY3JpYmVkIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDI3ODMyOSIsICJwcmVmZXJyZWROYW1lIjogIlByZXNjcmliZWQiLCAic2VtYW50aWNUeXBlIjogImhsY2EiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAidm9jYWJzIjogIk1USCxDSFYsTENIIn0sIHsidHlwZSI6ICJ1bWxzLk9yZ2FuaWNDaGVtaWNhbCIsICJ1aWQiOiA1LCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic2VtYW50aWNUeXBlIjogIm9yY2giLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInZvY2FicyI6ICJNVEgsTE5DLENTUCxNU0gsTVRIU1BMLFJYTk9STSxOQ0lfTkNJLUdMT1NTLENIVixBVEMsTkNJX0NUUlAsTkNJX0ZEQSxOQ0ksQU9ELFNOT01FRENUX1VTLERSVUdCQU5LLFZBTkRGIn0sIHsidHlwZSI6ICJ1bWxzLlBoYXJtYWNvbG9naWNTdWJzdGFuY2UiLCAidWlkIjogMiwgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJwcmVmZXJyZWROYW1lIjogImxvc2FydGFuIiwgInNlbWFudGljVHlwZSI6ICJwaHN1IiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzY2ODY5IiwgInNub21lZENvbmNlcHRJZCI6ICI5NjMwOTAwMCwzNzM1NjcwMDIiLCAibWVzaElkIjogIk0wMDI5NDAwIiwgInJ4Tm9ybUlkIjogIjUyMTc1IiwgImxvaW5jSWQiOiAiTFAxNzE2MTktMiIsICJ2b2NhYnMiOiAiTVRILExOQyxDU1AsTVNILE1USFNQTCxSWE5PUk0sTkNJX05DSS1HTE9TUyxDSFYsQVRDLE5DSV9DVFJQLE5DSV9GREEsTkNJLEFPRCxTTk9NRURDVF9VUyxEUlVHQkFOSyxWQU5ERiIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJtZWRpY2F0aW9uIjogeyJ1c2FnZSI6IHsidGFrZW5TY29yZSI6IDEuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMCwgImxhYk1lYXN1cmVtZW50U2NvcmUiOiAwLjB9LCAiYWR2ZXJzZUV2ZW50IjogeyJzY29yZSI6IDAuMCwgImFsbGVyZ3lTY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJkb3NlQ2hhbmdlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdGFydGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0b3BwZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19fX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJwcmVmZXJyZWROYW1lIjogIk15b2NhcmRpYWwgSW5mYXJjdGlvbiIsICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBEZXJpdmVkIENvbmNlcHRzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibmNpQ29kZSI6ICJDMjc5OTYiLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgIm1lc2hJZCI6ICJNMDAxNDM0MCIsICJsb2luY0lkIjogIk1USFUwMzU1NTEsTEExNDI3NC03LExQOTg4ODQtNyxMQTE2Mjg2LTkiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInJ1bGVJZCI6ICI2OThmMmIxOS0yN2I2LTRkYWItOTE1MC03ZDdlZjNiMDNhNWMiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAzfV0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDQyODk1MyIsICJwcmVmZXJyZWROYW1lIjogIkVsZWN0cm9jYXJkaW9ncmFtOiBteW9jYXJkaWFsIGluZmFyY3Rpb24gKGZpbmRpbmcpIiwgInNvdXJjZSI6ICJDbGluaWNhbCBJbnNpZ2h0cyAtIERlcml2ZWQgQ29uY2VwdHMiLCAic291cmNlVmVyc2lvbiI6ICJ2MS4wIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiSU5WQUxJRCJ9LCAicnVsZUlkIjogImMxZThkN2Q0LTdkMzYtNDIzYi1iMzlkLTRlYmI1ZWI2NWIwYyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDR9XX0sIHsidHlwZSI6ICJJQ01lZGljYXRpb24iLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgImluc2lnaHRNb2RlbERhdGEiOiB7Im1lZGljYXRpb24iOiB7InVzYWdlIjogeyJ0YWtlblNjb3JlIjogMS4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wLCAibGFiTWVhc3VyZW1lbnRTY29yZSI6IDAuMH0sICJhZHZlcnNlRXZlbnQiOiB7InNjb3JlIjogMC4wLCAiYWxsZXJneVNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgImRvc2VDaGFuZ2VkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0YXJ0ZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RvcHBlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX19fSwgInJ1bGVJZCI6ICI3ODYxYzAyNC1hZDFjLTQ3ZTYtYjQwZS1jOTBjYjdiMTllMjYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInJ1bGVJZCI6ICJkMDA0ZGY2Mi1hNjVkLTQxMzYtYWEzMi0xNjFhNDNlYjk1MDYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAicnVsZUlkIjogIjM0M2U2MTU4LTJjMzAtNDcyNi1iZTcxLTMzYTU3MGIyODcwMyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDV9XX1dLCAiTWVkaWNhdGlvbkluZCI6IFt7InR5cGUiOiAiYWNpLk1lZGljYXRpb25JbmQiLCAidWlkIjogNywgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnIjogW3siY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAiY3VpIjogIkMwMTI2MTc0IiwgImNvbXBsZXgiOiAiZmFsc2UiLCAiZW5kIjogNzUsICJ0eXBlIjogImFjaS5JbmRfRHJ1ZyIsICJuYW1lMSI6IFt7InJ4Tm9ybUlEIjogIjUyMTc1IiwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnU3VyZmFjZUZvcm0iOiAiTG9zYXJ0YW4iLCAiZHJ1Z05vcm1hbGl6ZWROYW1lIjogImxvc2FydGFuIiwgImVuZCI6IDc1LCAidHlwZSI6ICJhY2kuRHJ1Z05hbWUiLCAiYmVnaW4iOiA2N31dLCAiYmVnaW4iOiA2N31dLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19LCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCIsICJjb21tZW50IjogIm1hcmtlZCBWQUxJRCBieSBjbGluaWNhbCBpbnNpZ2h0IG1vZGVscy4ifX1dLCAiU3ltcHRvbURpc2Vhc2VJbmQiOiBbeyJ0eXBlIjogImFjaS5TeW1wdG9tRGlzZWFzZUluZCIsICJ1aWQiOiA4LCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibW9kYWxpdHkiOiAicG9zaXRpdmUiLCAic3ltcHRvbURpc2Vhc2VTdXJmYWNlRm9ybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgImNjc0NvZGUiOiAiMTAwIiwgInN5bXB0b21EaXNlYXNlTm9ybWFsaXplZE5hbWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgImljZDlDb2RlIjogIjQxMC45MCIsICJoY2NDb2RlIjogIjg2IiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjk5NCwgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDMsICJkaXNjdXNzZWRTY29yZSI6IDAuMDA0fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wMjEsICJzeW1wdG9tU2NvcmUiOiAwLjAwMSwgInRyYXVtYVNjb3JlIjogMC4wLCAiZmFtaWx5SGlzdG9yeVNjb3JlIjogMC4wfX0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19XSwgInNwZWxsQ29ycmVjdGVkVGV4dCI6IFt7ImNvcnJlY3RlZFRleHQiOiAiVGhlIHBhdGllbnQgaGFkIGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIGluIDIwMTUgYW5kIHdhcyBwcmVzY3JpYmVkIExvc2FydGFuLlxuIn1dLCAidGVtcG9yYWxTcGFucyI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfX1dfQ=="
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
</details>

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
MedicationStatement|Losartan


### Derived condition codes
Included in the condition are coding values for a number of industry standard systems that ACD understands.

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
http://terminology.hl7.org/CodeSystem/umls|C0027051|myocardial infarction
http://snomed.info/sct                    |22298006|
http://hl7.org/fhir/sid/icd-9-cm          |410.90  |
http://hl7.org/fhir/sid/icd-10-cm         |I21.9   |


### Derived MedicationStatement codes
ACD understands RxNorm, an industry standard coding system for medications. When ACD is configured as the NLP service for nlp-insights, RxNorm codes will added to derived MedicationStatements in addition to UMLS codes.

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

System                                     |Code    |Display
---                                        |---     |---
http://terminology.hl7.org/CodeSystem/umls |C0126174|Losartan
http://www.nlm.nih.gov/research/umls/rxnorm|52175   |

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
```

The insight id has a system and identifier that together identify the insight. In this example, the system tells us that the insight was discovered using ACD. The identifier value is unique (within the system) to this insight.

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
            "data": "eyJhdHRyaWJ1dGVWYWx1ZXMiOiBbeyJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAicHJlZmVycmVkTmFtZSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIn1dLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gQXR0cmlidXRlcyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiY29uY2VwdCI6IHsidWlkIjogOH0sICJuYW1lIjogIkRpYWdub3NpcyIsICJpY2Q5Q29kZSI6ICI0MTAuOTAiLCAiaWNkMTBDb2RlIjogIkkyMS45IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJkaWFnbm9zaXMiOiB7InVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC45OTQsICJwYXRpZW50UmVwb3J0ZWRTY29yZSI6IDAuMDAzLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAwNH0sICJzdXNwZWN0ZWRTY29yZSI6IDAuMDIxLCAic3ltcHRvbVNjb3JlIjogMC4wMDEsICJ0cmF1bWFTY29yZSI6IDAuMCwgImZhbWlseUhpc3RvcnlTY29yZSI6IDAuMH19LCAiY2NzQ29kZSI6ICIxMDAiLCAiaGNjQ29kZSI6ICI4NiIsICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7ImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAidmFsdWVzIjogW3sidmFsdWUiOiAibG9zYXJ0YW4ifV0sICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBBdHRyaWJ1dGVzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJjb25jZXB0IjogeyJ1aWQiOiA3fSwgIm5hbWUiOiAiUHJlc2NyaWJlZE1lZGljYXRpb24iLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19fV0sICJjb25jZXB0cyI6IFt7InR5cGUiOiAidW1scy5GaW5kaW5nIiwgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzQ1NTI5NTkiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24sIENUQ0FFIiwgInNlbWFudGljVHlwZSI6ICJmbmRnIiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzE0MzY5MSIsICJ2b2NhYnMiOiAiTVRILE5DSV9DVENBRV81LE5DSSJ9LCB7InR5cGUiOiAidW1scy5MYWJvcmF0b3J5T3JUZXN0UmVzdWx0IiwgInVpZCI6IDQsICJiZWdpbiI6IDE4LCAiZW5kIjogMzksICJjb3ZlcmVkVGV4dCI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwNDI4OTUzIiwgInByZWZlcnJlZE5hbWUiOiAiRWxlY3Ryb2NhcmRpb2dyYW06IG15b2NhcmRpYWwgaW5mYXJjdGlvbiAoZmluZGluZykiLCAic2VtYW50aWNUeXBlIjogImxidHIiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJJTlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjQsSTIxLjI5LEkyMS4wOSxJMjEuMTksUjk0LjMxLEkyNS4yLEkyMS45IiwgIm5jaUNvZGUiOiAiQzEwMTU4OSIsICJzbm9tZWRDb25jZXB0SWQiOiAiMTY0ODY1MDA1IiwgInZvY2FicyI6ICJDSFYsTVRILE5DSV9DRElTQyxOQ0ksU05PTUVEQ1RfVVMifSwgeyJ0eXBlIjogInVtbHMuRGlzZWFzZU9yU3luZHJvbWUiLCAidWlkIjogMywgImJlZ2luIjogMTgsICJlbmQiOiAzOSwgImNvdmVyZWRUZXh0IjogIm15b2NhcmRpYWwgaW5mYXJjdGlvbiIsICJuZWdhdGVkIjogZmFsc2UsICJjdWkiOiAiQzAwMjcwNTEiLCAicHJlZmVycmVkTmFtZSI6ICJNeW9jYXJkaWFsIEluZmFyY3Rpb24iLCAic2VtYW50aWNUeXBlIjogImRzeW4iLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAiaWNkMTBDb2RlIjogIkkyMS45IiwgIm5jaUNvZGUiOiAiQzI3OTk2IiwgInNub21lZENvbmNlcHRJZCI6ICIyMjI5ODAwNiIsICJtZXNoSWQiOiAiTTAwMTQzNDAiLCAibG9pbmNJZCI6ICJNVEhVMDM1NTUxLExBMTQyNzQtNyxMUDk4ODg0LTcsTEExNjI4Ni05IiwgInZvY2FicyI6ICJOQ0lfTklDSEQsTVRILExOQyxDU1AsTVNILENTVCxIUE8sT01JTSxOQ0lfQ1RDQUUsQ09TVEFSLEFJUixDSFYsTkNJX0ZEQSxNRURMSU5FUExVUyxOQ0ksTENIX05XLEFPRCxTTk9NRURDVF9VUyxEWFAiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInRlbXBvcmFsIjogW3siYmVnaW4iOiA0MywgImVuZCI6IDQ3LCAiY292ZXJlZFRleHQiOiAiMjAxNSIsICJ0ZW1wb3JhbFR5cGUiOiB7ImRhdGVTY29yZSI6IDEuMCwgInJlbGF0aXZlU2NvcmUiOiAwLjB9LCAicmVsYXRpb25UeXBlcyI6IHsib3ZlcmxhcHNTY29yZSI6IDAuOTk4LCAiZHVyYXRpb25TY29yZSI6IDAuMH19XX0sIHsidHlwZSI6ICJ1bWxzLkhlYWx0aENhcmVBY3Rpdml0eSIsICJiZWdpbiI6IDU2LCAiZW5kIjogNjYsICJjb3ZlcmVkVGV4dCI6ICJwcmVzY3JpYmVkIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDI3ODMyOSIsICJwcmVmZXJyZWROYW1lIjogIlByZXNjcmliZWQiLCAic2VtYW50aWNUeXBlIjogImhsY2EiLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAidm9jYWJzIjogIk1USCxDSFYsTENIIn0sIHsidHlwZSI6ICJ1bWxzLk9yZ2FuaWNDaGVtaWNhbCIsICJ1aWQiOiA1LCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic2VtYW50aWNUeXBlIjogIm9yY2giLCAic291cmNlIjogInVtbHMiLCAic291cmNlVmVyc2lvbiI6ICIyMDIwQUEiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInZvY2FicyI6ICJNVEgsTE5DLENTUCxNU0gsTVRIU1BMLFJYTk9STSxOQ0lfTkNJLUdMT1NTLENIVixBVEMsTkNJX0NUUlAsTkNJX0ZEQSxOQ0ksQU9ELFNOT01FRENUX1VTLERSVUdCQU5LLFZBTkRGIn0sIHsidHlwZSI6ICJ1bWxzLlBoYXJtYWNvbG9naWNTdWJzdGFuY2UiLCAidWlkIjogMiwgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJwcmVmZXJyZWROYW1lIjogImxvc2FydGFuIiwgInNlbWFudGljVHlwZSI6ICJwaHN1IiwgInNvdXJjZSI6ICJ1bWxzIiwgInNvdXJjZVZlcnNpb24iOiAiMjAyMEFBIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiTk9fREVDSVNJT04ifSwgIm5jaUNvZGUiOiAiQzY2ODY5IiwgInNub21lZENvbmNlcHRJZCI6ICI5NjMwOTAwMCwzNzM1NjcwMDIiLCAibWVzaElkIjogIk0wMDI5NDAwIiwgInJ4Tm9ybUlkIjogIjUyMTc1IiwgImxvaW5jSWQiOiAiTFAxNzE2MTktMiIsICJ2b2NhYnMiOiAiTVRILExOQyxDU1AsTVNILE1USFNQTCxSWE5PUk0sTkNJX05DSS1HTE9TUyxDSFYsQVRDLE5DSV9DVFJQLE5DSV9GREEsTkNJLEFPRCxTTk9NRURDVF9VUyxEUlVHQkFOSyxWQU5ERiIsICJpbnNpZ2h0TW9kZWxEYXRhIjogeyJtZWRpY2F0aW9uIjogeyJ1c2FnZSI6IHsidGFrZW5TY29yZSI6IDEuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMCwgImxhYk1lYXN1cmVtZW50U2NvcmUiOiAwLjB9LCAiYWR2ZXJzZUV2ZW50IjogeyJzY29yZSI6IDAuMCwgImFsbGVyZ3lTY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJkb3NlQ2hhbmdlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdGFydGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0b3BwZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19fX19LCB7InR5cGUiOiAiSUNEaWFnbm9zaXMiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJwcmVmZXJyZWROYW1lIjogIk15b2NhcmRpYWwgSW5mYXJjdGlvbiIsICJzb3VyY2UiOiAiQ2xpbmljYWwgSW5zaWdodHMgLSBEZXJpdmVkIENvbmNlcHRzIiwgInNvdXJjZVZlcnNpb24iOiAidjEuMCIsICJkaXNhbWJpZ3VhdGlvbkRhdGEiOiB7InZhbGlkaXR5IjogIlZBTElEIn0sICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibmNpQ29kZSI6ICJDMjc5OTYiLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgIm1lc2hJZCI6ICJNMDAxNDM0MCIsICJsb2luY0lkIjogIk1USFUwMzU1NTEsTEExNDI3NC03LExQOTg4ODQtNyxMQTE2Mjg2LTkiLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsiZGlhZ25vc2lzIjogeyJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuOTk0LCAicGF0aWVudFJlcG9ydGVkU2NvcmUiOiAwLjAwMywgImRpc2N1c3NlZFNjb3JlIjogMC4wMDR9LCAic3VzcGVjdGVkU2NvcmUiOiAwLjAyMSwgInN5bXB0b21TY29yZSI6IDAuMDAxLCAidHJhdW1hU2NvcmUiOiAwLjAsICJmYW1pbHlIaXN0b3J5U2NvcmUiOiAwLjB9fSwgInJ1bGVJZCI6ICI2OThmMmIxOS0yN2I2LTRkYWItOTE1MC03ZDdlZjNiMDNhNWMiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAzfV0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDQyODk1MyIsICJwcmVmZXJyZWROYW1lIjogIkVsZWN0cm9jYXJkaW9ncmFtOiBteW9jYXJkaWFsIGluZmFyY3Rpb24gKGZpbmRpbmcpIiwgInNvdXJjZSI6ICJDbGluaWNhbCBJbnNpZ2h0cyAtIERlcml2ZWQgQ29uY2VwdHMiLCAic291cmNlVmVyc2lvbiI6ICJ2MS4wIiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiSU5WQUxJRCJ9LCAicnVsZUlkIjogImMxZThkN2Q0LTdkMzYtNDIzYi1iMzlkLTRlYmI1ZWI2NWIwYyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDR9XX0sIHsidHlwZSI6ICJJQ01lZGljYXRpb24iLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgImluc2lnaHRNb2RlbERhdGEiOiB7Im1lZGljYXRpb24iOiB7InVzYWdlIjogeyJ0YWtlblNjb3JlIjogMS4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wLCAibGFiTWVhc3VyZW1lbnRTY29yZSI6IDAuMH0sICJhZHZlcnNlRXZlbnQiOiB7InNjb3JlIjogMC4wLCAiYWxsZXJneVNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgImRvc2VDaGFuZ2VkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fSwgInN0YXJ0ZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RvcHBlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX19fSwgInJ1bGVJZCI6ICI3ODYxYzAyNC1hZDFjLTQ3ZTYtYjQwZS1jOTBjYjdiMTllMjYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAibmNpQ29kZSI6ICJDNjY4NjkiLCAic25vbWVkQ29uY2VwdElkIjogIjk2MzA5MDAwLDM3MzU2NzAwMiIsICJtZXNoSWQiOiAiTTAwMjk0MDAiLCAicnhOb3JtSWQiOiAiNTIxNzUiLCAibG9pbmNJZCI6ICJMUDE3MTYxOS0yIiwgInJ1bGVJZCI6ICJkMDA0ZGY2Mi1hNjVkLTQxMzYtYWEzMi0xNjFhNDNlYjk1MDYiLCAiZGVyaXZlZEZyb20iOiBbeyJ1aWQiOiAyfV19LCB7InR5cGUiOiAiSUNOb3JtYWxpdHkiLCAiYmVnaW4iOiA2NywgImVuZCI6IDc1LCAiY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAibmVnYXRlZCI6IGZhbHNlLCAiY3VpIjogIkMwMTI2MTc0IiwgInByZWZlcnJlZE5hbWUiOiAibG9zYXJ0YW4iLCAic291cmNlIjogIkNsaW5pY2FsIEluc2lnaHRzIC0gRGVyaXZlZCBDb25jZXB0cyIsICJzb3VyY2VWZXJzaW9uIjogInYxLjAiLCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJOT19ERUNJU0lPTiJ9LCAicnVsZUlkIjogIjM0M2U2MTU4LTJjMzAtNDcyNi1iZTcxLTMzYTU3MGIyODcwMyIsICJkZXJpdmVkRnJvbSI6IFt7InVpZCI6IDV9XX1dLCAiTWVkaWNhdGlvbkluZCI6IFt7InR5cGUiOiAiYWNpLk1lZGljYXRpb25JbmQiLCAidWlkIjogNywgImJlZ2luIjogNjcsICJlbmQiOiA3NSwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnIjogW3siY292ZXJlZFRleHQiOiAiTG9zYXJ0YW4iLCAiY3VpIjogIkMwMTI2MTc0IiwgImNvbXBsZXgiOiAiZmFsc2UiLCAiZW5kIjogNzUsICJ0eXBlIjogImFjaS5JbmRfRHJ1ZyIsICJuYW1lMSI6IFt7InJ4Tm9ybUlEIjogIjUyMTc1IiwgImNvdmVyZWRUZXh0IjogIkxvc2FydGFuIiwgImN1aSI6ICJDMDEyNjE3NCIsICJkcnVnU3VyZmFjZUZvcm0iOiAiTG9zYXJ0YW4iLCAiZHJ1Z05vcm1hbGl6ZWROYW1lIjogImxvc2FydGFuIiwgImVuZCI6IDc1LCAidHlwZSI6ICJhY2kuRHJ1Z05hbWUiLCAiYmVnaW4iOiA2N31dLCAiYmVnaW4iOiA2N31dLCAiaW5zaWdodE1vZGVsRGF0YSI6IHsibWVkaWNhdGlvbiI6IHsidXNhZ2UiOiB7InRha2VuU2NvcmUiOiAxLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjAsICJsYWJNZWFzdXJlbWVudFNjb3JlIjogMC4wfSwgImFkdmVyc2VFdmVudCI6IHsic2NvcmUiOiAwLjAsICJhbGxlcmd5U2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAiZG9zZUNoYW5nZWRFdmVudCI6IHsic2NvcmUiOiAwLjAsICJ1c2FnZSI6IHsiZXhwbGljaXRTY29yZSI6IDAuMCwgImNvbnNpZGVyaW5nU2NvcmUiOiAwLjAsICJkaXNjdXNzZWRTY29yZSI6IDAuMH19LCAic3RhcnRlZEV2ZW50IjogeyJzY29yZSI6IDAuMCwgInVzYWdlIjogeyJleHBsaWNpdFNjb3JlIjogMC4wLCAiY29uc2lkZXJpbmdTY29yZSI6IDAuMCwgImRpc2N1c3NlZFNjb3JlIjogMC4wfX0sICJzdG9wcGVkRXZlbnQiOiB7InNjb3JlIjogMC4wLCAidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjAsICJjb25zaWRlcmluZ1Njb3JlIjogMC4wLCAiZGlzY3Vzc2VkU2NvcmUiOiAwLjB9fX19LCAiZGlzYW1iaWd1YXRpb25EYXRhIjogeyJ2YWxpZGl0eSI6ICJWQUxJRCIsICJjb21tZW50IjogIm1hcmtlZCBWQUxJRCBieSBjbGluaWNhbCBpbnNpZ2h0IG1vZGVscy4ifX1dLCAiU3ltcHRvbURpc2Vhc2VJbmQiOiBbeyJ0eXBlIjogImFjaS5TeW1wdG9tRGlzZWFzZUluZCIsICJ1aWQiOiA4LCAiYmVnaW4iOiAxOCwgImVuZCI6IDM5LCAiY292ZXJlZFRleHQiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImN1aSI6ICJDMDAyNzA1MSIsICJpY2QxMENvZGUiOiAiSTIxLjkiLCAibW9kYWxpdHkiOiAicG9zaXRpdmUiLCAic3ltcHRvbURpc2Vhc2VTdXJmYWNlRm9ybSI6ICJteW9jYXJkaWFsIGluZmFyY3Rpb24iLCAic25vbWVkQ29uY2VwdElkIjogIjIyMjk4MDA2IiwgImNjc0NvZGUiOiAiMTAwIiwgInN5bXB0b21EaXNlYXNlTm9ybWFsaXplZE5hbWUiOiAibXlvY2FyZGlhbCBpbmZhcmN0aW9uIiwgImljZDlDb2RlIjogIjQxMC45MCIsICJoY2NDb2RlIjogIjg2IiwgImRpc2FtYmlndWF0aW9uRGF0YSI6IHsidmFsaWRpdHkiOiAiVkFMSUQifSwgImluc2lnaHRNb2RlbERhdGEiOiB7ImRpYWdub3NpcyI6IHsidXNhZ2UiOiB7ImV4cGxpY2l0U2NvcmUiOiAwLjk5NCwgInBhdGllbnRSZXBvcnRlZFNjb3JlIjogMC4wMDMsICJkaXNjdXNzZWRTY29yZSI6IDAuMDA0fSwgInN1c3BlY3RlZFNjb3JlIjogMC4wMjEsICJzeW1wdG9tU2NvcmUiOiAwLjAwMSwgInRyYXVtYVNjb3JlIjogMC4wLCAiZmFtaWx5SGlzdG9yeVNjb3JlIjogMC4wfX0sICJ0ZW1wb3JhbCI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfSwgInJlbGF0aW9uVHlwZXMiOiB7Im92ZXJsYXBzU2NvcmUiOiAwLjk5OCwgImR1cmF0aW9uU2NvcmUiOiAwLjB9fV19XSwgInNwZWxsQ29ycmVjdGVkVGV4dCI6IFt7ImNvcnJlY3RlZFRleHQiOiAiVGhlIHBhdGllbnQgaGFkIGEgbXlvY2FyZGlhbCBpbmZhcmN0aW9uIGluIDIwMTUgYW5kIHdhcyBwcmVzY3JpYmVkIExvc2FydGFuLlxuIn1dLCAidGVtcG9yYWxTcGFucyI6IFt7ImJlZ2luIjogNDMsICJlbmQiOiA0NywgImNvdmVyZWRUZXh0IjogIjIwMTUiLCAidGVtcG9yYWxUeXBlIjogeyJkYXRlU2NvcmUiOiAxLjAsICJyZWxhdGl2ZVNjb3JlIjogMC4wfX1dfQ=="
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
evaluated-output | base64 response from the ACD Service
insight-result | value specific results for the insight. This structure contains one or more spans within the text at *reference-path* that support the insight.

##### Spans
The insight-result contains one or more span extensions. Each span contains

Extension | Purpose
-------|-----
covered text | text that the span covers
begin | offset in the original text that begins the span
end   | offset in the original text that ends the span
confidence | repeatable extension with a confidence score

##### Confidence scores
ACD confidence scores are directional; they are indicators of confidence of "context", rather than simple concept detection correctness. A Span may have more than a single direction of confidence associated with it.

<!-- 
command to build the table

cat /tmp/output | jq -r '
.entry[].resource | select(.resourceType == "Condition") | 
.meta.extension[0].extension[] | 
select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail") | 
.extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-result") | 
.extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/span") | 
.extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence") 
-->

<details><summary>Confidence extension for a condition</summary>

```json
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
}
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

```

</details>

###### Condition confidence score
The span in the derived condition has two confidence scores

<!-- cat /tmp/output | jq -r '["Description", "Score"], ["---", "---"], (.entry[].resource | select(.resourceType == "Condition") | .meta.extension[0].extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail") | .extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-result") | .extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/span") | .extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence") | .extension | [ (.[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/description").valueString), (.[] | select(.url=="http://ibm.com/fhir/cdm/StructureDefinition/score").valueDecimal) ]) | @tsv'| column -t -o "|" -s$'\t'` -->

Description           |Score
---                   |---
Explicit Score        |0.994
Patient Reported Score|0.003


This tells us that ACD (strongly) believed the span indicated an explicit mention of the condition. It also tells us that ACD did not believe that this condition is something that the patient said they had.

###### Medication confidence score
The span in the derived medication resource has a different score than the condition.

<!-- 
code to generate the table

cat /tmp/output | jq -r '
["Description", "Score"], 
["---", "---"], 
(.entry[].resource | select(.resourceType == "MedicationStatement") | 
 .meta.extension[0].extension[] | 
 select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail") | 
 .extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-result") | 
 .extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/span") | 
 .extension[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence") | 
 .extension | 
 [ 
  (.[] | select(.url == "http://ibm.com/fhir/cdm/StructureDefinition/description").valueString), 
  (.[] | select(.url=="http://ibm.com/fhir/cdm/StructureDefinition/score").valueDecimal) 
 ]
) 
| @tsv'| column -t -o "|" -s$'\t' 


-->

Description           |Score
---                   |---
Medication Taken Score|1

This score tells us that ACD strongly believes that the text says that the patient took the medication.




