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
"""Derive medication statements from NLP output"""

from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.reference import Reference

from nlp_insights.fhir import create_coding
from nlp_insights.fhir import fhir_object_utils
from nlp_insights.fhir.code_system import hl7
from nlp_insights.insight import id_util
from nlp_insights.insight.builder.derived_resource_builder import (
    DerivedResourceInsightBuilder,
)
from nlp_insights.insight.span import Span
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.nlp_config import NlpConfig, QUICK_UMLS_NLP_CONFIG
from nlp_insights.nlp.quickUMLS.nlp_response import (
    QuickUmlsResponse,
    QuickUmlsConcept,
)


def _add_codings_to_medication_stmt(
    medication_stmt: MedicationStatement, concept: QuickUmlsConcept
) -> None:
    """Adds information from the insight's concept to a MedicationStatement

    Because the entire medication statement is assumed to be derived from NLP of
    another resource, we do not mark individual codings as derived by
    NLP.

    Args:
        medication_stmt - condition to update
        concept   - concept with data to update the condition with
    """
    if medication_stmt.medicationCodeableConcept is None:
        codeable_concept = CodeableConcept.construct(
            text=concept.preferred_name, coding=[]
        )
        medication_stmt.medicationCodeableConcept = codeable_concept

    existing_codes_by_system = fhir_object_utils.get_existing_codes_by_system(
        medication_stmt.medicationCodeableConcept.coding
    )

    if concept.cui not in existing_codes_by_system[hl7.UMLS_URL]:
        coding = create_coding.create_coding(hl7.UMLS_URL, concept.cui)
        medication_stmt.medicationCodeableConcept.coding.append(coding)
        existing_codes_by_system[hl7.UMLS_URL].add(concept.cui)


def _create_minimum_medication_statement(
    subject: Reference,
    concept: QuickUmlsConcept,
) -> MedicationStatement:
    """Creates a new medication statement, with minimum fields set

    The object is created with a status of 'unknown' and a
    medicationCodeableConcept with text set based on the
    drug information in the provided concept.

    Args:
        subject - The subject of the medication statement
        concept - the insight returned by NLP

    Returns the new medication statement
    """
    codeable_concept = CodeableConcept.construct(text=concept.preferred_name, coding=[])

    return MedicationStatement.construct(
        subject=subject, medicationCodeableConcept=codeable_concept, status="unknown"
    )


class TrackerEntry(NamedTuple):
    """For a given CUI, this binds the resource being derived to the
    insight containing the evidence.
    """

    resource: MedicationStatement
    insight_builder: DerivedResourceInsightBuilder


def create_med_statements(
    text_source: UnstructuredText,
    nlp_response: QuickUmlsResponse,
    nlp_config: NlpConfig = QUICK_UMLS_NLP_CONFIG,
) -> Optional[List[MedicationStatement]]:
    """For the text source and NLP output, create FHIR medication statement resources

    Args:
        text_source - the resource text that NLP was run over
        nlp_response - the nlp concepts
        nlp_conifg - nlp configuration

    Returns conditions derived by NLP, or None if there are no conditions
    """
    # The key is the insight id value, which is a hash of the source of the
    # insight combined with the causing the new resource to be
    # created, plus the new resource type.
    # This creates a globally unique id value that will be the same
    # for multiple occurrences of the same derived concept.
    medication_tracker: Dict[str, TrackerEntry] = {}

    for concept in nlp_response.get_most_relevant_concepts(MedicationStatement):
        key = id_util.make_hash(text_source, concept.cui, MedicationStatement)

        if key not in medication_tracker:
            new_medication_stmt = _create_minimum_medication_statement(
                subject=text_source.source_resource.subject, concept=concept
            )

            insight_builder = DerivedResourceInsightBuilder(
                resource_type=MedicationStatement,
                text_source=text_source,
                insight_id_value=key,
                insight_id_system=nlp_config.nlp_system,
                nlp_response_json=nlp_response.service_resp,
            )

            medication_tracker[key] = TrackerEntry(
                resource=new_medication_stmt, insight_builder=insight_builder
            )

        med_stmt, insight_builder = medication_tracker[key]
        _add_codings_to_medication_stmt(med_stmt, concept)

        insight_builder.add_span(
            Span(
                begin=concept.begin,
                end=concept.end,
                covered_text=concept.covered_text,
            ),
            confidences=[],
        )

    if not medication_tracker:
        return None

    for medication, builder in medication_tracker.values():
        builder.append_insight_to_resource_meta(medication)
        builder.append_insight_summary_to_resource(medication)

    return [entry.resource for entry in medication_tracker.values()]
