from fhir.resources.allergyintolerance import AllergyIntolerance
from text_analytics.insights.add_insights_allergy import update_allergy_with_insights
import logging

logger = logging.getLogger()

def enhance_allergy_intolerance_payload_to_fhir(nlp, input_json):
    try:
        # Parse the AllergyIntolerance json
        allergy_intolerance_fhir = AllergyIntolerance.parse_obj(input_json)

        # list of list(s) - where the sub list is the fhir field object to update followed by the acd response for that field
        # example: [[AllergyIntolerance.code, acd_resp1],[AllergyIntolerance.reaction[0].manifestation[0], acd_resp2],
        #  [AllergyIntolerance.reaction[0].manifestation[1], acd_resp3]]
        nlp_results = []

        # AllergyIntolerance has multiple fields to NLP:
        #    AllergyIntolerance.code.text
        #    AllergyIntolerance.reaction[].manifestation[].text
        if allergy_intolerance_fhir.code.text is not None:
            # Process the allergen
            # AllergyIntolerance.code.text will have "Allergy to " appended to it to assist in getting correct codes
            text = 'Allergy to ' + allergy_intolerance_fhir.code.text
            nlp_resp = nlp.process(text)
            nlp_results.append([allergy_intolerance_fhir.code, nlp_resp])

        if allergy_intolerance_fhir.reaction is not None:
            for reaction in allergy_intolerance_fhir.reaction:
                for mf in reaction.manifestation:
                    # Process the manifestation
                    # Call ACD for each manifestation individually
                    nlp_resp = nlp.process(mf.text)
                    nlp_results.append([mf, nlp_resp])

        # update fhir resource with insights
        result_allergy = update_allergy_with_insights(nlp, allergy_intolerance_fhir, nlp_results)

    except Exception as ex:
        logger.exception("Error enhancing allergy intolerance FHIR")

    if result_allergy is not None:
        # create fhir bundle with transaction
        # url_transaction = result_allergy.resource_type + "/" + str(result_allergy.id)
        # bundle = create_transaction_bundle([[result_allergy, 'PUT', url_transaction]])
        # return bundle
        return result_allergy.json()
    else:
        return None
