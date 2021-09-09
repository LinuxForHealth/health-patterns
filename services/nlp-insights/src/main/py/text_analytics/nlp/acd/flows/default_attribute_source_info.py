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
"""Attributes and source locations for the Standard (v1.0) ACD flow

   This flow is the default annotator flow for the insight cartridge
"""

from typing import List

from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement

from text_analytics.insight_source.fields_of_interest import CodeableConceptRefType
from text_analytics.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    AcdAttrSourceLoc,
    AttributeNameAndSourceMap,
    AttrSourcePropName,
)

from text_analytics.umls.semtype_lookup import VACCINE_TYPES

ANNOTATION_TYPE_ALLERGY = [
    AcdAttrSourceLoc(
        attr_name="Diagnosis",
        source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
    ),
    AcdAttrSourceLoc(
        attr_name="MedicationAllergy",
        source_prop_names=[AttrSourcePropName.MEDICATION_IND],
    ),
]

ANNOTATION_TYPE_CONDITION = [
    AcdAttrSourceLoc(
        attr_name="Diagnosis",
        source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
    )
]


ANNOTATION_TYPE_IMMUNIZATION: List[AcdAttrSourceLoc] = [
    # The default pipeline does not have an annotator for vaccines
    # So fall back on matching Concepts by Type
    AcdAttrSourceLoc(
        attr_name=None,
        source_prop_names=[AttrSourcePropName.CONCEPTS],
        concept_types=VACCINE_TYPES,
    )
]

ANNOTATION_TYPE_MEDICATION = [
    AcdAttrSourceLoc(
        attr_name="PrescribedMedication",
        source_prop_names=[AttrSourcePropName.MEDICATION_IND],
    )
]

RELEVANT_ANNOTATIONS_STANDARD_V1_0: AttributeNameAndSourceMap = {
    Condition: ANNOTATION_TYPE_CONDITION,
    MedicationStatement: ANNOTATION_TYPE_MEDICATION,
    CodeableConceptRefType.ALLERGEN: ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.MANIFESTATION: ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.CONDITION: ANNOTATION_TYPE_CONDITION,
    CodeableConceptRefType.VACCINE: ANNOTATION_TYPE_IMMUNIZATION,
}
