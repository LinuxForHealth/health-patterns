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
"""Utilities for building and manipulating FHIR objects"""
from collections import defaultdict
from typing import DefaultDict
from typing import Dict
from typing import Iterable
from typing import List
from typing import Set
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from nlp_insights.fhir import create_coding


def find_codings(
    codeable_concept: CodeableConcept, system: str, code: str
) -> List[Coding]:
    """Returns a list of coding elements that match the system url and id."""
    if codeable_concept.coding is None:
        return []

    return list(
        filter(lambda c: c.system == system and c.code == code, codeable_concept.coding)
    )


def index_codings(codings: List[Coding]) -> DefaultDict[str, Dict[str, Coding]]:
    """Returns a map of system -> dict[code, coding]"""
    existing_codes: DefaultDict[str, Dict[str, Coding]] = defaultdict(dict)
    for code in codings:
        existing_codes[code.system][code.code] = code
    return existing_codes


def append_coding_obj(codeable_concept: CodeableConcept, coding: Coding) -> bool:
    """Appends a coding object, if it does not exist already"""
    if codeable_concept.coding is None:
        codeable_concept.coding = []

    existing_codings = find_codings(codeable_concept, coding.system, coding.code)
    if not existing_codings:
        codeable_concept.coding.append(coding)
        return True

    return False


def append_coding(
    codeable_concept: CodeableConcept, system: str, code: str, display: str = None
) -> bool:
    """Append the coding to the codebale concept, if the coding does not exist


    Example:
     >>> concept = CodeableConcept.construct()
     >>> append_coding(concept,
     ...               'http://example_system',
     ...               'Code_12345',
     ...               'example display string')
     True
     >>> print(concept.json(indent=2))
     {
       "coding": [
         {
           "code": "Code_12345",
           "display": "example display string",
           "system": "http://example_system"
         }
       ]
     }
    """
    if codeable_concept.coding is None:
        codeable_concept.coding = []

    existing_codings = find_codings(codeable_concept, system, code)
    if not existing_codings:
        new_coding = create_coding.create_coding(system, code, display)
        codeable_concept.coding.append(new_coding)
        return True

    return False


def get_existing_codes_by_system(
    codings: Iterable[Coding],
) -> DefaultDict[str, Set[str]]:
    """Returns a mutable map of system to list of code values

    The returned map is a (mutable) default dict, and will contain empty list for coding
    systems that do not exist in the list of codings.

    Args: codings -  coding objects
    Returns: map of coding system to set of contained codes
    """
    existing_codes: DefaultDict[str, Set[str]] = defaultdict(set)
    for code in codings:
        if code.system:
            if code.system not in existing_codes:
                existing_codes[code.system] = set()

            existing_codes[code.system].add(code.code)

    return existing_codes
