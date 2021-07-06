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
from acd.call_acd_service import call_acd_with_text
# from text_analytics.logging_codes import WHPA_CDP_TEXT_ANALYTICS_ACD_ERROR

# import caf_logger.logger as caflogger

# logger = caflogger.get_logger('whpa-cdp-text-analytics')


def _concept_to_dict(concept):
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


def _symptom_to_dict(symptom):
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


def call_acd_with_text_then_enhance(text):
    # Instantiate service instance
    # Replace {version}, {apikey}, and {url} below
    # service = acd.AnnotatorForClinicalDataV1(
    #     authenticator=IAMAuthenticator(apikey=auth),
    #     version="2021-01-01"
    # )

    return_list = []

    try:

        resp = call_acd_with_text(text)
        print("Enhancing ACD")
        concepts = getattr(resp, "concepts", [])
        if concepts is not None:
            for concept in concepts:
                return_list.append(_concept_to_dict(concept))
        symptoms = getattr(resp, "symptom_disease_ind", [])
        if symptoms is not None:
            for symptom in symptoms:
                return_list.append(_symptom_to_dict(symptom))

    except acd.acdException as ex:
        logger.error(WHPA_CDP_TEXT_ANALYTICS_ACD_ERROR, ex.code, ex.message, ex.correlation_id)

    return return_list
