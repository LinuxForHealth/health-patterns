import json
import logging

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.dosage import Dosage, DosageDoseAndRate
from fhir.resources.extension import Extension
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.quantity import Quantity
from fhir.resources.timing import Timing
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
from ibm_whcs_sdk import annotator_for_clinical_data as acd
from text_analytics.abstract_nlp_service import NLPService
from text_analytics.acd.config import get_config
from text_analytics.enhance import *
from text_analytics.insights import insight_constants
from text_analytics.insights.add_insights_medication import create_insight
from text_analytics.utils import fhir_object_utils


logger = logging.getLogger()


class ACDService(NLPService):
    types_can_handle = {'AllergyIntolerance': enhance_allergy_intolerance_payload_to_fhir,
                        'Immunization': enhance_immunization_payload_to_fhir,
                        'DiagnosticReport': enhance_diagnostic_report_payload_to_fhir}

    PROCESS_TYPE_UNSTRUCTURED = "ACD Unstructured"
    PROCESS_TYPE_STRUCTURED = "ACD Structured"

    version = "2021-01-01"

    
    def __init__(self, jsonString):
        _config = get_config()
        self.acd_key = _config['ACD_KEY']
        self.acd_url = _config['ACD_URL']
        self.acd_flow = _config['ACD_FLOW']
        self.jsonString = jsonString
        config_dict = json.loads(jsonString)
        if config_dict.get('version') is not None:
            self.version = config_dict.get('version')
        

    def process(self, text):
        service = acd.AnnotatorForClinicalDataV1(
            authenticator=IAMAuthenticator(apikey=self.acd_key),
            version=self.version
        )
        service.set_service_url(self.acd_url)

        logger.info("Calling ACD")
        resp = service.analyze_with_flow(self.acd_flow, text)
        out = resp.to_dict()
        return out


    def add_medications(nlp, diagnostic_report, nlp_output, med_statements_found, med_statements_insight_counter):
        medications = nlp_output.get('MedicationInd')
        for medication in medications:
            med_statements_found, med_statements_insight_counter = create_insight(medication, nlp, nlp_output, diagnostic_report, ACDService.build_medication, med_statements_found, med_statements_insight_counter)

        return med_statements_found, med_statements_insight_counter

    def build_medication(med_statement, medication, insight_id):
        if med_statement.status is None:
            med_statement.status = 'unknown'

        acd_drug = medication.get('drug')[0].get("name1")[0]
        acd_drug_name = acd_drug.get("drugSurfaceForm")


        if type(med_statement.medicationCodeableConcept) is dict and med_statement.medicationCodeableConcept.get("text") == "template":
            codeable_concept = CodeableConcept.construct()
            codeable_concept.text = acd_drug_name
            med_statement.medicationCodeableConcept = codeable_concept
            codeable_concept.coding = []

        fhir_object_utils.add_codings_drug(acd_drug, acd_drug_name, med_statement.medicationCodeableConcept, insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)

        if hasattr(medication, "administration"):
            if med_statement.dosage is None:
                med_statement.dosage = []
            dose = Dosage.construct()
            dose_rate = DosageDoseAndRate.construct()
            dose_with_units = medication.get('administration')[0].get("dosageValue")
            if dose_with_units is not None:
                dose_amount = None
                dose_units = None
                if ' ' in dose_with_units:
                    dose_info = dose_with_units.split(' ')
                    amount = dose_info[0].replace(',','') 
                    try:
                        dose_amount = float(amount)
                    except OverflowError as err:
                        logger.error("Error with dose amount overflow: {}".format(err.message))
                    if isinstance(dose_info[1], str):
                        dose_units = dose_info[1]
                else:
                    amount = dose_with_units.replace(',','') 
                    try:
                        dose_amount = float(amount)
                    except OverflowError as err:
                        logger.error("Error with dose amount overflow: {}".format(err.message))

                if dose_amount is not None:
                    dose_quantity = Quantity.construct()
                    dose_quantity.value = dose_amount
                    if dose_units is not None:
                        dose_quantity.unit = dose_units
                    dose_rate.doseQuantity = dose_quantity
                    dose.doseAndRate = [dose_rate]

            frequency = medication.get('administration')[0].get("frequencyValue")
            if frequency is not None:
                code = None
                display = None

                if frequency in ['Q AM', 'Q AM.', 'AM']:
                    code = 'AM'
                    display = 'AM'
                elif frequency in ['Q PM', 'Q PM.', 'PM']:
                    code = 'PM'
                    display = 'PM'

                if code is not None and display is not None:
                    timing = Timing.construct()
                    timing_codeable_concept = CodeableConcept.construct()
                    timing_codeable_concept.coding = [fhir_object_utils.create_coding(insight_constants.TIMING_URL, code, display)]
                    timing_codeable_concept.text = frequency
                    timing.code = timing_codeable_concept
                    dose.timing = timing

            dose.extension = [fhir_object_utils.create_insight_reference(insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)]
            med_statement.dosage.append(dose)