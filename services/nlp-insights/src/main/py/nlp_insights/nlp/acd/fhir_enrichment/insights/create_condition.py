# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""""
Process ACD output and derive conditions
"""

from collections import namedtuple
from typing import List
from typing import Optional

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)
from ibm_whcs_sdk.annotator_for_clinical_data import ContainerAnnotation
from nlp_insights.fhir import alvearie_ext
from nlp_insights.fhir import fhir_object_utils
from nlp_insights.insight import insight_id
from nlp_insights.insight.span import Span
from nlp_insights.insight.text_fragment import TextFragment
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.fhir_enrichment.insights import confidence
from nlp_insights.nlp.acd.fhir_enrichment.insights.append_codings import (
    append_codings,
    get_concept_display_text,
)
from nlp_insights.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    get_attribute_sources,
    AttrSourceConcept,
)
from nlp_insights.nlp.nlp_config import AcdNlpConfig


def create_conditions_from_insights(
    text_source: UnstructuredText,
    acd_output: ContainerAnnotation,
    nlp_config: AcdNlpConfig,
) -> Optional[List[Condition]]:
    """For the provided source and ACD output, create FHIR condition resources

    Args:
        text_source - the text that NLP was run over
        acd_output - the acd output
        nlp_config - nlp configuration

    Returns conditions derived by NLP, or None if there are no conditions
    """
    source_loc_map = nlp_config.acd_attribute_source_map

    TrackerEntry = namedtuple("TrackerEntry", ["fhir_resource", "id_maker"])
    condition_tracker = {}  # key is UMLS ID, value is TrackerEntry

    for cui_source in get_attribute_sources(acd_output, Condition, source_loc_map):
        if cui_source.sources:
            # some attributes have the cui in multiple places, if so
            # the first available source is the best one
            source: AttrSourceConcept = next(iter(cui_source.sources.values()))

            if source and hasattr(source, "cui") and source.cui:

                if source.cui not in condition_tracker:
                    condition_tracker[source.cui] = TrackerEntry(
                        fhir_resource=Condition.construct(
                            subject=text_source.source_resource.subject
                        ),
                        id_maker=insight_id.insight_id_maker_derive_resource(
                            source=text_source,
                            cui=source.cui,
                            derived=Condition,
                            start=nlp_config.insight_id_start,
                        ),
                    )

                condition, id_maker = condition_tracker[source.cui]

                _add_insight_to_condition(
                    text_source,
                    condition,
                    cui_source.attr,
                    source,
                    acd_output,
                    next(id_maker),
                    nlp_config,
                )

    if not condition_tracker:
        return None

    conditions = [entry.fhir_resource for entry in condition_tracker.values()]

    for condition in conditions:
        fhir_object_utils.append_derived_by_nlp_category_extension(condition)

    return conditions


def _add_insight_to_condition(  # pylint: disable=too-many-arguments;
    text_source: UnstructuredText,
    condition: Condition,
    attr: acd.AttributeValueAnnotation,
    cui_source: AttrSourceConcept,
    acd_output: acd.ContainerAnnotation,
    insight_id_string: str,
    nlp_config: AcdNlpConfig,
) -> None:
    """Adds data from the insight to the condition"""
    insight_id_ext = alvearie_ext.create_insight_id_extension(
        insight_id_string, nlp_config.nlp_system
    )

    source = TextFragment(
        text_source=text_source,
        text_span=Span(begin=attr.begin, end=attr.end, covered_text=attr.covered_text),
    )

    confidences = confidence.get_derived_condition_confidences(attr.insight_model_data)

    nlp_output_ext = nlp_config.create_nlp_output_extension(acd_output)

    unstructured_insight_detail = (
        alvearie_ext.create_derived_from_unstructured_insight_detail_extension(
            source=source,
            confidences=confidences,
            evaluated_output_ext=nlp_output_ext,
        )
    )

    fhir_object_utils.add_insight_to_meta(
        condition, insight_id_ext, unstructured_insight_detail
    )

    _add_insight_codings_to_condition(condition, cui_source)


def _add_insight_codings_to_condition(
    condition: Condition, concept: AttrSourceConcept
) -> None:
    """Adds information from the insight's concept to a condition

    Args:
        Condition - condition to update
        Concept   - concept with data to update the condition with
    """
    if condition.code is None:
        codeable_concept = CodeableConcept.construct()
        codeable_concept.text = get_concept_display_text(concept)
        condition.code = codeable_concept
        codeable_concept.coding = []

    append_codings(concept, condition.code, add_nlp_extension=False)
