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
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator

# get the secrets
from quickUMLS.config import get_config
from quickUMLS.semtype_lookup import lookup
# from nlp_service import NLP_SERVICE
import json
import requests


class QuickUMLSService:

    def __init__(self, json_string):
        _config = get_config()
        self.quickUMLS_url = _config['QUICKUMLS_URL']
        # self.parse_config(json_string)

    def process(self, text):
        print("url:", self.quickUMLS_url)

        try:
            print("Calling QUICKUMLS")
            request_body = {"text": text.decode('utf-8')}
            resp = requests.post(self.quickUMLS_url, json=request_body)
            print("RAW QUICKUMLS Response: ", resp.text, "<end>")
            return {"concepts": json.loads(resp.text)}
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
        output["GeneratingService"] = "quickUMLS"
        output["CUI"] = concept["cui"]
        output["Begin"] = concept["start"]
        output["End"] = concept["end"]
        output["PreferredName"] = concept["term"]
        output["Type"] = "umls." + lookup(concept["semtypes"][0] or None)
        # print(concept)  # if you want to see what the structure is like
        return output

    @staticmethod
    def symptom_to_dict(symptom):
        return None
        # Since quickUMLS does not explicitly generate symptoms.
