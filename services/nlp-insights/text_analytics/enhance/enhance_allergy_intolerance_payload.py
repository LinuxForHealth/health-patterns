from fhir.resources.allergyintolerance import AllergyIntolerance

from text_analytics.insights.text_adjustments import adjust_allergy_text
from text_analytics.insights.add_insights_allergy import update_allergy_with_insights
import logging

logger = logging.getLogger()

def enhance_allergy_intolerance_payload_to_fhir(nlp, input_json):
    try:
        allergy_intolerance_fhir = AllergyIntolerance.parse_obj(input_json)

        nlp_results = []

        if allergy_intolerance_fhir.code.text is not None:
            text = adjust_allergy_text(allergy_intolerance_fhir.code.text)
            nlp_resp = nlp.process(text)
            nlp_results.append([allergy_intolerance_fhir.code, nlp_resp])

        if allergy_intolerance_fhir.reaction is not None:
            for reaction in allergy_intolerance_fhir.reaction:
                for mf in reaction.manifestation:
                    nlp_resp = nlp.process(mf.text)
                    nlp_results.append([mf, nlp_resp])

        result_allergy = update_allergy_with_insights(nlp, allergy_intolerance_fhir, nlp_results)

    except Exception as ex:
        logger.exception("Error enhancing allergy intolerance FHIR", ex)

    if result_allergy is not None:
        return result_allergy.json()
    else:
        return None
