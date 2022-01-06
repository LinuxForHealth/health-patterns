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
from nlp_insights.nlp.nlp_config import NlpConfig, QUICK_UMLS_NLP_CONFIG
from nlp_insights.nlp.quickumls.concept_container import (
    QuickUmlsConceptContainer,
    QuickUmlsConcept,
)


class QuickumlsConceptRef(NamedTuple):
    """Binding between ref to a codeable concept and QuickUmls concept container"""

    adjusted_concept: AdjustedConceptRef
    container: QuickUmlsConceptContainer

    @property
    def relevant_concepts(self) -> List[QuickUmlsConcept]:
        """Returns best relevant concepts for the insight"""
        return self.container.get_most_relevant_concepts(
            self.adjusted_concept.concept_ref.type
        )


def _derive_codings(nlp_concept: QuickUmlsConcept) -> List[Coding]:
    """Derives codings from QuickUMLs NLP response

    Today we only return the UMLS code, but in the future we could
    return other codes using this interface as well.
    """
    return [
        create_coding.create_coding(
            system=hl7.UMLS_URL,
            code=nlp_concept.cui,
            display=nlp_concept.preferred_name,
        )
    ]


def update_codeable_concepts_and_meta_with_insights(
    concept_insights: List[QuickumlsConceptRef],
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
            nlp_response_json=concept_insight.container.service_resp,
        )

        derived_codes = [
            coding
            for concept in concept_insight.relevant_concepts
            for coding in _derive_codings(concept)
        ]

        builder.add_derived_codings(derived_codes)

        if builder.num_summary_extensions_added > 0:
            builder.append_insight_to_resource_meta()

    return builder.num_summary_extensions_added
