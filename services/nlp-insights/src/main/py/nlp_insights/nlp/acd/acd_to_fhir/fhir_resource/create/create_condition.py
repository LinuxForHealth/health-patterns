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
""""
Process ACD output and derive conditions
"""
from typing import List
from typing import cast

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition
from ibm_whcs_sdk.annotator_for_clinical_data import ContainerAnnotation
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    InsightModelData,
)

from nlp_insights.fhir import fhir_object_utils
from nlp_insights.fhir.insight_builder import InsightConfidenceBuilder
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.acd_to_fhir import confidence
from nlp_insights.nlp.acd.acd_to_fhir import create_codings
from nlp_insights.nlp.acd.acd_to_fhir.fhir_resource.create import abstract_builder
from nlp_insights.nlp.acd.flows import attribute
from nlp_insights.nlp.nlp_config import AcdNlpConfig


class ConditionBuilder(abstract_builder.ResourceBuilder):
    """Instructions for building a condition resource"""

    def __init__(
        self,
        text_source: UnstructuredText,
        acd_output: ContainerAnnotation,
        nlp_config: AcdNlpConfig,
    ):
        super().__init__(text_source, acd_output, nlp_config, Condition)

    def create_resource(
        self,
        first_acd_attr: attribute.AttributeWithSource,
    ) -> Condition:
        return Condition.construct(subject=self.text_source.subject)

    def update_codings(
        self, resource: Condition, acd_attr: attribute.AttributeWithSource
    ) -> None:
        condition = cast(Condition, resource)

        if condition.code is None:
            codeable_concept = CodeableConcept.construct()
            codeable_concept.text = create_codings.get_concept_display_text(
                acd_attr.best_source.source
            )
            codeable_concept.coding = create_codings.derive_codings_from_acd_concept(
                acd_attr.best_source.source
            )
            condition.code = codeable_concept
        else:
            derived_codes = create_codings.derive_codings_from_acd_concept(
                acd_attr.best_source.source
            )
            for dcode in derived_codes:
                fhir_object_utils.append_coding_obj(condition.code, dcode)

    def get_confidences(
        self, insight_model_data: InsightModelData
    ) -> List[InsightConfidenceBuilder]:
        return confidence.get_derived_condition_confidences(insight_model_data)
