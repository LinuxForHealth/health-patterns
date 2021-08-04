from text_analytics.abstract_nlp_service import NLPService
from text_analytics.quickUMLS.config import get_config
from text_analytics.quickUMLS.semtype_lookup import lookup
from text_analytics.enhance import *
import json
import requests
import logging

logger = logging.getLogger()


class QuickUMLSService(NLPService):
    types_can_handle = {'AllergyIntolerance': enhance_allergy_intolerance_payload_to_fhir,
                        'Immunization': enhance_immunization_payload_to_fhir,
                        'DiagnosticReport': enhance_diagnostic_report_payload_to_fhir}

    PROCESS_TYPE_UNSTRUCTURED = "QuickUMLS Unstructured"
    PROCESS_TYPE_STRUCTURED = "QuickUMLS Structured"
    
    def __init__(self, json_string):
        _config = get_config()
        self.quickUMLS_url = _config['QUICKUMLS_URL']

    def process(self, text):
        try:
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
        except requests.exceptions as ex:
            logger.error("Error calling QuickUMLS on: " + text + ", with error " + ex.message)
            return None

    def parse_config(self, jsonString):
        configJson = json.loads(jsonString)
        self.resourceTypes = configJson["resourceTypes"]
        self.resourcePaths = configJson["resourcePaths"]
        self.queryBy = configJson["queryBy"]
        self.createNew = configJson["createNew"]

    @staticmethod
    def concept_to_dict(concept):
        output = {"Structure": "Concept"}
        output["generatingService"] = "quickUMLS"
        output["coveredText"] = concept["ngram"] if "ngram" in concept else None
        output["cui"] = concept["cui"] if "cui" in concept else None
        output["begin"] = concept["start"] if "start" in concept else None
        output["end"] = concept["end"] if "end" in concept else None
        output["preferredName"] = concept["term"] if "term" in concept else None
        output["type"] = lookup(concept["semtypes"][0]) if "semtypes" in concept and len(concept["semtypes"]) > 0 else None
        output["negated"] = False
        return output

