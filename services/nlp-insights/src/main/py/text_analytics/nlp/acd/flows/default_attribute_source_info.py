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

from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement

from text_analytics.insight_source.fields_of_interest import CodeableConceptRefType
from text_analytics.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    SourceCuiSearchMap,
    AnnotationContext,
    AcdConceptCuiFallBack,
    AcdAttrCuiSourceLoc,
    AttrSourcePropName,
)
from text_analytics.umls import semtype_lookup

ANNOTATION_TYPE_ALLERGY = AnnotationContext(
    attribute_mapping=[
        AcdAttrCuiSourceLoc(
            attr_name="Diagnosis",
            source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
        ),
        AcdAttrCuiSourceLoc(
            attr_name="MedicationAllergy",
            source_prop_names=[AttrSourcePropName.MEDICATION_IND],
        ),
    ],
    concept_fallback=[
        AcdConceptCuiFallBack(concept_types=semtype_lookup.ALLERGEN_TYPES),
    ],
)

ANNOTATION_TYPE_CONDITION = AnnotationContext(
    attribute_mapping=[
        AcdAttrCuiSourceLoc(
            attr_name=set(["Diagnosis", "PotentialDiagnosis"]),
            source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
        ),
    ],
    concept_fallback=None,
)

ANNOTATION_TYPE_IMMUNIZATION = AnnotationContext(
    attribute_mapping=None,
    concept_fallback=[
        AcdConceptCuiFallBack(concept_types=semtype_lookup.VACCINE_TYPES)
    ],
)

ANNOTATION_TYPE_MEDICATION = AnnotationContext(
    attribute_mapping=[
        AcdAttrCuiSourceLoc(
            attr_name="PrescribedMedication",
            source_prop_names=[AttrSourcePropName.MEDICATION_IND],
        ),
    ],
    concept_fallback=None,
)


RELEVANT_ANNOTATIONS_STANDARD_V1_0: SourceCuiSearchMap = {
    Condition: ANNOTATION_TYPE_CONDITION,
    MedicationStatement: ANNOTATION_TYPE_MEDICATION,
    CodeableConceptRefType.ALLERGEN: ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.MANIFESTATION: ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.CONDITION: ANNOTATION_TYPE_CONDITION,
    CodeableConceptRefType.VACCINE: ANNOTATION_TYPE_IMMUNIZATION,
}
