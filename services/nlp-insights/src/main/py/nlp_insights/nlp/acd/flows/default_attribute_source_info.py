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

from nlp_insights.insight_source.fields_of_interest import CodeableConceptRefType
from nlp_insights.nlp.acd.fhir_enrichment.insights.attribute import (
    SourceSearchMap,
    AnnotationContext,
    AcdAttrSourceDfn,
    AttrSourcePropName,
)


# There's an assumption here that this allergy mapping is used
# in a context that is known to be allergy. For example enriching an
# allergy intolerance coding.
# With this assumption, we can assume diagnosis is for an allergy, or if
# no attribute is found the concepts can be searched for correct types.
# This doesn't work in general unstructured text, because then we might
# see a non-allergy diagnosis or CUIs that are not for the patient.
#
ANNOTATION_TYPE_ALLERGY = AnnotationContext(
    attribute_mapping=[
        AcdAttrSourceDfn(
            attr_name="Diagnosis",
            source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
        ),
        AcdAttrSourceDfn(
            attr_name="MedicationAllergy",
            source_prop_names=[AttrSourcePropName.MEDICATION_IND],
        ),
    ]
)


# Annotations to look at when deriving conditions
# We don't want "PotentialDiagnosis" attributes, since those are only
# suspected and not something the patient is believed to have
# We do want "PatientReported".
ANNOTATION_TYPE_CONDITION_DERIVED = AnnotationContext(
    attribute_mapping=[
        AcdAttrSourceDfn(
            attr_name=set(["Diagnosis", "PatientReportedCondition"]),
            source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
        ),
    ],
)


# This condition mapping is currently believed to work in both a condition
# context (enriching a condition's coding)
# Here we can be a lot more liberal about what attribute and concepts we
# consider
ANNOTATION_TYPE_CONDITION_ENRICH = AnnotationContext(
    attribute_mapping=[
        AcdAttrSourceDfn(
            attr_name=set(["Diagnosis"]),
            source_prop_names=[AttrSourcePropName.SYMPTOM_DISEASE_IND],
        ),
    ],
)


# This mapping for medication is intended to be used for constructing
# medication objects from unstructured text.
ANNOTATION_TYPE_MEDICATION = AnnotationContext(
    attribute_mapping=[
        AcdAttrSourceDfn(
            attr_name="PrescribedMedication",
            source_prop_names=[AttrSourcePropName.MEDICATION_IND],
        ),
    ],
)


# There are two root types used as keys for this map
# Fhir Resource & Codeable concept reference type.
# For a concept reference type, we can use a mapping that assumes the text has a specific context,
# such as when we enrich an allergy intolerance coding.
#
# For a FHIR resource, this is the resource we want to create from unstructured text.
# We can't assume the text is only about that resource, or even says anything about that
# kind of resource.
#
# We can be a lot more liberal in what we consider matching attributes and concepts when we
# are aware of the context of the text.
#
# This is why it is possible that we have different mapping for creating Conditions vs
# enriching condition codings.
#
# It's also why in the actual rules we can get away with assuming 'Diagnosis' is talking about an
# allergy diagnosis when enriching an AllergyIntolerance coding...but we could not use that same rule
# if we were to someday try and create an allergy intolerance resource from a diagnostic report.
RELEVANT_ANNOTATIONS_STANDARD_V1_0: SourceSearchMap = {
    Condition: ANNOTATION_TYPE_CONDITION_DERIVED,
    MedicationStatement: ANNOTATION_TYPE_MEDICATION,
    CodeableConceptRefType.ALLERGEN: ANNOTATION_TYPE_ALLERGY,
    CodeableConceptRefType.CONDITION: ANNOTATION_TYPE_CONDITION_ENRICH,
}
