# *******************************************************************************
# IBM Confidential                                                            *
#                                                                             *
# OCO Source Materials                                                        *
#                                                                             *
# (C) Copyright IBM Corp. 2021                                                *
#                                                                             *
# The source code for this program is not published or otherwise              *
# divested of its trade secrets, irrespective of what has been                *
# deposited with the U.S. Copyright Office.                                   *
# ******************************************************************************/

from ibm_whcs_sdk import annotator_for_clinical_data as acd
from fhir.resources.diagnosticreport import DiagnosticReport
from text_analytics.insights.add_insights_condition import create_conditions_from_insights
from text_analytics.insights.add_insights_medication import create_med_statements_from_insights
from text_analytics.utils import fhir_object_utils

#logger = caflogger.get_logger('whpa-cdp-text_analytics')


def enhance_diagnostic_report_payload_to_fhir(nlp, diagnostic_report_json):
    try:
        # Parse the diagnostic report json
        diagnostic_report_fhir = DiagnosticReport.parse_obj(diagnostic_report_json)

        text = fhir_object_utils.get_diagnostic_report_data(diagnostic_report_fhir)
        #acd_resp = call_service_then_enhance(nlp, text)
        acd_resp = nlp.process(text)
        create_conditions_fhir = create_conditions_from_insights(diagnostic_report_fhir, acd_resp)
        create_med_statements_fhir = create_med_statements_from_insights(diagnostic_report_fhir, acd_resp)
    except acd.ACDException as ex:
        #logger.error(logging_codes.WHPA_CDP_TEXT_ANALYTICS_ACD_ERROR, ex.code, ex.message, ex.correlation_id)
        return None
    except Exception as e:
        #logger.error(logging_codes.WHPA_CDP_TEXT_ANALYTICS_COULD_NOT_FIND_DATA, str(diagnostic_report_json), exc_info=e)
        return None

    # create fhir bundle with transaction
    bundle_entries = []

    # Only create and send back a bundle if there were conditions found.
    if create_conditions_fhir is not None:
        for condition in create_conditions_fhir:
            bundle_entry = []
            bundle_entry.append(condition)
            bundle_entry.append('POST')
            bundle_entry.append(condition.resource_type)
            bundle_entries.append(bundle_entry)
    if create_med_statements_fhir is not None:
        for med_statement in create_med_statements_fhir:
            bundle_entry = []
            bundle_entry.append(med_statement)
            bundle_entry.append('POST')
            bundle_entry.append(med_statement.resource_type)
            bundle_entries.append(bundle_entry)
    if create_conditions_fhir is None and create_med_statements_fhir is None:
        # If no conditions or medications were found, return None
        bundle = None

    if len(bundle_entries) > 0:
        bundle = fhir_object_utils.create_transaction_bundle(bundle_entries)

    return bundle
