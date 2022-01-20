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
"""Functions to update codeable concepts with derived codings"""

import json
import logging
from typing import List
from typing import NamedTuple

from fhir.resources.coding import Coding
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from nlp_insights.insight import id_util
from nlp_insights.insight.builder.enrich_resource_builder import (
    EnrichedResourceInsightBuilder,
)
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.nlp.acd.acd_to_fhir import create_codings
from nlp_insights.nlp.acd.flows import attribute
from nlp_insights.nlp.nlp_config import AcdNlpConfig


logger = logging.getLogger(__name__)


class AcdConceptRef(NamedTuple):
    """Binding between reference to a codeable concept with adjusted text, and an ACD NLP Response"""

    adjusted_concept: AdjustedConceptRef
    acd_response: acd.ContainerAnnotation


def derive_codings(
    insight: AcdConceptRef,
    nlp_config: AcdNlpConfig,
) -> List[Coding]:
    """Derives codings for the insight"""
    derived_codes: List[Coding] = []
    attrs = attribute.get_attribute_sources(
        insight.acd_response,
        insight.adjusted_concept.concept_ref.type,
        nlp_config.acd_attribute_source_map,
    )

    for attr in attrs:
        derived_codes.extend(
            create_codings.derive_codings_from_acd_concept(attr.best_source.source)
        )

    return derived_codes


def update_codeable_concepts_and_meta_with_insights(
    concept_insights: List[AcdConceptRef],
    nlp_config: AcdNlpConfig,
) -> int:
    """Updates the resource with derived insights

    Each element in concept insights contains a reference a codeable concept within the resource to
    enrich, as well as the adjusted text and ACD response for the NLP.

    The codings are updated with additional codings derived by ACD.
    The meta of the FHIR resource is updated with the insight details extension.

    Args:
        fhir_resource - the fhir resource to update the meta
        concept_insights - collection of concepts to enrich with insights.
                           These concepts should be contained within the FHIR resource.
        nlp_config - NLP configuration

    Returns: total number of derived codings added to the resource, across all provided
             codeable concepts.
    """
    for concept_insight in concept_insights:
        builder = EnrichedResourceInsightBuilder(
            enriched_concept=concept_insight.adjusted_concept.concept_ref,
            insight_id_value=id_util.make_hash(
                concept_insight.adjusted_concept.concept_ref
            ),
            insight_id_system=nlp_config.nlp_system,
            nlp_response_json=json.dumps(concept_insight.acd_response.to_dict()),
        )

        builder.add_derived_codings(derive_codings(concept_insight, nlp_config))

        if builder.num_summary_extensions_added > 0:
            builder.append_insight_to_resource_meta()

    return builder.num_summary_extensions_added
