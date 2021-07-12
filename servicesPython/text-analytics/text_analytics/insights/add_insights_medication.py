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

#import caf_logger.logger as caflogger
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.dosage import Dosage, DosageDoseAndRate
from fhir.resources.extension import Extension
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.quantity import Quantity
from fhir.resources.timing import Timing
from text_analytics import logging_codes
from text_analytics.insights import insight_constants
from text_analytics.utils import fhir_object_utils

#logger = caflogger.get_logger('whpa-cdp-text_analytics')


def _create_med_statement_from_template():
    # Currently have to create medication statement object with required fields.
    # Doing just a .construct() and then adding the fields, causing a validation
    # error the first time a field is added
    # TODO: investigate a better way of doing this, ie can we turn off validation temporarily
    med_statement_template = {
        "status": "unknown",
        "medicationCodeableConcept": {

            "text": "template"
        }
    }
    med_statement = MedicationStatement.construct(**med_statement_template)
    return med_statement


def _build_resource(diagnostic_report, acd_output):
    # build insight set from ACD output
    # initially using aci.MedicationInd
    acd_medications = acd_output.medication_ind
    med_statements_found = {}            # key is UMLS ID, value is the FHIR resource
    med_statements_insight_counter = {}  # key is UMLS ID, value is the current insight_num
    if acd_medications is not None:
        for acd_medication in acd_medications:
            cui = acd_medication.cui
            med_statement = med_statements_found.get(cui)
            if med_statement is None:
                med_statement = _create_med_statement_from_template()
                med_statement.meta = fhir_object_utils.add_resource_meta_unstructured(diagnostic_report)
                med_statements_found[cui] = med_statement
                insight_num = 1
            else:
                insight_num = med_statements_insight_counter[cui] + 1
            med_statements_insight_counter[cui] = insight_num
            insight_id = "insight-" + str(insight_num)
            _build_resource_data(med_statement, acd_medication, insight_id)

            insight = Extension.construct()
            insight.url = insight_constants.INSIGHT_INSIGHT_ENTRY_URL

            insight_id_ext = fhir_object_utils.create_insight_extension(insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)
            insight.extension = [insight_id_ext]

            insight_detail = fhir_object_utils.create_insight_detail_extension(acd_output)
            insight.extension.append(insight_detail)

            insight_span = fhir_object_utils.create_insight_span_extension(acd_medication)
            insight.extension.append(insight_span)

            # if there is insight model data, save confidences to insight extension
            insight_model_data = acd_medication.insight_model_data

            if insight_model_data is not None:
                fhir_object_utils.add_medication_confidences(insight.extension, insight_model_data)

            result_extension = med_statement.meta.extension[0]
            result_extension.extension.append(insight)

    if len(med_statements_found) == 0:
        return None
    return list(med_statements_found.values())


def _build_resource_data(med_statement, acd_medication, insight_id):
    if med_statement.status is None:
        # hard code to unknown for now
        med_statement.status = 'unknown'

    # TODO: may need to reconsider hard coding into the first drug and first name entry
    # Currently we have only seen medication entries looking like this,
    # but suspect this may be problematic in the future
    acd_drug = acd_medication.drug[0].get("name1")[0]

    # Update template text
    # Should be template on the first occurrance found of the drug
    # Future occurrances of this drug in the same document will not be set to template
    # First instance will be dict until we create the CodeableConcept the first time
    if type(med_statement.medicationCodeableConcept) is dict and med_statement.medicationCodeableConcept.get("text") == "template":
        codeable_concept = CodeableConcept.construct()
        # TODO: investigate in construction if we should be using drugSurfaceForm or drugNormalizedName
        codeable_concept.text = acd_drug.get("drugSurfaceForm")
        med_statement.medicationCodeableConcept = codeable_concept
        codeable_concept.coding = []

    fhir_object_utils.add_codings_drug(acd_drug, med_statement.medicationCodeableConcept, insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)

    if hasattr(acd_medication, "administration"):
        # Dosage
        if med_statement.dosage is None:
            med_statement.dosage = []
        dose = Dosage.construct()
        dose_rate = DosageDoseAndRate.construct()
        dose_with_units = acd_medication.administration[0].get("dosageValue")
        if dose_with_units is not None:
            dose_amount = None
            dose_units = None
            if ' ' in dose_with_units:
                # for now need parse, assuming units is after the first space
                dose_info = dose_with_units.split(' ')
                amount = dose_info[0].replace(',','') # Remove any commas, e.g. 1,000
                try:
                    dose_amount = float(amount)
                except OverflowError as err:
                    print(err)
                    #logger.error(logging_codes.WHPA_CDP_TEXT_ANALYTICS_NOT_VALID_FLOAT, amount, err.message)
                if isinstance(dose_info[1], str):
                    dose_units = dose_info[1]
            else:
                # if no space, assume only value
                amount = dose_with_units.replace(',','') # Remove any commas, e.g. 1,000
                try:
                    dose_amount = float(amount)
                except OverflowError as err:
                    print(err)
                    #logger.error(logging_codes.WHPA_CDP_TEXT_ANALYTICS_NOT_VALID_FLOAT, amount, err.message)

            if dose_amount is not None:
                dose_quantity = Quantity.construct()
                dose_quantity.value = dose_amount
                if dose_units is not None:
                    dose_quantity.unit = dose_units
                dose_rate.doseQuantity = dose_quantity
                dose.doseAndRate = [dose_rate]

        # medication timing
        frequency = acd_medication.administration[0].get("frequencyValue")
        if frequency is not None:
            code = None
            display = None

            # TODO: Create function to map from ACD frequency to possible FHIR dose timings
            if frequency in ['Q AM', 'Q AM.', 'AM']:
                code = 'AM'
                display = 'AM'
            elif frequency in ['Q PM', 'Q PM.', 'PM']:
                code = 'PM'
                display = 'PM'

            if code is not None and display is not None:
                timing = Timing.construct()
                timing_codeable_concept = CodeableConcept.construct()
                timing_codeable_concept.coding = [fhir_object_utils.create_coding_with_display(insight_constants.TIMING_URL, code, display)]
                timing_codeable_concept.text = frequency
                timing.code = timing_codeable_concept
                dose.timing = timing

        dose.extension = [fhir_object_utils.create_insight_reference(insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)]
        med_statement.dosage.append(dose)


def create_med_statements_from_insights(diagnostic_report, acd_output):
    # Create Condition FHIR resource
    med_statements = _build_resource(diagnostic_report, acd_output)
    if med_statements is not None:
        for med_statement in med_statements:
            med_statement.subject = diagnostic_report.subject
            fhir_object_utils.create_derived_resource_extension(med_statement)
    return med_statements
