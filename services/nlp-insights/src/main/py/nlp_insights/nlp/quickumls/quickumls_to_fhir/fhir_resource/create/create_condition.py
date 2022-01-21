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
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition

from nlp_insights.fhir import create_coding
from nlp_insights.fhir import fhir_object_utils
from nlp_insights.fhir.code_system import hl7
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.nlp_config import NlpConfig
from nlp_insights.nlp.quickumls.concept_container import (
    QuickUmlsConceptContainer,
    QuickUmlsConcept,
)

from nlp_insights.nlp.quickumls.quickumls_to_fhir.fhir_resource.create import (
    abstract_builder,
)


class ConditionBuilder(abstract_builder.ResourceBuilder):
    """Instructions for building a condition resource from QuickUMLS"""

    def __init__(
        self,
        text_source: UnstructuredText,
        concept_container: QuickUmlsConceptContainer,
        nlp_config: NlpConfig,
    ):
        super().__init__(text_source, concept_container, nlp_config, Condition)

    def create_resource(
        self,
        first_concept: QuickUmlsConcept,
    ) -> Condition:
        return Condition.construct(subject=self.text_source.source_ref.resource.subject)

    def update_codings(self, resource: Condition, concept: QuickUmlsConcept) -> None:
        if resource.code is None:
            codeable_concept = CodeableConcept.construct(
                text=concept.preferred_name, coding=[]
            )
            resource.code = codeable_concept

        existing_codes_by_system = fhir_object_utils.get_existing_codes_by_system(
            resource.code.coding
        )

        if concept.cui not in existing_codes_by_system[hl7.UMLS_URL]:
            coding = create_coding.create_coding(hl7.UMLS_URL, concept.cui)
            resource.code.coding.append(coding)
            existing_codes_by_system[hl7.UMLS_URL].add(concept.cui)
