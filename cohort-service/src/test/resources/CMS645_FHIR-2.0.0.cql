library "CMS645_FHIR" version '2.0.0'

using FHIR version '4.0.0'

include "FHIRHelpers" version '4.0.0' called FHIRHelpers 

codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "RXNORM": 'http://www.nlm.nih.gov/research/umls/rxnorm'
codesystem "CONDCLINSTATUS": 'http://terminology.hl7.org/CodeSystem/condition-clinical'

code "Condition Relapse code": 'relapse' from "CONDCLINSTATUS" display 'Relapse'
code "Condition Recurrence code": 'recurrence' from "CONDCLINSTATUS" display 'Recurrence'
code "Condition Active code": 'active' from "CONDCLINSTATUS" display 'Active'

concept "Condition Relapse": { "Condition Relapse code" } display 'Relapse'
concept "Condition Recurrence": { "Condition Recurrence code" } display 'Recurrence'
concept "Condition Active": { "Condition Active code" } display 'Active'

code "Malignant neoplasm of prostate (disorder)": '399068003' from "SNOMED"
code "DEXA Bone Density Scan": '241686001' from "SNOMED"
code "Lupron": '203852' from "RXNORM"

context Patient

define "Patient is Male": 
  Patient.gender.value = 'male'

define "Prostate Cancer Diagnosis":
  exists(ActiveOrRecurring([Condition: "Malignant neoplasm of prostate (disorder)"]))
 
define "First Androgen Deprivation Therapy":
  exists([MedicationRequest: "Lupron"])

define "Baseline DEXA Scan":
  exists([Procedure: "DEXA Bone Density Scan"])

define "Initial Population":
    "Patient is Male"
        and "Prostate Cancer Diagnosis"
        and "First Androgen Deprivation Therapy"

define "Denominator":
    "Initial Population"

define "Numerator":
    "Baseline DEXA Scan"

define function ActiveOrRecurring(CondList List<Condition>):
  CondList C
    where C.clinicalStatus ~ "Condition Active"
      or C.clinicalStatus ~ "Condition Recurrence"
      or C.clinicalStatus ~ "Condition Relapse"
      