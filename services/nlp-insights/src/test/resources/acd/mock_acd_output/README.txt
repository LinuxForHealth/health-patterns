When copying ACD output from the cartridge preview output, you need to remove a couple layers.
1) Remove these lines from the top (leave the first line with the opening brace, remove the next 4 lines).
  Note the "text" value will change from this example:
    "unstructured": [
      {
         "text": "zzzzz",
        "data": {
2) remove from the end (leave the last line and remove the previous 3):
         }
       }
     ]

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
For diagnostic reports, we have a single generic FHIR input since we always mock the ACD response.
This is the text to use for these reports

-- Condition_Nothing_Useful.json --
Patient came in looking for a friend, he said he was lonely.

Text does not pick up any insights.
base64 encoded text: UGF0aWVudCBjYW1lIGluIGxvb2tpbmcgZm9yIGEgZnJpZW5kLCBoZSBzYWlkIGhlIHdhcyBsb25lbHku

-- Condition.json --
Patient has type 1 diabetes

This text picks up a single Condition with a single annotation.
base64 encoded text: UGF0aWVudCBoYXMgdHlwZSAxIGRpYWJldGVz

-- Condition_Multiple.json --
Patient has type 1 diabetes and hypertension, and is reporting shortness of breath.

This text picks up multiple (3) different conditions, a single annotations each.
base64 encoded text: UGF0aWVudCBoYXMgdHlwZSAxIGRpYWJldGVzIGFuZCBoeXBlcnRlbnNpb24sIGFuZCBpcyByZXBvcnRpbmcgc2hvcnRuZXNzIG9mIGJyZWF0aC4=

-- Condition_MultipleAnnotations.json --
Patient with diabetes is here for bi-annual checkup.  Diagnosis of diabetes is now 10 years past.  She is doing well with diet and exercise, and labs show diabetes remains stable, kidney function is normal.

This text picks up a single condition, but has several (3) annotations for that same condition.
base64 encoded text: UGF0aWVudCB3aXRoIGRpYWJldGVzIGlzIGhlcmUgZm9yIGJpLWFubnVhbCBjaGVja3VwLiBEaWFnbm9zaXMgb2YgZGlhYmV0ZXMgaXMgbm93IDEwIHllYXJzIHBhc3QuIFNoZSBpcyBkb2luZyB3ZWxsIHdpdGggZGlldCBhbmQgZXhlcmNpc2UsIGFuZCBsYWJzIHNob3cgZGlhYmV0ZXMgcmVtYWlucyBzdGFibGUsIGtpZG5leSBmdW5jdGlvbiBpcyBub3JtYWwu

-- Condition_Multiple_and_MultipleAnnotations.json --
Checkup for patient with type 1 diabetes, hypertension, and coronary artery disease.
Type 1 diabetes dianogsed at 8 years of age.  Hypertension treatment began 5 years ago at age 55.  Coronary artery disease under watch since 2017.
Type 1 diabetes remains under control and patient is compliant with monitoring and treatment.
Hypertension remains elevated and we will try increasing the medication dose.  Follow-up after 1 month to check if hypertension is improved.

This text picks up multiple different conditions, and has several annotations for each condition.
base64 encoded text: Q2hlY2t1cCBmb3IgcGF0aWVudCB3aXRoIHR5cGUgMSBkaWFiZXRlcywgaHlwZXJ0ZW5zaW9uLCBhbmQgY29yb25hcnkgYXJ0ZXJ5IGRpc2Vhc2UuClR5cGUgMSBkaWFiZXRlcyBkaWFub2dzZWQgYXQgOCB5ZWFycyBvZiBhZ2UuIEh5cGVydGVuc2lvbiB0cmVhdG1lbnQgYmVnYW4gNSB5ZWFycyBhZ28gYXQgYWdlIDU1LiBDb3JvbmFyeSBhcnRlcnkgZGlzZWFzZSB1bmRlciB3YXRjaCBzaW5jZSAyMDE3LgpUeXBlIDEgZGlhYmV0ZXMgcmVtYWlucyB1bmRlciBjb250cm9sIGFuZCBwYXRpZW50IGlzIGNvbXBsaWFudCB3aXRoIG1vbml0b3JpbmcgYW5kIHRyZWF0bWVudC4KSHlwZXJ0ZW5zaW9uIHJlbWFpbnMgZWxldmF0ZWQgYW5kIHdlIHdpbGwgdHJ5IGluY3JlYXNpbmcgdGhlIG1lZGljYXRpb24gZG9zZS4gRm9sbG93LXVwIGFmdGVyIDEgbW9udGggdG8gY2hlY2sgaWYgaHlwZXJ0ZW5zaW9uIGlzIGltcHJvdmVkLg==

-- medication_metformin.json --
[PERSONALNAME] Hospital Emergency Room~MEDICATIONS:  Metformin 1,000 mg Q AM.~

base64 encoded text: W1BFUlNPTkFMTkFNRV0gSG9zcGl0YWwgRW1lcmdlbmN5IFJvb21+TUVESUNBVElPTlM6ICBNZXRmb3JtaW4gMSwwMDAgbWcgUSBBTS5+

-- medication_no_dosage.json --
The patient's chest pain improved after the sublingual nitroglycerine

-- medication_metformin_multiple.json --
MEDICATIONS:  Metformin 1,000 mg Q AM~Metformin 500 mg PM~Treated with Metformin.~

This text finds a single medication, but has several (3) annotations for that same medication.
base64 encoded text: TUVESUNBVElPTlM6ICBNZXRmb3JtaW4gMSwwMDAgbWcgUSBBTX5NZXRmb3JtaW4gNTAwIG1nIFBNflRyZWF0ZWQgd2l0aCBNZXRmb3JtaW4ufg==


-- medication_multiple.json --
[PERSONALNAME] Hospital Emergency Room~MEDICATIONS:  Metformin 1,000 mg and Lisinopril 10 mg Q AM.~

base64 encoded text: W1BFUlNPTkFMTkFNRV0gSG9zcGl0YWwgRW1lcmdlbmN5IFJvb21+TUVESUNBVElPTlM6ICBNZXRmb3JtaW4gMSwwMDAgbWcgYW5kIExpc2lub3ByaWwgMTAgbWcgUSBBTS5+

-- Multiple_Mixed.json --
Patient has diabetes and is taking Metformin.
Patient has hypertension and is taking lisinopril.

Text picks up 2 Conditions and 2 Medications.
base64 encoded text: UGF0aWVudCBoYXMgZGlhYmV0ZXMgYW5kIGlzIHRha2luZyBNZXRmb3JtaW4uClBhdGllbnQgaGFzIGh5cGVydGVuc2lvbiBhbmQgaXMgdGFraW5nIGxpc2lub3ByaWwu