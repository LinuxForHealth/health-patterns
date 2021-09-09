# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines onstants for use when creating insights.
   These are intended to be useful regardless of the NLP solution generating
    the insight.
"""
# Extension URL used in standard FHIR resource extension (extension directly under the resource type)
INSIGHT_REFERENCE_URL = (
    "http://ibm.com/fhir/cdm/insight/reference"  # general extension for a resource
)
INSIGHT_CLASSIFICATION_URL = (
    "http://ibm.com/fhir/cdm/insight/classification"  # indicates if derived
)
# also see PROCESS_*_URL

# Extension URLs used in meta extensions (extensions in the meta section of a FHIR resource)
# also see INSIGHT_PROCESS_NAME_URL, INSIGHT_CLASSIFICATION_URL
INSIGHT_RESULT_URL = (
    "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"  # insight result
)
INSIGHT_SPAN_URL = "http://ibm.com/fhir/cdm/StructureDefinition/span"  # span information (general, complex extension)
INSIGHT_SPAN_OFFSET_BEGIN_URL = "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin"  # beginning offset of NLP annotation
INSIGHT_SPAN_OFFSET_END_URL = "http://ibm.com/fhir/cdm/StructureDefinition/offset-end"  # ending offset of NLP annotation
INSIGHT_SPAN_COVERED_TEXT_URL = "http://ibm.com/fhir/cdm/StructureDefinition/covered-text"  # text covered by the NLP annotation
INSIGHT_CONFIDENCE_URL = "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"  # confidence (general, complex extension)
INSIGHT_CONFIDENCE_SCORE_URL = "http://ibm.com/fhir/cdm/StructureDefinition/score"  # confidence score for the insight
INSIGHT_CONFIDENCE_NAME_URL = "http://ibm.com/fhir/cdm/StructureDefinition/description"  # name of the specific confidence score


# Extension URLs used within standard FHIR resource fields (extensions within a nested field of a FHIR resource)
# also see INSIGHT_REFERENCE_URL, INSIGHT_CLASSIFICATION_URL
INSIGHT_RESULT_ID_URL = "http://ibm.com/fhir/cdm/insight/result-insight-id"  # in a FHIR resource field, points to the insight in meta


# Extension URL used in standard FHIR resource extension (extension directly under the resource type)
# INSIGHT_REFERENCE_URL = "http://ibm.com/fhir/cdm/insight/reference"               # general extension for a resource
INSIGHT_CATEGORY_URL = "http://ibm.com/fhir/cdm/StructureDefinition/category"  # indicates how derivation was done, eg from NLP


# Extension URLs used in meta extensions (extensions in the meta section of a FHIR resource)
# also see INSIGHT_CATEGORY_URL
INSIGHT_URL = "http://ibm.com/fhir/cdm/StructureDefinition/insight"  # insight top level for confidences and spans (unstructured only)
INSIGHT_BASED_ON_URL = "http://ibm.com/fhir/cdm/StructureDefinition/reference"  # link to the unstructured report (FHIR DiagnosticReport)
INSIGHT_DETAIL_URL = "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"  # a derived insight (general, complex extension)
INSIGHT_ID_URL = (
    "http://ibm.com/fhir/cdm/StructureDefinition/insight-id"  # ID of the insight entry
)
INSIGHT_NLP_OUTPUT_URL = (
    "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output"  # full ACD output
)
INSIGHT_REFERENCE_PATH_URL = "http://ibm.com/fhir/cdm/StructureDefinition/reference-path"  # path in resource insight was used for

# non-insight URLS
SNOMED_URL = "http://snomed.info/sct"
UMLS_URL = "http://terminology.hl7.org/CodeSystem/umls"
LOINC_URL = "http://loinc.org"
MESH_URL = "http://www.nlm.nih.gov/mesh/meshhome.html"
NCI_URL = "http://ncithesaurus.nci.nih.gov/ncitbrowser/"
ICD9_URL = "http://terminology.hl7.org/CodeSystem/icd9"
ICD10_URL = "https://terminology.hl7.org/CodeSystem/icd10"
RXNORM_URL = "http://www.nlm.nih.gov/research/umls/rxnorm"
TIMING_URL = "http://hl7.org/fhir/ValueSet/timing-abbreviation"


# category coding system values
CLASSIFICATION_DERIVED_CODE = "natural-language-processing"
CLASSIFICATION_DERIVED_DISPLAY = "NLP"
CLASSIFICATION_DERIVED_SYSTEM = (
    "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
)


INSIGHT_CLASSIFICATION_SYSTEM = "cdm/insight/classification"

CONFIDENCE_SCORE_EXPLICIT = "Explicit Score"
CONFIDENCE_SCORE_PATIENT_REPORTED = "Patient Reported Score"
CONFIDENCE_SCORE_DISCUSSED = "Discussed Score"
CONFIDENCE_SCORE_SUSPECTED = "Suspected Score"
CONFIDENCE_SCORE_FAMILY_HISTORY = "Family History Score"

CONFIDENCE_SCORE_MEDICATION_TAKEN = "Medication Taken Score"
CONFIDENCE_SCORE_MEDICATION_CONSIDERING = "Medication Considering Score"
CONFIDENCE_SCORE_MEDICATION_DISCUSSED = "Medication Discussed Score"
CONFIDENCE_SCORE_MEDICATION_MEASUREMENT = "Medication Lab Measurement Score"
