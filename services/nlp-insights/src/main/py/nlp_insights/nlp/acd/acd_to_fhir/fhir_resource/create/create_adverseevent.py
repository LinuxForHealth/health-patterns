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

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.adverseevent import AdverseEvent
from fhir.resources.coding import Coding
from fhir.resources.identifier import Identifier
from ibm_whcs_sdk.annotator_for_clinical_data import ContainerAnnotation
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    InsightModelData,
)

from nlp_insights.fhir.insight_builder import InsightConfidenceBuilder
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.acd_to_fhir import confidence
from nlp_insights.nlp.acd.acd_to_fhir.fhir_resource.create import abstract_builder
from nlp_insights.nlp.acd.flows import attribute
from nlp_insights.nlp.nlp_config import AcdNlpConfig


class AdverseEventBuilder(abstract_builder.ResourceBuilder):
    """Instructions for building an adverse event resource"""

    def __init__(
        self,
        text_source: UnstructuredText,
        acd_output: ContainerAnnotation,
        nlp_config: AcdNlpConfig
    ):
        super().__init__(text_source, acd_output, nlp_config, AdverseEvent)

    def create_resource(
        self,
        first_acd_attr: attribute.AttributeWithSource,
    ) -> AdverseEvent:

        meddra = [[{'prefName': 'Not available', 'meddraCode': 'Not available'}]]  # default
        # If medra codes are available this can be modified to use them
        # if adverse_event_mods is not None:
        #    for adverse_event_mod in adverse_event_mods:
        #        if 'meddraCodes' in adverse_event_mod:
        #            meddra = adverse_event_mod['meddraCodes']

        condition_name = meddra[0][0]['prefName']
        code = meddra[0][0]['meddraCode']
        source = 'http://medra.com/codings'

        code_template = {
            "system": source,
            "code": code,
            "display": f"{condition_name}"
        }

        type_template = {
            "text": f"{condition_name}",
            "coding": [Coding.construct(**code_template)]
        }
        ade_type = CodeableConcept.construct(**type_template)

        id_template = {
            "type": ade_type,
            "system": source,
            "value": code
        }
        id_type = Identifier.construct(**id_template)

        is_confirmed = first_acd_attr.attr.insight_model_data.medication.adverse
        if is_confirmed is None:
            is_confirmed = 1.0
        else:
            is_confirmed = first_acd_attr.attr.insight_model_data.medication.adverse.usage.considering_score

        actuality_value = "potential"
        if is_confirmed < 0.5:
            actuality_value = "actual"
        a_e = AdverseEvent.construct(subject=self.text_source.subject, identifier=id_type, actuality=actuality_value)

        return a_e

    def update_codings(
        self, resource: AdverseEvent, acd_attr: attribute.AttributeWithSource
    ) -> None:
        # adverseevent = cast(AdverseEvent, resource)
        return None

    def get_confidences(
        self, insight_model_data: InsightModelData
    ) -> List[InsightConfidenceBuilder]:
        return confidence.get_derived_ae_confidences(insight_model_data)
