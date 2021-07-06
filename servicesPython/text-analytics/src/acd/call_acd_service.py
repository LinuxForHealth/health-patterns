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
from acd.config import get_config
# from nlp_service import NLP_SERVICE
import json


class ACD_SERVICE:

    def __init__(self, jsonString):
        _config = get_config()
        self.acd_key = _config['WHPA_CDP_ACD_KEY']
        self.acd_url = _config['WHPA_CDP_ACD_URL']
        self.acd_flow = _config['WHPA_CDP_ACD_FLOW']

        self.parse_config(jsonString)

    def call_acd_with_text(self, text):
        # Instantiate service instance
        # Replace {version}, {apikey}, and {url} below
        print("key:", self.acd_key)
        print("url:", self.acd_url)
        print("flow:", self.acd_flow)
        service = acd.AnnotatorForClinicalDataV1(
            authenticator=IAMAuthenticator(apikey=self.acd_key),
            version="2021-01-01"
        )
        service.set_service_url(self.acd_url)

        try:
            print("Calling ACD")
            resp = service.analyze_with_flow(self.acd_flow, text)
            print("RAW ACD Response: ", resp, "<end>")
            return resp

        except acd.ACDException:
            return None
    
    def parse_config(self, jsonString):
        configJson = json.loads(jsonString)
        self.resourceTypes = configJson["resourceTypes"]
        self.resourcePaths = configJson["resourcePaths"]
        self.queryBy = configJson["queryBy"]
        self.createNew = configJson["createNew"]
        
