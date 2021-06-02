library "FemalePatients" version '1.0.0'
using FHIR version '4.0.0'
include "FHIRHelpers" version '4.0.0' called "FHIRHelpers" 
context Patient

define "Female patients": 
  Patient.gender.value = 'female'

define "MeetsInclusionCriteria":
  "Female patients"

define "InPopulation":
   "MeetsInclusionCriteria" 



