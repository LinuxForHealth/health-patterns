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
"""Derive condition from NLP output"""

from collections import namedtuple
from typing import List
from typing import Optional

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition

from nlp_insights.fhir import alvearie_ig
from nlp_insights.fhir import fhir_object_utils
from nlp_insights.insight.insight_constants import UMLS_URL, SNOMED_URL
from nlp_insights.insight.insight_id import insight_id_maker
from nlp_insights.insight.span import Span
from nlp_insights.insight.text_fragment import TextFragment
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.nlp_config import NlpConfig, QUICK_UMLS_NLP_CONFIG
from nlp_insights.nlp.nlp_response import NlpResponse, NlpCui
from nlp_insights.umls.semtype_lookup import resource_relevant_to_any_type_names


def _add_insight_codings_to_condition(condition: Condition, nlp_cui: NlpCui) -> None:
    """Adds information from the insight's concept to a condition

    Because the entire condition is assumed to be derived from NLP of
    another resource, we do not mark individual codings as derived by
    NLP.

    Args:
        Condition - condition to update
        nlp_cui   - concept with data to update the condition with
    """
    if condition.code is None:
        codeable_concept = CodeableConcept.construct(
            text=nlp_cui.preferred_name, coding=[]
        )
        condition.code = codeable_concept

    existing_codes_by_system = fhir_object_utils.get_existing_codes_by_system(
        condition.code.coding
    )

    if nlp_cui.cui not in existing_codes_by_system[UMLS_URL]:
        coding = fhir_object_utils.create_coding(
            UMLS_URL, nlp_cui.cui, derived_by_nlp=False
        )
        condition.code.coding.append(coding)
        existing_codes_by_system[UMLS_URL].add(nlp_cui.cui)

    if nlp_cui.snomed_ct:
        for snomed_code in nlp_cui.snomed_ct:
            if snomed_code not in existing_codes_by_system[SNOMED_URL]:
                coding = fhir_object_utils.create_coding(
                    SNOMED_URL, snomed_code, derived_by_nlp=False
                )
                condition.code.coding.append(coding)
                existing_codes_by_system[SNOMED_URL].add(snomed_code)


def _add_insight_to_condition(
    text_source: UnstructuredText,
    condition: Condition,
    nlp_cui: NlpCui,
    insight_id: str,
    nlp_config: NlpConfig,
) -> None:
    """Adds data from the insight to the condition"""
    insight_id_ext = fhir_object_utils.create_insight_id_extension(
        insight_id, nlp_config.nlp_system
    )

    source = TextFragment(
        text_source=text_source,
        text_span=Span(
            begin=nlp_cui.begin, end=nlp_cui.end, covered_text=nlp_cui.covered_text
        ),
    )

    nlp_output_ext = nlp_config.create_nlp_output_extension(nlp_cui)

    unstructured_insight_detail = (
        alvearie_ig.create_derived_from_unstructured_insight_detail_extension(
            source=source,
            confidences=None,
            evaluated_output_ext=nlp_output_ext,
        )
    )

    fhir_object_utils.add_insight_to_meta(
        condition, insight_id_ext, unstructured_insight_detail
    )

    _add_insight_codings_to_condition(condition, nlp_cui)


def create_conditions_from_insights(
    text_source: UnstructuredText,
    nlp_response: NlpResponse,
    nlp_config: NlpConfig = QUICK_UMLS_NLP_CONFIG,
) -> Optional[List[Condition]]:
    """For the text source and NLP output, create FHIR condition resources

    Args:
        text_source - the text that NLP was run over
        nlp_response - the nlp response
        nlp_config - NLP configuration


    Returns conditions derived by NLP, or None if there are no conditions
    """
    TrackerEntry = namedtuple("TrackerEntry", ["fhir_resource", "id_maker"])
    condition_tracker = {}  # key is UMLS ID, value is TrackerEntry

    for nlp_cui in nlp_response.nlp_cuis:
        if resource_relevant_to_any_type_names(Condition, nlp_cui.types):
            if nlp_cui.cui not in condition_tracker:
                condition_tracker[nlp_cui.cui] = TrackerEntry(
                    fhir_resource=Condition.construct(
                        subject=text_source.source_resource.subject
                    ),
                    id_maker=insight_id_maker(start=nlp_config.insight_id_start),
                )

            condition, id_maker = condition_tracker[nlp_cui.cui]

            _add_insight_to_condition(
                text_source,
                condition,
                nlp_cui,
                next(id_maker),
                nlp_config,
            )

    if not condition_tracker:
        return None

    conditions = [entry.fhir_resource for entry in condition_tracker.values()]

    for condition in conditions:
        fhir_object_utils.append_derived_by_nlp_extension(condition)

    return conditions
