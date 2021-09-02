from fhir.resources.extension import Extension
from text_analytics.insights import insight_constants
from text_analytics.utils import fhir_object_utils


def update_allergy_with_insights(nlp, allergy, nlp_results):
    insight_num = 0
    for codeable_concept, nlp_response in nlp_results:
        concepts = nlp_response["concepts"]
        if concepts is not None:
            for concept in concepts:
                the_type = concept['type']
                if isinstance(the_type, str):
                    the_type = [the_type]
                if len(set(the_type) & set(["umls.DiseaseOrSyndrome", "umls.PathologicFunction", "umls.SignOrSymptom"])) > 0:
                    insight_num = insight_num + 1
                    insight_id = "insight-" + str(insight_num)

                    if codeable_concept.coding is None:
                        codeable_concept.coding = []
                    fhir_object_utils.add_codings(concept, codeable_concept, insight_id, insight_constants.INSIGHT_ID_STRUCTURED_SYSTEM)

                    insight = Extension.construct()
                    insight.url = insight_constants.INSIGHT_INSIGHT_ENTRY_URL
                    insight_id_ext = fhir_object_utils.create_insight_extension(insight_id, insight_constants.INSIGHT_ID_STRUCTURED_SYSTEM)
                    insight.extension = [insight_id_ext]
                    insight_detail = fhir_object_utils.create_insight_detail_extension(nlp_response)
                    insight.extension.append(insight_detail)

                    fhir_object_utils.add_resource_meta_structured(nlp, allergy)
                    if allergy.meta.extension is None:
                        ext = Extension.construct()
                        ext.url = insight_constants.INSIGHT_RESULT_URL
                        allergy.meta.extension = [ext]
                    result_extension = allergy.meta.extension[0]
                    if result_extension.extension is None:
                        result_extension.extension = []
                    result_extension.extension.append(insight)

    if insight_num == 0:
        return None

    return allergy
