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
"""Attributes and source locations for IBM CDP Flow

   The ACD flow generating these attributes is internal to IBM, however the
   output format is used by many tests
"""

from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement

from text_analytics.insight_source.fields_of_interest import CodeableConceptRefType
from text_analytics.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    AcdAttrSourceLoc,
    AttributeNameAndSourceMap,
    AttrSourcePropName,
)


CDP_ANNOTATION_TYPE_ALLERGY = [
    AcdAttrSourceLoc(
        attr_name="CDP-Allergy", source_prop_names=[AttrSourcePropName.CONCEPTS]
    )
]
CDP_ANNOTATION_TYPE_CONDITION = [
    AcdAttrSourceLoc(
        attr_name="CDP-Condition", source_prop_names=[AttrSourcePropName.CONCEPTS]
    )
]

CDP_ANNOTATION_TYPE_IMMUNIZATION = [
    AcdAttrSourceLoc(
        attr_name="CDP-Immunization", source_prop_names=[AttrSourcePropName.CONCEPTS]
    )
]

CDP_ANNOTATION_TYPE_MEDICATION = [
    AcdAttrSourceLoc(
        attr_name="CDP-Medication",
        source_prop_names=[AttrSourcePropName.MEDICATION_IND],
    )
]


RELEVANT_ANNOTATIONS_CDP: AttributeNameAndSourceMap = {
    Condition: CDP_ANNOTATION_TYPE_CONDITION,
    MedicationStatement: CDP_ANNOTATION_TYPE_MEDICATION,
    CodeableConceptRefType.ALLERGEN: CDP_ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.MANIFESTATION: CDP_ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.CONDITION: CDP_ANNOTATION_TYPE_CONDITION,
    CodeableConceptRefType.VACCINE: CDP_ANNOTATION_TYPE_IMMUNIZATION,
}
