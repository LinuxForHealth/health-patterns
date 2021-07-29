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

from fhir.resources.extension import Extension
from text_analytics.insights import insight_constants
from text_analytics.utils import fhir_object_utils


"""
allergy --> allergy intolerance resource object that is updated
acd_results --> list of list(s) - where the sub list is the fhir field object to update followed by the acd response for that field
    example: [[AllergyIntolerance.code, acd_resp1],[AllergyIntolerance.reaction[0].manifestation[0], acd_resp2],
        [AllergyIntolerance.reaction[0].manifestation[1], acd_resp3]]
"""
def update_allergy_with_insights(nlp, allergy, acd_results):
    insight_num = 0
    # adding codings to each field run through ACD
    for codeable_concept, acd_response in acd_results:
        concepts = acd_response["concepts"]
        if concepts is not None:
            for concept in concepts:
                # Allergen types umls.DiseaseOrSyndrome or umls.PathologicFunction
                # Manifestation types umls.DiseaseOrSyndrome or umls.SignOrSymptom
                # For now not separating the types accepted by field, may have to in the future if we see issues
                if concept["type"] == "umls.DiseaseOrSyndrome" or concept["type"] == "umls.PathologicFunction" or concept["type"] == "umls.SignOrSymptom":

                    # Add a new insight
                    insight_num = insight_num + 1
                    insight_id = "insight-" + str(insight_num)

                    if codeable_concept.coding is None:
                        codeable_concept.coding = []
                    fhir_object_utils.add_codings(concept, codeable_concept, insight_id, insight_constants.INSIGHT_ID_STRUCTURED_SYSTEM)

                    # Create insight for resource level extension
                    insight = Extension.construct()
                    insight.url = insight_constants.INSIGHT_INSIGHT_ENTRY_URL
                    insight_id_ext = fhir_object_utils.create_insight_extension(insight_id, insight_constants.INSIGHT_ID_STRUCTURED_SYSTEM)
                    insight.extension = [insight_id_ext]
                    # Save ACD response
                    insight_detail = fhir_object_utils.create_insight_detail_extension(acd_response)
                    insight.extension.append(insight_detail)

                    # Add meta if any insights were added
                    fhir_object_utils.add_resource_meta_structured(nlp, allergy)
                    if allergy.meta.extension is None:
                        ext = Extension.construct()
                        ext.url = insight_constants.INSIGHT_RESULT_URL
                        allergy.meta.extension = [ext]
                    result_extension = allergy.meta.extension[0]
                    if result_extension.extension is None:
                        result_extension.extension = []
                    result_extension.extension.append(insight)

    if insight_num == 0:  # No insights found
        return None

    return allergy
