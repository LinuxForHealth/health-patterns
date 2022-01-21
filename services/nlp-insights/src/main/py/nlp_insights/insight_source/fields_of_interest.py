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
"""
This module defines fields within FHIR resources that contain CodableConcepts
suitable for NLP Analysis.

A CodableConcept has an optional coding field and an optional text field.
The module contains utilities to determine which of these concepts can be used
to produce additional insights. Running NLP over the coding text may produce
additional codes that are not included in the original FHIR resource.

References to the codeable concept may be used to update the concept with discovered
insights.
"""
from enum import Enum
from typing import Iterable
from typing import NamedTuple

from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition
from fhir.resources.resource import Resource
from nlp_insights.fhir.path import FhirPath
from nlp_insights.fhir.reference import ResourceReference


class CodeableConceptRefType(Enum):
    """Type assignments for CodeableConceptTest"""

    ALLERGEN = "ALLERGEN"
    CONDITION = "CONDITION"


class CodeableConceptRef(NamedTuple):
    """
    A REFERENCE with metadata to a CodeableConcept

    The concept contains descriptive text that should be
    analyzed to find more insights (usually codings)

    The referenced codeable concept may be updated as insights
    are discovered by NLP
    """

    type: CodeableConceptRefType
    code_ref: CodeableConcept
    path: FhirPath
    resource_ref: ResourceReference[Resource]

    @property
    def path_text(self) -> FhirPath:
        """Returns the path to the text that is being processed by NLP"""
        return FhirPath(self.path + ".text")

    @property
    def path_coding(self) -> FhirPath:
        """Returns the path to the coding that is being enriched"""
        return FhirPath(self.path + ".coding")


def _get_allergy_intolerance_concepts_to_analyze(
    allergy_ref: ResourceReference[AllergyIntolerance],
) -> Iterable[CodeableConceptRef]:
    """Determines concepts that should be analyzed by NLP for an Allergy Intolerance

    Args:
        allergy_ref - the allergy intolerance's reference

    Returns: Concepts to analyze with NLP
    """
    fields_of_interest = []

    if allergy_ref.resource.code.text:
        fields_of_interest.append(
            CodeableConceptRef(
                resource_ref=allergy_ref,
                type=CodeableConceptRefType.ALLERGEN,
                code_ref=allergy_ref.resource.code,
                path=FhirPath("AllergyIntolerance.code"),
            )
        )

    return fields_of_interest


def _get_condition_concepts_to_analyze(
    condition_ref: ResourceReference[Condition],
) -> Iterable[CodeableConceptRef]:
    """Determines concepts with text to be analyzed by NLP for a Condition resource

    args: condition_ref - the condition resource's reference
    returns: concepts to be analyzed
    """
    if condition_ref.resource.code and condition_ref.resource.code.text:
        return [
            CodeableConceptRef(
                resource_ref=condition_ref,
                type=CodeableConceptRefType.CONDITION,
                code_ref=condition_ref.resource.code,
                path=FhirPath("Condition.code"),
            )
        ]

    return []


def get_concepts_for_nlp_analysis(
    resource_ref: ResourceReference[Resource],
) -> Iterable[CodeableConceptRef]:
    """Determines concepts for a FHIR Resource that should be analyzed by NLP

    Args:
        resource_ref - the resource reference with potential NLP Concepts

    returns:
        references to concepts with text that can be updated with NLP insights
    """
    if allergy := resource_ref.down_cast(AllergyIntolerance):
        return _get_allergy_intolerance_concepts_to_analyze(allergy)

    if condition := resource_ref.down_cast(Condition):
        return _get_condition_concepts_to_analyze(condition)

    return []
