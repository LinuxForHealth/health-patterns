import logging

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.dosage import Dosage, DosageDoseAndRate
from fhir.resources.extension import Extension
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.quantity import Quantity
from fhir.resources.timing import Timing
from text_analytics.insights import insight_constants
from text_analytics.utils import fhir_object_utils

logger = logging.getLogger()

def _create_med_statement_from_template():

    med_statement_template = {
        "status": "unknown",
        "medicationCodeableConcept": {

            "text": "template"
        }
    }
    med_statement = MedicationStatement.construct(**med_statement_template)
    return med_statement


def _build_resource(nlp, diagnostic_report, nlp_output):
    concepts = nlp_output.get('concepts')
    med_statements_found = {}            # key is UMLS ID, value is the FHIR resource
    med_statements_insight_counter = {}  # key is UMLS ID, value is the current insight_num

    if hasattr(nlp, 'add_medications'):
        med_statements_found, med_statements_insight_counter = nlp.add_medications(nlp, diagnostic_report, nlp_output, med_statements_found, med_statements_insight_counter)

    for concept in concepts:
        the_type = concept['type']
        if isinstance(the_type, str):
            the_type = [the_type]
        if len(set(the_type) & set(['umls.Antibiotic', 'umls.ClinicalDrug', 'umls.PharmacologicSubstance', 'umls.OrganicChemical'])) > 0:
            med_statements_found, med_statements_insight_counter = create_insight(concept, nlp, nlp_output, diagnostic_report, _build_resource_data, med_statements_found, med_statements_insight_counter)

    if len(med_statements_found) == 0:
        return None
    return list(med_statements_found.values())

def create_insight(concept, nlp, nlp_output, diagnostic_report, build_resource, med_statements_found, med_statements_insight_counter):
    cui = concept.get('cui')
    med_statement = med_statements_found.get(cui)
    if med_statement is None:
        med_statement = _create_med_statement_from_template()
        med_statement.meta = fhir_object_utils.add_resource_meta_unstructured(nlp, diagnostic_report)
        med_statements_found[cui] = med_statement
        insight_num = 1
    else:
        insight_num = med_statements_insight_counter[cui] + 1
    med_statements_insight_counter[cui] = insight_num
    insight_id = "insight-" + str(insight_num)
    build_resource(med_statement, concept, insight_id)
    insight = Extension.construct()
    insight.url = insight_constants.INSIGHT_INSIGHT_ENTRY_URL
    insight_id_ext = fhir_object_utils.create_insight_extension(insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)
    insight.extension = [insight_id_ext]
    insight_detail = fhir_object_utils.create_insight_detail_extension(nlp_output)
    insight.extension.append(insight_detail)
    insight_span = fhir_object_utils.create_insight_span_extension(concept)
    insight.extension.append(insight_span)
    insight_model_data = concept.get('insightModelData')
    if insight_model_data is not None:
        fhir_object_utils.add_medication_confidences(insight.extension, insight_model_data)
    result_extension = med_statement.meta.extension[0]
    result_extension.extension.append(insight)
    return med_statements_found, med_statements_insight_counter

def _build_resource_data(med_statement, concept, insight_id):
    if med_statement.status is None:
        med_statement.status = 'unknown'

    drug = concept.get('preferredName')

    if type(med_statement.medicationCodeableConcept) is dict and med_statement.medicationCodeableConcept.get("text") == "template":
        codeable_concept = CodeableConcept.construct()
        codeable_concept.text = drug
        med_statement.medicationCodeableConcept = codeable_concept
        codeable_concept.coding = []

    fhir_object_utils.add_codings_drug(concept, drug, med_statement.medicationCodeableConcept, insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)

def create_med_statements_from_insights(nlp, diagnostic_report, nlp_output):
    med_statements = _build_resource(nlp, diagnostic_report, nlp_output)
    if med_statements is not None:
        for med_statement in med_statements:
            med_statement.subject = diagnostic_report.subject
            fhir_object_utils.create_derived_resource_extension(med_statement)
    return med_statements
