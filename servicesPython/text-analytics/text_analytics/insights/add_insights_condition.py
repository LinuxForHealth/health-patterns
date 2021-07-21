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
from fhir.resources.condition import Condition
from fhir.resources.codeableconcept import CodeableConcept

from text_analytics.insights import insight_constants
from text_analytics.utils import fhir_object_utils


def _build_resource(diagnostic_report, acd_output):
    # build insight set from ACD output
    # initially using ICDiagnosis concepts this could change when we do analysis / tune ACD
    # print('lmao')
    # print(acd_output)
    # acd_concepts = acd_output.concepts
    # print(acd_concepts)
    # acd_concepts = acd_output['concepts']
    acd_concepts = acd_output.get('concepts')
    # print('lol')
    conditions_found = {}            # key is UMLS ID, value is the FHIR resource
    conditions_insight_counter = {}  # key is UMLS ID, value is the current insight_id_num
    for concept in acd_concepts:
        if concept["type"] == "ICDiagnosis":
            # print('1')
            condition = conditions_found.get(concept["cui"])
            # print('2')
            if condition is None:
                # print('3')
                condition = Condition.construct()
                condition.meta = fhir_object_utils.add_resource_meta_unstructured(diagnostic_report)
                conditions_found[concept["cui"]] = condition
                insight_id_num = 1
            else:
                insight_id_num = conditions_insight_counter[concept["cui"]] + 1
            conditions_insight_counter[concept["cui"]] = insight_id_num
            insight_id_string = "insight-" + str(insight_id_num)
            _build_resource_data(condition, concept, insight_id_string)

            insight = Extension.construct()
            insight.url = insight_constants.INSIGHT_INSIGHT_ENTRY_URL

            insight_id_ext = fhir_object_utils.create_insight_extension(insight_id_string, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)
            insight.extension = [insight_id_ext]
            insight_detail = fhir_object_utils.create_insight_detail_extension(acd_output)
            insight.extension.append(insight_detail)
            insight_span = fhir_object_utils.create_insight_span_extension(concept)
            insight.extension.append(insight_span)
            # if there is insight model data, save confidences to insight extension
            if "insightModelData" in concept:
                fhir_object_utils.add_diagnosis_confidences(insight.extension, concept["insightModelData"])
            result_extension = condition.meta.extension[0]
            result_extension.extension.append(insight)

    if len(conditions_found) == 0:
        return None  
    return list(conditions_found.values())


def _build_resource_data(condition, concept, insight_id):
    if condition.code is None:
        codeable_concept = CodeableConcept.construct()
        codeable_concept.text = concept["preferredName"]
        condition.code = codeable_concept
        codeable_concept.coding = []
    fhir_object_utils.add_codings(concept, condition.code, insight_id, insight_constants.INSIGHT_ID_UNSTRUCTURED_SYSTEM)


def create_conditions_from_insights(diagnostic_report, acd_output):
    # Create Condition FHIR resource
    conditions = _build_resource(diagnostic_report, acd_output)
    if conditions is not None:
        for condition in conditions:
            condition.subject = diagnostic_report.subject
            fhir_object_utils.create_derived_resource_extension(condition)
    # print(conditions)
    return conditions
