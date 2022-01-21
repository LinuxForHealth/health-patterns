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
Defines methods for adjusting the text of a concept prior to NLP.

The goal of adjustment is to provide context words so that NLP can better understand the
text associated with the concept.

For example if a concept is for an allergy intolerance, appending "allergy" to the text helps NLP
understand that the text refers to an allergy and not a substance or medication

This logic depends greatly on what the input resources have for their coding text. We found
that for the examples we looked at, this logic helped. For other use cases, this logic
may be excessive or incomplete.
"""
from typing import Callable
from typing import Dict
from typing import NamedTuple

from nlp_insights.insight_source.fields_of_interest import (
    CodeableConceptRefType,
    CodeableConceptRef,
)


class AdjustedConceptRef(NamedTuple):
    """Binds concept text that has been adjusted for NLP with the original concept ref"""

    concept_ref: CodeableConceptRef
    adjusted_text: str


def adjust_allergy_text(text: str) -> str:
    """Adjusts a text string that is known to be an allergy

    Args:
        text - the text to adjust
    Returns
        the adjusted text

    Example:
    >>> adjust_allergy_text('peanuts')
    'peanuts allergy'
    >>> adjust_allergy_text('peanut allergy')
    'peanut allergy'
    """
    # Adjust code in order to get the correct codes for the allergy,
    # as the source text contains only the allergen.
    if not any(
        term in text.lower() for term in set(["allergy", "allergic", "allergies"])
    ):
        return text + " allergy"
    return text


DEFAULT_CONCEPT_TEXT_ADJUSTERS: Dict[CodeableConceptRefType, Callable[[str], str]] = {
    CodeableConceptRefType.ALLERGEN: adjust_allergy_text,
}


def adjust_concept_text(
    concept: CodeableConceptRef,
    adjusters: Dict[CodeableConceptRefType, Callable[[str], str]] = None,
) -> AdjustedConceptRef:
    """Performs adjustment on text within a codeable concept.

    Args:
        concept - the concept with text to adjust
        adjusters - (optional) mapping of adjusters to use for each type of concept

    Returns
        adjusted text information, the referenced concept is not modified
    """
    if adjusters:
        adjuster = adjusters.get(concept.type)
    else:
        adjuster = DEFAULT_CONCEPT_TEXT_ADJUSTERS.get(concept.type)

    if adjuster:
        return AdjustedConceptRef(
            concept_ref=concept, adjusted_text=adjuster(concept.code_ref.text)
        )

    return AdjustedConceptRef(concept_ref=concept, adjusted_text=concept.code_ref.text)
