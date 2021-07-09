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

import os
import configparser

from ibm_whcs_sdk import annotator_for_clinical_data as acd
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator

print("Simple acd call start")


def print_concept(concept):
    output = "CONCEPT: "
    output += "CUI: %s" % concept.cui
    output += ", Span: \"%s\"" % concept.covered_text
    output += ", PreferredName: %s" % concept.preferred_name
    output += ", Type: %s" % concept.type
    if concept.nci_code is not None:
        output += ", NCI: %s" % concept.nci_code
    if concept.rx_norm_id is not None:
        output += ", RxNorm: %s" % concept.rx_norm_id
    if concept.mesh_id is not None:
        output += ", Mesh: %s" % concept.mesh_id
    if concept.snomed_concept_id is not None:
        output += ", Snowmed: %s" % concept.snomed_concept_id
    if concept.loinc_id is not None:
        output += ", LOINC: %s" % concept.loinc_id
    if concept.vocabs is not None:
        output += ", Vocabs: %s" % concept.vocabs
    output += ", negated: %s" % concept.negated
    # print(concept)  # if you want to see what the structure is like
    print(output)


def print_symptom(symptom):
    output = "SYMPTOM: "
    output += "CUI: %s" % symptom.cui
    output += ", Span: \"%s\"" % symptom.covered_text
    output += ", PreferredName: %s" % symptom.symptom_disease_normalized_name
    output += ", Type: %s" % symptom.type
    if symptom.hcc_code is not None:
        output += ", HCC: %s" % symptom.hcc_code
    if symptom.snomed_concept_id is not None:
        output += ", Snomed: %s" % symptom.snomed_concept_id
    if symptom.modality is not None:
        output += ", Modality: %s" % symptom.modality
    output += ", negated: %s" % symptom.negated
    # print(symptom) # if you want to see what the structure is like
    print(output)


# Instantiate service instance
# Replace {version}, {apikey}, and {url} below
# package_directory = os.path.dirname(os.path.abspath(__file__))
# secret_file = package_directory + '/../../../donotcheckin.ini'
acd_file = os.path.abspath('src/acd/acd_config.ini')
print(acd_file)
config = configparser.ConfigParser()
# config.read(secret_file)
config.read(acd_file)
apikey = config.get('ACD_CONFIG', 'WHPA_CDP_ACD_KEY')
service = acd.AnnotatorForClinicalDataV1(
    authenticator=IAMAuthenticator(apikey),
    version="2021-01-01"
)
apiurl = config.get("ACD_CONFIG", "WHPA_CDP_ACD_URL")
service.set_service_url(apiurl)

# text = "COVID-19 vaccine."
text = "Patient has lung cancer, but did not smoke. She may consider chemotherapy as part of a treatment plan."

try:
    flowId = config.get("ACD_CONFIG", "WHPA_CDP_ACD_FLOW")
    resp = service.analyze_with_flow(flowId, text)
    concepts = resp.concepts
    for concept in concepts:
        print_concept(concept)
    symptoms = resp.symptom_disease_ind
    for symptom in symptoms:
        print_symptom(symptom)
except acd.ACDException as ex:
    print("Error Occurred:  Code ", ex.code, " Message ", ex.message, " CorrelationId ", ex.correlation_id)
print("Simple acd call end.")
