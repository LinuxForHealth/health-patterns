import json
import logging
import requests

from text_analytics.abstract_nlp_service import NLPService
from text_analytics.enhance import *
from text_analytics.quickUMLS.config import get_config
from text_analytics.quickUMLS.semtype_lookup import lookup
from text_analytics.quickUMLS.semtype_lookup import get_semantic_type_list

logger = logging.getLogger()

class QuickUMLSService(NLPService):
    types_can_handle = {'AllergyIntolerance': enhance_allergy_intolerance_payload_to_fhir,
                        'Immunization': enhance_immunization_payload_to_fhir,
                        'DiagnosticReport': enhance_diagnostic_report_payload_to_fhir,
                        'DocumentReference': enhance_document_reference_payload_to_fhir
                        }

    PROCESS_TYPE_UNSTRUCTURED = "QuickUMLS Unstructured"
    PROCESS_TYPE_STRUCTURED = "QuickUMLS Structured"

    def __init__(self, jsonString):
        _config = get_config()
        self.quickUMLS_url = _config['QUICKUMLS_URL']
        self.jsonString = jsonString

    def process(self, text):
        if type(text) is bytes:
            request_body = {"text": text.decode('utf-8')}
        else:
            request_body = {"text": text}
        logger.info("Calling QUICKUMLS")
        resp = requests.post(self.quickUMLS_url, json=request_body)
        concepts = json.loads(resp.text)
        conceptsList = []
        if concepts is not None:
            for concept in concepts:
                conceptsList.append(self.concept_to_dict(concept))
        return {"concepts": conceptsList}

    @staticmethod
    def concept_to_dict(concept):
        output = {"Structure": "Concept"}
        output["generatingService"] = "quickUMLS"
        output["coveredText"] = concept["ngram"] if "ngram" in concept else None
        output["cui"] = concept["cui"] if "cui" in concept else None
        output["begin"] = concept["start"] if "start" in concept else None
        output["end"] = concept["end"] if "end" in concept else None
        output["preferredName"] = concept["term"] if "term" in concept else None
        output["type"] = get_semantic_type_list(concept["semtypes"]) if "semtypes" in concept and len(concept["semtypes"]) > 0 else None
        output["negated"] = False
        return output
