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
Module for defining data types to represent simple NLP concepts
"""

from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from text_analytics.umls.semtype_lookup import UmlsTypeName


class NlpCui(NamedTuple):
    """Models concepts returned by a very simple NLP capable of cui detection"""

    cui: str
    covered_text: str
    begin: int
    end: int
    preferred_name: str
    types: Set[UmlsTypeName]
    snomed_ct: Optional[Set[str]]
    negated: bool = False


class NlpResponse(NamedTuple):
    """Models a response from a very simple NLP engine"""

    nlp_cuis: List[NlpCui]
