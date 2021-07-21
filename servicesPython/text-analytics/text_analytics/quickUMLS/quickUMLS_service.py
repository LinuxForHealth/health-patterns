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

# get the secrets
from text_analytics.quickUMLS.config import get_config
from text_analytics.quickUMLS.semtype_lookup import lookup
from text_analytics.enhance import *
# from nlp_service import NLP_SERVICE
import json
import requests


class QuickUMLSService:

    types_can_handle = {'AllergyIntolerance': enhance_allergy_intolerance_payload_to_fhir, 
                        'Immunization': enhance_immunization_payload_to_fhir,
                        'DiagnosticReport': enhance_diagnostic_report_payload_to_fhir}

    def __init__(self, json_string):
        _config = get_config()
        self.quickUMLS_url = _config['QUICKUMLS_URL']
        # self.parse_config(json_string)

    def process(self, text):
        print("url:", self.quickUMLS_url)

        try:
            if type(text) is bytes:
                print("Calling QUICKUMLS" + text.decode('utf-8'))
                request_body = {"text": text.decode('utf-8')}
            else:
                print("Calling QUICKUMLS" + text)
                request_body = {"text": text}
            resp = requests.post(self.quickUMLS_url, json=request_body)
            print("RAW QUICKUMLS Response: ", resp.text, "<end>")
            concepts = json.loads(resp.text)
            print(concepts)
            conceptsList = []
            if concepts is not None:
                for concept in concepts:
                    conceptsList.append(self.concept_to_dict(concept))
            print(conceptsList)
            return {"concepts": conceptsList}
        except requests.exceptions:
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
