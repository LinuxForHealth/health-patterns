import logging

from fhir.resources.documentreference import DocumentReference
from text_analytics.insights.add_insights_condition import create_conditions_from_insights
from text_analytics.insights.add_insights_medication import create_med_statements_from_insights
from text_analytics.utils import fhir_object_utils

logger = logging.getLogger()

def enhance_document_reference_payload_to_fhir(nlp, document_reference_json):
    """
    Given an NLP service and document_reference (as json object), returns a json string for
    a FHIR bundle resource with additional insights.

    """
    bundle_entries = []

    document_reference_fhir = DocumentReference.parse_obj(document_reference_json)
    text = fhir_object_utils.get_document_reference_data(document_reference_fhir)
    if text:
        nlp_resp = nlp.process(text)
        create_conditions_fhir = create_conditions_from_insights(nlp, document_reference_fhir, nlp_resp)
        create_med_statements_fhir = create_med_statements_from_insights(nlp, document_reference_fhir, nlp_resp)

        if create_conditions_fhir:
            for condition in create_conditions_fhir:
                bundle_entry = [condition, 'POST', condition.resource_type]
                bundle_entries.append(bundle_entry)

        if create_med_statements_fhir:
            for med_statement in create_med_statements_fhir:
                bundle_entry = [med_statement, 'POST', med_statement.resource_type]
                bundle_entries.append(bundle_entry)

    bundle = fhir_object_utils.create_transaction_bundle(bundle_entries)

    return bundle.json()
