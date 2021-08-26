import logging

from fhir.resources.diagnosticreport import DiagnosticReport
from text_analytics.insights.add_insights_condition import create_conditions_from_insights
from text_analytics.insights.add_insights_medication import create_med_statements_from_insights
from text_analytics.utils import fhir_object_utils


logger = logging.getLogger()

def enhance_diagnostic_report_payload_to_fhir(nlp, diagnostic_report_json):
    """
    Given an NLP service and diagnostic_report (as json object), returns a json string for
    a FHIR bundle resource with additional insights.
    
    If no insights are found, a json string for the original fhir resource is returned..
    """
    # Parse the diagnostic report json
    diagnostic_report_fhir = DiagnosticReport.parse_obj(diagnostic_report_json)
    text = fhir_object_utils.get_diagnostic_report_data(diagnostic_report_fhir)
    if text:
        nlp_resp = nlp.process(text)
        create_conditions_fhir = create_conditions_from_insights(nlp, diagnostic_report_fhir, nlp_resp)
        create_med_statements_fhir = create_med_statements_from_insights(nlp, diagnostic_report_fhir, nlp_resp)
    
        # create fhir bundle with transaction
        bundle_entries = []
    
        # Only create and send back a bundle if there were conditions found.
        if create_conditions_fhir:
            for condition in create_conditions_fhir:
                bundle_entry = []
                bundle_entry.append(condition)
                bundle_entry.append('POST')
                bundle_entry.append(condition.resource_type)
                bundle_entries.append(bundle_entry)
        if create_med_statements_fhir:
            for med_statement in create_med_statements_fhir:
                bundle_entry = []
                bundle_entry.append(med_statement)
                bundle_entry.append('POST')
                bundle_entry.append(med_statement.resource_type)
                bundle_entries.append(bundle_entry)
    
        if bundle_entries:
            bundle = fhir_object_utils.create_transaction_bundle(bundle_entries)
            return bundle.json()
    
    return diagnostic_report_fhir.json()
