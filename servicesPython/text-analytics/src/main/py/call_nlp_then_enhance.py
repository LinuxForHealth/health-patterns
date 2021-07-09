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
from acd.acd_service import ACDService


def call_service_then_enhance(nlp, text):
    # Instantiate service instance
    # Replace {version}, {apikey}, and {url} below
    # service = acd.AnnotatorForClinicalDataV1(
    #     authenticator=IAMAuthenticator(apikey=auth),
    #     version="2021-01-01"
    # )

    return_list = []

    resp = nlp.process(text)
    print("Enhancing ACD")
    concepts = resp["concepts"]
    print(resp)
    if concepts is not None:
        for concept in concepts:
            return_list.append(nlp.concept_to_dict(concept))
    symptoms = getattr(resp, "symptom_disease_ind", [])
    # pull out symptoms from UMLS?
    if symptoms is not None:
        for symptom in symptoms:
            return_list.append(nlp.symptom_to_dict(symptom))

    return return_list
