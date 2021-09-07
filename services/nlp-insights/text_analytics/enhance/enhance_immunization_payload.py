import logging

from fhir.resources.immunization import Immunization
from text_analytics.insights.add_insights_immunization import update_immunization_with_insights
from text_analytics.insights.text_adjustments import adjust_vaccine_text

logger = logging.getLogger()

def enhance_immunization_payload_to_fhir(nlp, immunization_json):
    """
    Given an NLP service and immunization (as json object), returns a json string for
    a FHIR bundle resource with additional insights.

    If no insights are found, a json string for the original fhir resource is returned..
    """
    immunization_fhir = {}

    immunization_fhir = Immunization.parse_obj(immunization_json)
    updated_immunization = None
    if immunization_fhir.vaccineCode.text:
        text = adjust_vaccine_text(immunization_fhir.vaccineCode.text)
        nlp_resp = nlp.process(text)
        updated_immunization = update_immunization_with_insights(nlp, immunization_fhir, nlp_resp)

    return updated_immunization.json() if updated_immunization else immunization_fhir.json()
