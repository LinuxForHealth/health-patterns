from ibm_whcs_sdk import annotator_for_clinical_data as acd
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
from text_analytics.acd.config import get_config
from text_analytics.enhance.enhance_allergy_intolerance_payload import enhance_allergy_intolerance_payload_to_fhir
from text_analytics.enhance.enhance_diagnostic_report_payload import enhance_diagnostic_report_payload_to_fhir
from text_analytics.enhance.enhance_immunization_payload import enhance_immunization_payload_to_fhir
import json
import logging

from text_analytics.abstract_nlp_service import NLPService

logger = logging.getLogger()


class ACDService(NLPService):
    types_can_handle = {'AllergyIntolerance': enhance_allergy_intolerance_payload_to_fhir,
                        'Immunization': enhance_immunization_payload_to_fhir,
                        'DiagnosticReport': enhance_diagnostic_report_payload_to_fhir}

    def __init__(self, json_string):
        _config = get_config()
        self.acd_key = _config['WHPA_CDP_ACD_KEY']
        self.acd_url = _config['WHPA_CDP_ACD_URL']
        self.acd_flow = _config['WHPA_CDP_ACD_FLOW']

        # self.parse_config(json_string)

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
            print(text)
            resp = service.analyze_with_flow(self.acd_flow, text)
            # print("RAW ACD Response: ", resp, "<end>")
            out = resp.to_dict()
            print(out)
            return out

        except acd.ACDException as err:
            logger.error("ACD could not be run on text: " + text + " with error: {}".format(err.message))
            return

    def parse_config(self, jsonString):
        configJson = json.loads(jsonString)
        self.resourceTypes = configJson["resourceTypes"] or None
        self.resourcePaths = configJson["resourcePaths"]
        self.queryBy = configJson["queryBy"]
        self.createNew = configJson["createNew"]

    @staticmethod
    def concept_to_dict(concept):
        return concept
        output = {"Structure": "Concept"}
        output["generating_service"] = "ACD"
        output["cui"] = concept["cui"]
        output["coveredText"] = concept["coveredText"]
        output["begin"] = concept.begin
        output["end"] = concept.end
        output["preferred_name"] = concept.preferred_name
        output["type"] = concept.type
        if concept.nci_code is not None:
            output["nci_code"] = concept.nci_code
        if concept.rx_norm_id is not None:
            output["rx_norm_id"] = concept.rx_norm_id
        if concept.mesh_id is not None:
            output["mesh_id"] = concept.mesh_id
        if concept.snomed_concept_id is not None:
            output["snomed_concept_id"] = concept.snomed_concept_id
        if concept.loinc_id is not None:
            output["loinc_id"] = concept.loinc_id
        if concept.vocabs is not None:
            output["vocabs"] = concept.vocabs
        output["negated"] = concept.negated
        # print(concept)  # if you want to see what the structure is like
        return output

    @staticmethod
    def symptom_to_dict(symptom):
        output = {"Structure": "Symptom"}
        output["generating_service"] = "ACD"
        output["cui"] = symptom.cui
        output["covered_text"] = symptom.covered_text
        output["begin"] = symptom.begin
        output["end"] = symptom.end
        output["preferred_name"] = symptom.symptom_disease_normalized_name
        output["type"] = symptom.type
        if symptom.hcc_code is not None:
            output["hcc_code"] = symptom.hcc_code
        if symptom.snomed_concept_id is not None:
            output["snomed_concept_id"] = symptom.snomed_concept_id
        if symptom.modality is not None:
            output["modality"] = symptom.modality
        output["negated"] = symptom.negated
        # print(symptom) # if you want to see what the structure is like
        return output
