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

# There's an assumption here that this allergy mapping is used
# in a context that is known to be allergy. For example enriching an
# allergy intolerance coding.
# With this assumption, we can assume diagnosis is for an allergy, or if
# no attribute is found the concepts can be searched for correct types.
# This doesn't work in general unstructured text, because then we might
# see a non-allergy diagnosis or CUIs that are not for the patient.
#
# This can also be used for an allergy manifestation context.
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

# This condition mapping is currently believed to work in both a condition
# context (enriching a condition's coding), and also for constructing
# conditions from unstructured text.
ANNOTATION_TYPE_CONDITION = AnnotationContext(
    attribute_mapping=[
        AcdAttrCuiSourceLoc(
            attr_name=set(["Diagnosis", "PotentialDiagnosis"]),
            source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
        ),
    ],
    concept_fallback=None,
)


# This mapping assumes an immunization context (such as enriching an Immunization
# resources's coding).
# Because of that assumption, we can assume any concepts that look related to immunization
# are codings we are interested in.
#
# We are not aware of an attribute for immunization.
ANNOTATION_TYPE_IMMUNIZATION = AnnotationContext(
    attribute_mapping=None,
    concept_fallback=[
        AcdConceptCuiFallBack(concept_types=semtype_lookup.VACCINE_TYPES)
    ],
)


# This mapping for medication is intended to be used for constructing
# medication objects from unstructured text.
ANNOTATION_TYPE_MEDICATION = AnnotationContext(
    attribute_mapping=[
        AcdAttrCuiSourceLoc(
            attr_name="PrescribedMedication",
            source_prop_names=[AttrSourcePropName.MEDICATION_IND],
        ),
    ],
    concept_fallback=None,
)


# There are two root types used as keys for this map
# Fhir Resource & Codeable concept reference type.
# For a concept reference type, we can use a mapping that assumes the text has a specific context,
# such as when we enrich an allergy intolerance or immunization coding.
#
# For a FHIR resource, this is the resource we want to create from unstructured text.
# We can't assume the text is only about that resource, or even says anything about that
# kind of resource.
#
# We can be a lot more liberal in what we consider matching attributes and concepts when we
# are aware of the context of the text.
#
# This is why it is possible that we could have a different mapping for creating Conditions vs
# enriching condition codings. Even though today we reuse the same rules for both, this could change in
# the future as our understanding of ACD evolves.
#
# It's also why in the actual rules we can get away with assuming 'Diagnosis' is talking about an
# allergy diagnosis when enriching an AllergyIntolerance coding...but we could not use that same rule
# if we were to someday try and create an allergy intolerance resource from a diagnostic report.
RELEVANT_ANNOTATIONS_STANDARD_V1_0: SourceCuiSearchMap = {
    Condition: ANNOTATION_TYPE_CONDITION,
    MedicationStatement: ANNOTATION_TYPE_MEDICATION,
    CodeableConceptRefType.ALLERGEN: ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.MANIFESTATION: ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.CONDITION: ANNOTATION_TYPE_CONDITION,
    CodeableConceptRefType.VACCINE: ANNOTATION_TYPE_IMMUNIZATION,
}
