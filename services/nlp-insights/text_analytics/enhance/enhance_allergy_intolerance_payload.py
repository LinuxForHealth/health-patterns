import logging
from fhir.resources.allergyintolerance import AllergyIntolerance
from text_analytics.insights.add_insights_allergy import update_allergy_with_insights
from text_analytics.insights.text_adjustments import adjust_allergy_text

logger = logging.getLogger()

def enhance_allergy_intolerance_payload_to_fhir(nlp, input_json):
    """
    Given an NLP service and allergy intolerance (as json object), returns a json string for
    a FHIR bundle resource with additional insights.

    If no insights are found, a json string for the original fhir resource is returned..
    """

    allergy_intolerance_fhir = AllergyIntolerance.parse_obj(input_json)
    nlp_results = []

    if allergy_intolerance_fhir.code and allergy_intolerance_fhir.code.text:
        text = adjust_allergy_text(allergy_intolerance_fhir.code.text)
        nlp_resp = nlp.process(text)
        nlp_results.append([allergy_intolerance_fhir.code, nlp_resp])

    if allergy_intolerance_fhir.reaction:
        for reaction in allergy_intolerance_fhir.reaction:
            for mf in reaction.manifestation:
                nlp_resp = nlp.process(mf.text)
                nlp_results.append([mf, nlp_resp])

    if nlp_results:
        result_allergy = update_allergy_with_insights(nlp, allergy_intolerance_fhir, nlp_results)

    return result_allergy.json() if result_allergy else allergy_intolerance_fhir.json()
