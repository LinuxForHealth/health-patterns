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
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import NamedTuple
from typing import Optional
from typing import Type

from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.allergyintolerance import AllergyIntoleranceReaction
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition
from fhir.resources.immunization import Immunization
from fhir.resources.resource import Resource


class CodeableConceptRefType(Enum):
    """Type assignments for CodeableConceptTest"""

    ALLERGEN = "ALLERGEN"
    MANIFESTATION = "MANIFESTATION"
    CONDITION = "CONDITION"
    VACCINE = "VACCINE"


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
    fhir_path: str


def _get_concepts_from_allergy_reaction(
    reaction: AllergyIntoleranceReaction, path: str
) -> Iterable[CodeableConceptRef]:
    """Determines concepts from an allergy intolerance reaction

    Args:
        reaction - the reaction within the FHIR resource
        path - path to the reaction element in the FHIR resource

    Returns: concepts with text to be analyzed by NLP
    """
    fields_of_interest = []
    if reaction.manifestation:
        for manif_counter, manif in enumerate(reaction.manifestation):
            if manif.text:
                fhir_path = f"{path}.manifestation[{manif_counter}]"
                fields_of_interest.append(
                    CodeableConceptRef(
                        type=CodeableConceptRefType.MANIFESTATION,
                        code_ref=manif,
                        fhir_path=fhir_path,
                    )
                )

    return fields_of_interest


def _get_allergy_intolerance_concepts_to_analyze(
    allergy_intolerance: AllergyIntolerance,
) -> Iterable[CodeableConceptRef]:
    """Determines concepts that should be analyzed by NLP for an Allergy Intolerance

    Args:
        allergy_intolerance - the FHIR resource

    Returns: Concepts to analyze with NLP
    """
    fields_of_interest = []

    #    AllergyIntolerance.code.text
    if allergy_intolerance.code.text:
        fields_of_interest.append(
            CodeableConceptRef(
                type=CodeableConceptRefType.ALLERGEN,
                code_ref=allergy_intolerance.code,
                fhir_path="AllergyIntolerance.code",
            )
        )

    #  AllergyIntolerance.reaction[]
    if allergy_intolerance.reaction:
        for reaction_counter, reaction in enumerate(allergy_intolerance.reaction):
            fields_of_interest.extend(
                _get_concepts_from_allergy_reaction(
                    reaction, f"AllergyIntolerance.reaction[{reaction_counter}]"
                )
            )

    return fields_of_interest


def _get_condition_concepts_to_analyze(
    condition: Condition,
) -> Iterable[CodeableConceptRef]:
    """Determines concepts with text to be analyzed by NLP for a Condition resource

    args: condition - the condition resource
    returns: concepts to be analyzed
    """
    if condition.code.text:
        return [
            CodeableConceptRef(
                type=CodeableConceptRefType.CONDITION,
                code_ref=condition.code,
                fhir_path="Condition.code",
            )
        ]

    return []


def _get_immunization_concepts_to_analyze(
    immunization: Immunization,
) -> Iterable[CodeableConceptRef]:
    """Determines concepts with text to be analyzed by NLP for a immunization resource

    args: immunization - the condition resource
    returns: concepts to be analyzed
    """
    if immunization.vaccineCode.text:
        return [
            CodeableConceptRef(
                type=CodeableConceptRefType.VACCINE,
                code_ref=immunization.vaccineCode,
                fhir_path="Immunization.vaccineCode",
            )
        ]

    return []


ExtractorFunction = Callable[[Resource], Iterable[CodeableConceptRef]]

_concept_extractors: Dict[Type[Resource], ExtractorFunction] = {
    AllergyIntolerance: _get_allergy_intolerance_concepts_to_analyze,
    Condition: _get_condition_concepts_to_analyze,
    Immunization: _get_immunization_concepts_to_analyze,
}


def get_concepts_for_nlp_analysis(
    resource: Resource,
    concept_extractors: Optional[Dict[Type[Resource], ExtractorFunction]] = None,
) -> Iterable[CodeableConceptRef]:
    """Determines concepts for a FHIR Resource that should be analyzed by NLP

    Args:
        resource - the resource with potential NLP Concepts
        concept_extractors - (optional) mapping of resource class name to extractor
                             function.
    returns:
        references to concepts with text that can be updated with NLP insights
    """
    extractors = concept_extractors if concept_extractors else _concept_extractors
    extractor = extractors.get(type(resource))
    return extractor(resource) if extractor else []
