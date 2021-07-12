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
from fhir.resources.allergyintolerance import AllergyIntolerance
from text_analytics.call_acd_service import call_acd_with_text
from text_analytics import logging_codes
from text_analytics.insights.add_insights_allergy import update_allergy_with_insights
from text_analytics.utils.fhir_object_utils import create_transaction_bundle

#import caf_logger.logger as caflogger

#logger = caflogger.get_logger('whpa-cdp-text_analytics')


def enhance_allergy_intolerance_payload_to_fhir(input_json):
    try:
        # Parse the AllergyIntolerance json
        allergy_intolerance_fhir = AllergyIntolerance.parse_obj(input_json)

        # list of list(s) - where the sub list is the fhir field object to update followed by the acd response for that field
        # example: [[AllergyIntolerance.code, acd_resp1],[AllergyIntolerance.reaction[0].manifestation[0], acd_resp2],
        #  [AllergyIntolerance.reaction[0].manifestation[1], acd_resp3]]
        acd_results = []

        # AllergyIntolerance has multiple fields to NLP:
        #    AllergyIntolerance.code.text
        #    AllergyIntolerance.reaction[].manifestation[].text
        if allergy_intolerance_fhir.code.text is not None:
            # Process the allergen
            # AllergyIntolerance.code.text will have "Allergy to " appended to it to assist in getting correct codes
            text = 'Allergy to ' + allergy_intolerance_fhir.code.text
            #logger.info(logging_codes.WHPA_CDP_TEXT_ANALYTICS_CALLING_ACD_INFO, "AllergyIntolerance.code.text")
            acd_resp = call_acd_with_text(text)
            acd_results.append([allergy_intolerance_fhir.code, acd_resp])

        if allergy_intolerance_fhir.reaction is not None:
            for reaction in allergy_intolerance_fhir.reaction:
                for mf in reaction.manifestation:
                    # Process the manifestation
                    # Call ACD for each manifestation individually
                    acd_resp = call_acd_with_text(mf.text)
                    #logger.info(logging_codes.WHPA_CDP_TEXT_ANALYTICS_CALLING_ACD_INFO, "AllergyIntolerance.reaction["
                                #+ str(allergy_intolerance_fhir.reaction.index(reaction)) + "].manifestation["
                                #+ str(reaction.manifestation.index(mf)) + "].text")
                    acd_results.append([mf, acd_resp])

        # update fhir resource with insights
        result_allergy = update_allergy_with_insights(allergy_intolerance_fhir, acd_results)

    except acd.ACDException as ex:
        print("err")
        #logger.error(logging_codes.WHPA_CDP_TEXT_ANALYTICS_ACD_ERROR, ex.code, ex.message, ex.correlation_id)

    if result_allergy is not None:
        # create fhir bundle with transaction
        url_transaction = result_allergy.resource_type + "/" + str(result_allergy.id)
        bundle = create_transaction_bundle([[result_allergy, 'PUT', url_transaction]])
        return bundle
    else:
        return None
