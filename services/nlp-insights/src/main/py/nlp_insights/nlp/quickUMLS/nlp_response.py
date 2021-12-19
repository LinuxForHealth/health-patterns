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
Module for defining data types to represent QuickUmls concepts
"""

import json
from typing import Any
from typing import List
from typing import NamedTuple
from typing import Set

from nlp_insights.umls.semtype_lookup import UmlsTypeName


class QuickUmlsConcept(NamedTuple):
    """Models a concept returned by QuickUmls"""

    cui: str
    covered_text: str
    begin: int
    end: int
    preferred_name: str
    types: Set[UmlsTypeName]
    negated: bool = False


class QuickUmlsResponse(NamedTuple):
    """Models a response from QuickUmls,

    The class should be serialized to json using the
    QuickUmlsEncoder
    """

    concepts: List[QuickUmlsConcept]


class QuickUmlsEncoder(json.JSONEncoder):
    """Json Encoder for QuickUmlsResponse and QuickUmlsConcept

    The built in json encoder can't serialize a set. This class
    converts any set encountered into a sorted list for serialization.

    Example:
    >>> response = QuickUmlsResponse(
    ...                concepts=[
    ...                    QuickUmlsConcept(
    ...                        cui="C12345",
    ...                        covered_text="my text",
    ...                        begin=1000,
    ...                        end=1007,
    ...                        preferred_name="concept preferred name",
    ...                        types=set(["umls.DiseaseOrSyndrome", "umls.CellOrMolecularDysfunction"])
    ...                    )
    ...                ]
    ...             )
    >>> print(json.dumps(response, cls=QuickUmlsEncoder, indent=2))
    [
      [
        [
          "C12345",
          "my text",
          1000,
          1007,
          "concept preferred name",
          [
            "umls.CellOrMolecularDysfunction",
            "umls.DiseaseOrSyndrome"
          ],
          false
        ]
      ]
    ]
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, set):
            return sorted(list(o))
        return json.JSONEncoder.default(self, o)
