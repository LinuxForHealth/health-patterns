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


class ACDService:

    def __init__(self, json_string):
        _config = get_config()
        self.acd_key = _config['WHPA_CDP_ACD_KEY']
        self.acd_url = _config['WHPA_CDP_ACD_URL']
        self.acd_flow = _config['WHPA_CDP_ACD_FLOW']

        #self.parse_config(json_string)

    def process(self, text):
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
            print(type(resp))
            return vars(resp)

        except acd.ACDException:
            return None
    
    def parse_config(self, jsonString):
        configJson = json.loads(jsonString)
        self.resourceTypes = configJson["resourceTypes"] or None
        self.resourcePaths = configJson["resourcePaths"]
        self.queryBy = configJson["queryBy"]
        self.createNew = configJson["createNew"]

    @staticmethod
    def concept_to_dict(concept):
        output = {"Structure": "Concept"}
        output["CUI"] = concept.cui
        output["Span"] = concept.covered_text
        output["Begin"] = concept.begin
        output["End"] = concept.end
        output["PreferredName"] = concept.preferred_name
        output["Type"] = concept.type
        if concept.nci_code is not None:
            output["NCI"] = concept.nci_code
        if concept.rx_norm_id is not None:
            output["RxNorm"] = concept.rx_norm_id
        if concept.mesh_id is not None:
            output["Mesh"] = concept.mesh_id
        if concept.snomed_concept_id is not None:
            output["Snowmed"] = concept.snomed_concept_id
        if concept.loinc_id is not None:
            output["LOINC"] = concept.loinc_id
        if concept.vocabs is not None:
            output["Vocabs"] = concept.vocabs
        output["negated"] = concept.negated
        # print(concept)  # if you want to see what the structure is like
        return output

    @staticmethod
    def symptom_to_dict(symptom):
        output = {"Structure": "Symptom"}
        output["CUI"] = symptom.cui
        output["Span"] = symptom.covered_text
        output["Begin"] = symptom.begin
        output["End"] = symptom.end
        output["PreferredName"] = symptom.symptom_disease_normalized_name
        output["Type"] = symptom.type
        if symptom.hcc_code is not None:
            output["HCC"] = symptom.hcc_code
        if symptom.snomed_concept_id is not None:
            output["Snomed"] = symptom.snomed_concept_id
        if symptom.modality is not None:
            output["Modality"] = symptom.modality
        output["negated"] = symptom.negated
        # print(symptom) # if you want to see what the structure is like
        return output