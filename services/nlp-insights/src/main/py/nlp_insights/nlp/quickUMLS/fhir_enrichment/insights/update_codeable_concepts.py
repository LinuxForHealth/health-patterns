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
"""Update codeable concepts with codings derived from NLP"""

import json
from typing import Generator
from typing import List
from typing import NamedTuple
from fhir.resources.coding import Coding
from nlp_insights.fhir import create_coding
from nlp_insights.fhir.code_system import hl7
from nlp_insights.insight import id_util
from nlp_insights.insight.builder.enrich_resource_builder import (
    EnrichedResourceInsightBuilder,
)
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.insight_source.fields_of_interest import (
    CodeableConceptRefType,
)
from nlp_insights.nlp.nlp_config import NlpConfig, QUICK_UMLS_NLP_CONFIG
from nlp_insights.nlp.quickUMLS.nlp_response import (
    QuickUmlsResponse,
    QuickUmlsConcept,
    QuickUmlsEncoder,
)
from nlp_insights.umls.semtype_lookup import ref_type_relevant_to_any_type_names


class NlpConceptRef(NamedTuple):
    """Binding between ref to a codeable concept and QuickUmls response"""

    adjusted_concept: AdjustedConceptRef
    nlp_response: QuickUmlsResponse


def _relevant_concepts(
    ref_type: CodeableConceptRefType, response: QuickUmlsResponse
) -> Generator[QuickUmlsConcept, None, None]:
    """filter response to those concepts that are relevant to the code reference"""
    for concept in response.concepts:
        if ref_type_relevant_to_any_type_names(ref_type, concept.types):
            yield concept


def _derive_codings(nlp_concept: QuickUmlsConcept) -> List[Coding]:
    """Derives codings from QuickUMLs NLP response"""
    return [
        create_coding.create_coding(
            system=hl7.UMLS_URL,
            code=nlp_concept.cui,
            display=nlp_concept.preferred_name,
        )
    ]


def update_codeable_concepts_and_meta_with_insights(
    concept_insights: List[NlpConceptRef],
    nlp_config: NlpConfig = QUICK_UMLS_NLP_CONFIG,
) -> int:
    """Updates the resource with derived insights

    Each element in concept insights contains a reference a codeable concept within the resource to
    enrich, as well as the adjusted text and response for the NLP.

    The codings are updated with additional codings derived by QuickUmls.
    The meta of the FHIR resource is updated with the insight details extension.

    Args:
        fhir_resource - the fhir resource to update the meta
        concept_insights - collection of concepts to enrich with insights.
                           These concepts should be contained within the FHIR resource.
        nlp_config - the nlp configuration

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
            nlp_response_json=json.dumps(
                concept_insight.nlp_response, cls=QuickUmlsEncoder
            ),
        )

        derived_codes = [
            coding
            for concept in _relevant_concepts(
                concept_insight.adjusted_concept.concept_ref.type,
                concept_insight.nlp_response,
            )
            for coding in _derive_codings(concept)
        ]

        builder.add_derived_codings(derived_codes)
        builder.append_insight_to_resource_meta()

    return builder.num_summary_extensions_added
