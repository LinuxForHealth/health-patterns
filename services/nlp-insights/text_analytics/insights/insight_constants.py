# Extension URL used in standard FHIR resource extension (extension directly under the resource type)
INSIGHT_REFERENCE_URL = "http://ibm.com/fhir/cdm/insight/reference"               # general extension for a resource
INSIGHT_CLASSIFICATION_URL = "http://ibm.com/fhir/cdm/insight/classification"     # indicates if derived
# also see PROCESS_*_URL

# Extension URLs used in meta extensions (extensions in the meta section of a FHIR resource)
# also see INSIGHT_PROCESS_NAME_URL, INSIGHT_CLASSIFICATION_URL
INSIGHT_RESULT_URL = "http://ibm.com/fhir/cdm/insight/result"                      # insight top level
INSIGHT_BASED_ON_URL = "http://ibm.com/fhir/cdm/insight/basedOn"                   # link to the unstructured report (FHIR DiagnosticReport)
INSIGHT_INSIGHT_ENTRY_URL = "http://ibm.com/fhir/cdm/insight/insight-entry"        # a derived insight (general, complex extension)
INSIGHT_INSIGHT_ID_URL = "http://ibm.com/fhir/cdm/insight/insight-id"              # ID of the insight entry
INSIGHT_EVIDENCE_DETAIL_URL = "http://ibm.com/fhir/cdm/insight/evidence-detail"    # full ACD output
INSIGHT_SPAN_URL = "http://ibm.com/fhir/cdm/insight/span"                          # span information (general, complex extension)
INSIGHT_SPAN_OFFSET_BEGIN_URL = "http://ibm.com/fhir/cdm/insight/offset-begin"     # beginning offset of NLP annotation
INSIGHT_SPAN_OFFSET_END_URL = "http://ibm.com/fhir/cdm/insight/offset-end"         # ending offset of NLP annotation
INSIGHT_SPAN_COVERED_TEXT_URL = "http://ibm.com/fhir/cdm/insight/covered-text"     # text covered by the NLP annotation
INSIGHT_CONFIDENCE_URL = "http://ibm.com/fhir/cdm/insight/confidence"              # confidence (general, complex extension)
INSIGHT_CONFIDENCE_SCORE_URL = "http://ibm.com/fhir/cdm/insight/confidence-score"  # confidence score for the insight
INSIGHT_CONFIDENCE_NAME_URL = "http://ibm.com/fhir/cdm/insight/confidence-name"    # name of the specific confidence score

# Extension URLs used within standard FHIR resource fields (extensions within a nested field of a FHIR resource)
# also see INSIGHT_REFERENCE_URL, INSIGHT_CLASSIFICATION_URL
INSIGHT_RESULT_ID_URL = "http://ibm.com/fhir/cdm/insight/result-insight-id"        # in a FHIR resource field, points to the insight in meta

# non-insight URLS
SNOMED_URL = "http://snomed.info/sct"
UMLS_URL = "http://terminology.hl7.org/CodeSystem/umls"
LOINC_URL = "http://loinc.org"
MESH_URL = "https://www.nlm.nih.gov/mesh/meshhome.html"
NCI_URL = "https://ncithesaurus.nci.nih.gov/ncitbrowser/"
ICD9_URL = "https://terminology.hl7.org/CodeSystem/icd9"
ICD10_URL = "https://terminology.hl7.org/CodeSystem/icd10"
RXNORM_URL = "http://www.nlm.nih.gov/research/umls/rxnorm"
TIMING_URL = "http://hl7.org/fhir/ValueSet/timing-abbreviation"


PROCESS_NAME_URL = "http://ibm.com/fhir/cdm/StructureDefinition/process-name"
PROCESS_TYPE_URL = "http://ibm.com/fhir/cdm/StructureDefinition/process-type"
PROCESS_VERSION_URL = "http://ibm.com/fhir/cdm/StructureDefinition/process-version"

# classification coding system values
CLASSIFICATION_DERIVED = "DERIVED"
CLASSIFICATION_MIXED = "MIXED"

PROCESS_NAME = "COM.IBM.WH.PA.CDP.CDE"
PROCESS_VERSION = "1.0"

ACD_PROCESS_TYPE_UNSTRUCTURED = "ACD Unstructured"
ACD_PROCESS_TYPE_STRUCTURED = "ACD Structured"
QUICKUMLS_PROCESS_TYPE_UNSTRUCTURED = "QuickUMLS Unstructured"
QUICKUMLS_PROCESS_TYPE_STRUCTURED = "QuickUMLS Structured"

INSIGHT_ID_UNSTRUCTURED_SYSTEM = "urn:id:COM.IBM.WH.PA.CDP.CDE.U"
INSIGHT_ID_STRUCTURED_SYSTEM = "urn:id:COM.IBM.WH.PA.CDP.CDE.S"

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
