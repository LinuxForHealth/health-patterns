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

from typing import DefaultDict
from typing import Generator
from typing import List
from typing import NamedTuple
from typing import Set

from fhir.resources.resource import Resource

from nlp_insights.fhir import fhir_object_utils
from nlp_insights.fhir.code_system import hl7
from nlp_insights.insight import insight_id
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.insight_source.fields_of_interest import (
    CodeableConceptRef,
    CodeableConceptRefType,
)
from nlp_insights.nlp.nlp_config import NlpConfig, QUICK_UMLS_NLP_CONFIG
from nlp_insights.nlp.quickUMLS.nlp_response import QuickUmlsResponse, QuickUmlsConcept
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


def _append_codes_from_nlp_cui(
    fhir_concept_ref: CodeableConceptRef,
    nlp_concept: QuickUmlsConcept,
    existing_codes_by_system: DefaultDict[str, Set[str]],
) -> int:
    """Appends the code(s) from the nlp_cui to the coding in the concept ref

    Codes are only appended if they do not already exist in the list.

    Args: fhir_concept_ref - reference to the coding list to update
          nlp_concept - code returned by nlp to append
                    This includes a UMLS cui, and possibly one or more
                    associated codes.
          existing_codes_by_system - mapping of code systems to existing codes,
                                     this mapping is updated as codes are added.

    Returns: The number of codes added
    """
    codes_added = 0
    if nlp_concept.cui not in existing_codes_by_system[hl7.UMLS_URL]:
        existing_codes_by_system[hl7.UMLS_URL].add(nlp_concept.cui)
        fhir_object_utils.append_derived_by_nlp_coding(
            fhir_concept_ref.code_ref,
            hl7.UMLS_URL,
            nlp_concept.cui,
            nlp_concept.preferred_name,
        )
        codes_added += 1

    if nlp_concept.snomed_ct:
        for snomed_code in nlp_concept.snomed_ct:
            if snomed_code not in existing_codes_by_system[hl7.SNOMED_URL]:
                existing_codes_by_system[hl7.SNOMED_URL].add(nlp_concept.cui)
                fhir_object_utils.append_derived_by_nlp_coding(
                    fhir_concept_ref.code_ref, hl7.SNOMED_URL, snomed_code
                )
                codes_added += 1

    return codes_added


def _add_codeable_concept_insight(
    fhir_resource: Resource,
    nlp_concept_ref: NlpConceptRef,
    id_maker: Generator[str, None, None],
    nlp_config: NlpConfig,
) -> int:
    """Updates a codeable concept and resource meta with insights.

    The codeable concept referenced by the insight is updated with codings that were
    derived from the text.

    The meta extension for the supplied resource is updated with the insight id and
    reference path.

    Args:
        fhir_resource - the resource to update the meta with the new insight
        insight - binding between the concept text that was analyzed by ACD-NLP and the
                  NLP response for that analysis.
        id_maker - generator for producing ids for insights

    Returns: the number of codings added to the codeable concept.
    """
    codes_added = 0
    concept_ref: CodeableConceptRef = nlp_concept_ref.adjusted_concept.concept_ref

    if concept_ref.code_ref.coding is None:
        concept_ref.code_ref.coding = []

    existing_codes_by_system = fhir_object_utils.get_existing_codes_by_system(
        concept_ref.code_ref.coding
    )
    for nlp_cui in _relevant_concepts(concept_ref.type, nlp_concept_ref.nlp_response):
        codes_added += _append_codes_from_nlp_cui(
            concept_ref, nlp_cui, existing_codes_by_system
        )

    if codes_added:
        fhir_object_utils.append_insight_with_path_expr_to_resource_meta(
            fhir_resource=fhir_resource,
            insight_id=next(id_maker),
            system=nlp_config.nlp_system,
            fhir_path=nlp_concept_ref.adjusted_concept.concept_ref.fhir_path,
            nlp_output_uri=nlp_config.get_nlp_output_loc(nlp_concept_ref.nlp_response),
        )

    return codes_added


def update_codeable_concepts_and_meta_with_insights(
    fhir_resource: Resource,
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
    num_codes_added: int = 0

    for concept_insight in concept_insights:
        id_maker = insight_id.insight_id_maker_update_concept(
            concept=concept_insight.adjusted_concept.concept_ref,
            resource=fhir_resource,
            start=nlp_config.insight_id_start,
        )
        num_codes_added += _add_codeable_concept_insight(
            fhir_resource, concept_insight, id_maker, nlp_config
        )

    return num_codes_added
