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
from fhir.resources.immunization import Immunization
from text_analytics.insights.add_insights_immunization import update_immunization_with_insights
from text_analytics.utils.fhir_object_utils import create_transaction_bundle
from text_analytics.insights.text_adjustments import adjust_vaccine_text

#logger = caflogger.get_logger('whpa-cdp-text_analytics')


def enhance_immunization_payload_to_fhir(nlp, immunization_json):
    immunization_fhir = {}
    try:
        # Parse the immunization json
        immunization_fhir = Immunization.parse_obj(immunization_json)

        if immunization_fhir.vaccineCode.text is not None:
            text = adjust_vaccine_text(immunization_fhir.vaccineCode.text)
            #logger.info(logging_codes.WHPA_CDP_TEXT_ANALYTICS_CALLING_ACD_INFO, text)
            acd_resp = nlp.process(text)
            updated_immunization = update_immunization_with_insights(immunization_fhir, acd_resp)
    except acd.ACDException as ex:
        print("err")
        #logger.error(logging_codes.WHPA_CDP_TEXT_ANALYTICS_ACD_ERROR, ex.code, ex.message, ex.correlation_id)

    # create fhir bundle with transaction
    bundle = None
    if updated_immunization is not None:
        url_transaction = updated_immunization.resource_type + "/" + str(updated_immunization.id)
        bundle = create_transaction_bundle([[updated_immunization, 'PUT', url_transaction]])
    return bundle
