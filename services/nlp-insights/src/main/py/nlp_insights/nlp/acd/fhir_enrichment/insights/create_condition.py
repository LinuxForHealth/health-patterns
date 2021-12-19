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
import json
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition
from ibm_whcs_sdk.annotator_for_clinical_data import ContainerAnnotation
from nlp_insights.fhir import fhir_object_utils
from nlp_insights.insight import id_util
from nlp_insights.insight.builder.derived_resource_builder import (
    DerivedResourceInsightBuilder,
)
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.fhir_enrichment.insights import attribute
from nlp_insights.nlp.acd.fhir_enrichment.insights import confidence
from nlp_insights.nlp.acd.fhir_enrichment.insights import create_codings
from nlp_insights.nlp.nlp_config import AcdNlpConfig


class TrackerEntry(NamedTuple):
    """For a given CUI, this binds the resource being derived to the
    insight containing the evidence.
    """

    resource: Condition
    insight_builder: DerivedResourceInsightBuilder


def create_conditions(
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

    # Tracks the conditions that have been created for a cui
    # If ACD produces multiple insights for the same CUI, we want to reuse the
    # same insight (with an additional span).
    # The key is the insight id value, which is a hash of the source of the
    # insight combined with the cui causing the new resource to be
    # created, plus the new resource type.
    # This creates a globally unique id value that will be the same
    # for multiple occurrences of the same derived concept.
    condition_tracker: Dict[str, TrackerEntry] = {}

    for attr in attribute.get_attribute_sources(acd_output, Condition, source_loc_map):
        if hasattr(attr.best_source.source, "cui") and attr.best_source.source.cui:
            key = id_util.make_hash(text_source, attr.best_source.source.cui, Condition)
            if key not in condition_tracker:
                # Create a new condition + insight and store in the tracker
                condition = Condition.construct(
                    subject=text_source.source_resource.subject
                )
                insight_builder = DerivedResourceInsightBuilder(
                    resource_type=Condition,
                    text_source=text_source,
                    insight_id_value=key,
                    insight_id_system=nlp_config.nlp_system,
                    nlp_response_json=json.dumps(acd_output.to_dict()),
                )
                condition_tracker[key] = TrackerEntry(
                    resource=condition, insight_builder=insight_builder
                )

            # Retrieve condition and insight from tracker,
            condition, insight_builder = condition_tracker[key]

            # Update codings
            # This is most likely a no-op for any attributes after the first one
            # that causes the condition to be created. (CUI is the same).
            # Still, we should let ACD decide whether the codes are the same or not
            # between two attributes and not assume.
            _add_insight_codings_to_condition(condition, attr.best_source.source)

            # Update insight with new span and confidence information
            span = attr.get_attribute_span()
            if span:
                confidences = []
                if attr.attr.insight_model_data:
                    confidences = confidence.get_derived_condition_confidences(
                        attr.attr.insight_model_data
                    )
                insight_builder.add_span(span=span, confidences=confidences)

    if not condition_tracker:
        return None

    for condition, insight in condition_tracker.values():
        insight.append_insight_to_resource_meta(condition)
        insight.append_insight_summary_to_resource(condition)

    return [entry.resource for entry in condition_tracker.values()]


def _add_insight_codings_to_condition(
    condition: Condition, concept: attribute.AttrSourceConcept
) -> None:
    """Adds information from the insight's concept to a condition

    Args:
        Condition - condition to update
        Concept   - concept with data to update the condition with
    """
    if condition.code is None:
        codeable_concept = CodeableConcept.construct()
        codeable_concept.text = create_codings.get_concept_display_text(concept)
        codeable_concept.coding = create_codings.derive_codings_from_acd_concept(
            concept
        )
        condition.code = codeable_concept
    else:
        derived_codes = create_codings.derive_codings_from_acd_concept(concept)
        for dcode in derived_codes:
            fhir_object_utils.append_coding_obj(condition.code, dcode)
