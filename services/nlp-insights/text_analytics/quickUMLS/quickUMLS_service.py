from text_analytics.quickUMLS.config import get_config
from text_analytics.quickUMLS.semtype_lookup import lookup
from text_analytics.enhance import *
import json
import requests
import logging

logger = logging.getLogger()


class QuickUMLSService:
    types_can_handle = {'AllergyIntolerance': enhance_allergy_intolerance_payload_to_fhir,
                        'Immunization': enhance_immunization_payload_to_fhir,
                        'DiagnosticReport': enhance_diagnostic_report_payload_to_fhir}

    def __init__(self, json_string):
        _config = get_config()
        self.quickUMLS_url = _config['QUICKUMLS_URL']

    def process(self, text):
        print("url:", self.quickUMLS_url)

        try:
            if type(text) is bytes:
                request_body = {"text": text.decode('utf-8')}
            else:
                # print("Calling QUICKUMLS" + text)
                request_body = {"text": text}
            resp = requests.post(self.quickUMLS_url, json=request_body)
            # print("RAW QUICKUMLS Response: ", resp.text, "<end>")
            concepts = json.loads(resp.text)
            # print(concepts)
            conceptsList = []
            if concepts is not None:
                for concept in concepts:
                    conceptsList.append(self.concept_to_dict(concept))
            print({"concepts": conceptsList})
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
        output["coveredText"] = concept["ngram"]
        output["cui"] = concept["cui"]
        output["begin"] = concept["start"]
        output["end"] = concept["end"]
        output["preferredName"] = concept["term"]
        output["type"] = lookup(concept["semtypes"][0] or None)
        output["negated"] = False
        # print(concept)  # if you want to see what the structure is like
        return output

    @staticmethod
    def symptom_to_dict(symptom):
        return None
        # Since quickUMLS does not explicitly generate symptoms.
