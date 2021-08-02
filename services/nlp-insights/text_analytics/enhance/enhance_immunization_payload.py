from fhir.resources.immunization import Immunization
from text_analytics.insights.add_insights_immunization import update_immunization_with_insights
from text_analytics.insights.text_adjustments import adjust_vaccine_text
import logging

logger = logging.getLogger()


def enhance_immunization_payload_to_fhir(nlp, immunization_json):
    immunization_fhir = {}
    try:
        # Parse the immunization json
        immunization_fhir = Immunization.parse_obj(immunization_json)

        if immunization_fhir.vaccineCode.text is not None:
            text = adjust_vaccine_text(immunization_fhir.vaccineCode.text)
            nlp_resp = nlp.process(text)
            updated_immunization = update_immunization_with_insights(nlp, immunization_fhir, nlp_resp)
    except Exception as ex:
        logger.exception("Error enhancing immunization FHIR")

    # create fhir bundle with transaction
    bundle = None
    if updated_immunization is not None:
        # url_transaction = updated_immunization.resource_type + "/" + str(updated_immunization.id)
        # bundle = create_transaction_bundle([[updated_immunization, 'PUT', url_transaction]])
        return updated_immunization.json()
    else:
        return None
    # return bundle
