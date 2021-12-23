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
from typing import List
from typing import NamedTuple
from typing import Set
from typing import Type
from typing import Union
from nlp_insights.insight_source.fields_of_interest import CodeableConceptRefType
from nlp_insights.umls import semtype_lookup


class QuickUmlsConcept(NamedTuple):
    """Models a concept returned by QuickUmls

    cui - UMLS concept unique identifier
    covered_text - the text that the identified span covers
    begin - offset of the span's begin
    end - offset of the span's end
    preferred_name - UMLS preferred name for the concept
    types - UMLS type names for the concept.
            These can be used as an aid to disambiguate concepts.
            These names are converted from the quickUmls returned
            data. An example value might be "umls.DiseaseOrSyndrome"
    similarity - QuickUMLS similarity score. The meaning of this value
                 depends on how the instance of QuickUMLS is configured.
                 In general QuickUMLS returns results with a similarity score
                 that is above a configured threshold. nlp-insights can use
                 this score of returned values to further select the best
                 CUI out of the returned set of CUIs.

    The QuickUMLS definition of these values can found in the QuickUMLS
    documentation at: https://github.com/Georgetown-IR-Lab/QuickUMLS
    """

    cui: str
    covered_text: str
    begin: int
    end: int
    preferred_name: str
    types: Set[semtype_lookup.UmlsTypeName]
    similarity: float


class QuickUmlsResponse(NamedTuple):
    """Models a response from QuickUmls,"""

    concepts: List[QuickUmlsConcept]
    service_resp: str  # For debug, the original json response from the service

    def get_most_relevant_concepts(
        self,
        to_what: Union[Type[semtype_lookup.ExtendsResource], CodeableConceptRefType],
    ) -> List[QuickUmlsConcept]:
        """Returns the most relevant concepts from the response

        This filters the QuickUMLS returned concepts by similarity, and
        then returns those concepts with the highest score.

        This should reduce the problem where QuickUMLs returns many
        surface forms that partially match the search phrase, when
        there is a perfect match that is the one that we are interested
        in.

        Args:
            to_what - the resource class (for deriving a new resource),
                      or the concept type (for enrichment) that returned concepts
                      should be relevant to.
        """
        relevant_concepts = [
            concept
            for concept in self.concepts
            if semtype_lookup.is_relevant(to_what, concept.types)
        ]
        if relevant_concepts:
            top_score = max(c.similarity for c in relevant_concepts)
            return [c for c in relevant_concepts if c.similarity == top_score]

        return []
