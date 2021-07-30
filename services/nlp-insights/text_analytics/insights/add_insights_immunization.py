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

from text_analytics.insights import insight_constants
from text_analytics.utils import fhir_object_utils
from fhir.resources.extension import Extension
from fhir.resources.codeableconcept import CodeableConcept


"""
Parameters:
  immunization: FHIR immunization resource object that is updated
  acd_results: json ACD response]
Returns the updated resource if any insights were added to it.  Returns None if no insights found (resource not updated).
"""
def update_immunization_with_insights(nlp, immunization, nlp_results):
    insight_num = 0
    # build insight set from ACD output
    # initially using ICMedication concepts; this could change when we do analysis / tune ACD
    concepts = nlp_results["concepts"]
    if concepts is not None:
        for concept in concepts:
            if concept["type"] == "ICMedication" or concept["type"] == "umls.ImmunologicFactor":
                # TODO check if the coding already exists in the FHIR reqource

                # Add a new insight
                insight_num = insight_num + 1
                insight_id = "insight-" + str(insight_num)

                if immunization.vaccineCode is None:
                    codeable_concept = CodeableConcept.construct()
                    codeable_concept.text = concept["preferredName"]
                    immunization.vaccineCode = codeable_concept
                    codeable_concept.coding = []
                fhir_object_utils.add_codings(concept, immunization.vaccineCode, insight_id, insight_constants.INSIGHT_ID_STRUCTURED_SYSTEM)

                # Create insight for resource level extension
                insight = Extension.construct()
                insight.url = insight_constants.INSIGHT_INSIGHT_ENTRY_URL
                insight_id_ext = fhir_object_utils.create_insight_extension(insight_id, insight_constants.INSIGHT_ID_STRUCTURED_SYSTEM)
                insight.extension = [insight_id_ext]
                # Save ACD response
                insight_detail = fhir_object_utils.create_insight_detail_extension(nlp_results)
                insight.extension.append(insight_detail)

                # Add meta if any insights were added
                fhir_object_utils.add_resource_meta_structured(nlp, immunization)
                if immunization.meta.extension is None:
                    ext = Extension.construct()
                    ext.url = insight_constants.INSIGHT_RESULT_URL
                    immunization.meta.extension = [ext]
                result_extension = immunization.meta.extension[0]
                if result_extension.extension is None:
                    result_extension.extension = []
                result_extension.extension.append(insight)

    if insight_num == 0:  # No insights found
        return None

    return immunization

'''
Adds insights in the FHIR immunization resource (vaccineCode field) for the codes in the ACD Concept.
Parameters:
  immunization: FHIR immunization resource being updates
  concept: Concept with insight being added to FHIR resource
  insight_id: ID of the insight to reference for the codes added
'''
def _build_resource_data(immunization, concept, insight_id):
    if immunization.vaccineCode is None:
        codeable_concept = CodeableConcept.construct()
        codeable_concept.text = concept["preferredName"]
        immunization.vaccineCode = codeable_concept
        codeable_concept.coding = []
    fhir_object_utils.add_codings(concept, immunization.vaccineCode, insight_id, insight_constants.INSIGHT_ID_STRUCTURED_SYSTEM)
