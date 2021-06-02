library "MaleorFemalePatients" version '1.0.0'
using FHIR version '4.0.0'
include "FHIRHelpers" version '4.0.0' called "FHIRHelpers" 
context Patient

define "Male Patient": 
  Patient.gender.value = 'male'

define "Female Patient": 
  Patient.gender.value = 'female'

define "MeetsInclusionCriteria":
  "Male Patient"
  or "Female Patient"

define "InPopulation":
   "MeetsInclusionCriteria" 



