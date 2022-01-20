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
"""Functions to create derived medication statement resources"""
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import cast

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.medicationstatement import MedicationStatement
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)
from ibm_whcs_sdk.annotator_for_clinical_data import ContainerAnnotation
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    InsightModelData,
)

from nlp_insights.fhir import fhir_object_utils
from nlp_insights.fhir.code_system import hl7
from nlp_insights.fhir.insight_builder import InsightConfidenceBuilder

from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.acd_to_fhir import confidence
from nlp_insights.nlp.acd.acd_to_fhir.fhir_resource.create import abstract_builder
from nlp_insights.nlp.acd.flows import attribute
from nlp_insights.nlp.nlp_config import AcdNlpConfig


logger = logging.getLogger(__name__)


class MedicationStatementBuilder(abstract_builder.ResourceBuilder):
    """Instructions for building a condition resource"""

    def __init__(
        self,
        text_source: UnstructuredText,
        acd_output: ContainerAnnotation,
        nlp_config: AcdNlpConfig,
    ):
        super().__init__(text_source, acd_output, nlp_config, MedicationStatement)

    def create_resource(
        self,
        first_acd_attr: attribute.AttributeWithSource,
    ) -> MedicationStatement:
        med_ind = first_acd_attr.best_source.source_as(acd.MedicationAnnotation)
        acd_drug = _get_drug_from_annotation(med_ind)

        # The fhir standard requires medicationCodeableConcept for a valid
        # MedicationStatement. So set that now, that way we always have
        # something valid.
        #
        # This sets only the overall text for the medication codeable concept
        # Specific codes are added by update_codings after the
        # resource has been created.
        codeable_concept = CodeableConcept.construct()

        codeable_concept.text = acd_drug.get("drugSurfaceForm")
        codeable_concept.coding = []

        return MedicationStatement.construct(
            subject=self.text_source.subject,
            medicationCodeableConcept=codeable_concept,
            status="unknown",
        )

    def update_codings(
        self, resource: MedicationStatement, acd_attr: attribute.AttributeWithSource
    ) -> None:
        med_ind = acd_attr.best_source.source_as(acd.MedicationAnnotation)
        med_statement = cast(MedicationStatement, resource)
        acd_drug = _get_drug_from_annotation(med_ind)

        if "cui" in acd_drug:
            for cui in acd_drug["cui"].split(","):
                fhir_object_utils.append_coding(
                    med_statement.medicationCodeableConcept,
                    hl7.UMLS_URL,
                    cui,
                    acd_drug.get("drugSurfaceForm"),
                )

        if "rxNormID" in acd_drug:
            for code_id in acd_drug["rxNormID"].split(","):
                fhir_object_utils.append_coding(
                    med_statement.medicationCodeableConcept, hl7.RXNORM_URL, code_id
                )

    def get_confidences(
        self, insight_model_data: InsightModelData
    ) -> List[InsightConfidenceBuilder]:
        return confidence.get_derived_medication_confidences(insight_model_data)


def _get_drug_from_annotation(annotation: acd.MedicationAnnotation) -> Dict[Any, Any]:
    """Returns a dictionary of drug information

    Args:
       annotation - the ACD annotation to get the drug info from

    Return a dictionary
    """
    try:
        return cast(dict, annotation.drug[0].get("name1")[0])
    except (TypeError, IndexError, AttributeError):
        logger.exception("Unable to retrieve drug information")
        return {}
