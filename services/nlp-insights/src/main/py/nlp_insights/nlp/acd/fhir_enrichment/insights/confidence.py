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
"""Functions for extracting confidences from ACD insights

    An ACD confidence score has a direction associated with it.
    For example a diagnosis explicit confidence score would be high for a
    statement such as "The patient has cancer",
    but low low for a statement such as "suspect cancer" or "could be cancer".
    The later two examples would have a high suspected confidence score.

    Although there are many confidence scores available,
    nlp-insights only uses a subset of them that are believed to be
    interesting for our examples and use cases.
"""
from typing import Optional, List

from fhir.resources.extension import Extension
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    InsightModelData,
)

from nlp_insights.fhir import alvearie_ext
from nlp_insights.fhir.code_system import acd_scoring_method


def get_diagnosis_usage_explicit_ext(
    insight_model_data: InsightModelData,
) -> Optional[Extension]:
    """Returns the diagnosis usage explicit confidence extension, if there is one.

    This score is likely to be high for statements such as:
    * The patient was diagnosed with diabetes
    But low for variations like:
    * The patient reports that he has diabetes
    * The patient's brother has diabetes
    * We suspect that the patient has diabetes
    """
    try:
        explicit_score = insight_model_data.diagnosis.usage.explicit_score
    except AttributeError:
        return None

    return alvearie_ext.create_confidence_extension(
        alvearie_ext.create_scoring_method_extension(
            acd_scoring_method.SCORING_METHOD_ACD_CODE_SYSTEM,
            acd_scoring_method.DIAGNOSIS_EXPLICIT_SCORE,
        ),
        explicit_score,
        description="Explicit Score",
    )


def get_diagnosis_usage_patient_reported_ext(
    insight_model_data: InsightModelData,
) -> Optional[Extension]:
    """Returns the diagnosis usage patient reported confidence extension, if there is one.

    This score is likely to be high for statements such as:
    * The patient reports that she has diabetes
    But low for variations like:
    * The patient was diagnosed with diabetes
    * The patient's sister has diabetes
    * The patient might have diabetes
    """
    try:
        patient_reported_score = (
            insight_model_data.diagnosis.usage.patient_reported_score
        )
    except AttributeError:
        return None

    return alvearie_ext.create_confidence_extension(
        alvearie_ext.create_scoring_method_extension(
            acd_scoring_method.SCORING_METHOD_ACD_CODE_SYSTEM,
            acd_scoring_method.DIAGNOSIS_PATIENT_REPORTED_SCORE,
        ),
        patient_reported_score,
        description="Patient Reported Score",
    )


def get_derived_condition_confidences(
    insight_model_data: InsightModelData,
) -> Optional[List[Extension]]:
    """Returns confidences for a derived condition

    Args: insight_model_data - model data from the attribute's concept
    Returns: a list of extensions, or none if confidences could not be computed.
    """
    if not insight_model_data:
        return None

    confidence_list = []
    conf = get_diagnosis_usage_explicit_ext(insight_model_data)
    if conf:
        confidence_list.append(conf)

    conf = get_diagnosis_usage_patient_reported_ext(insight_model_data)
    if conf:
        confidence_list.append(conf)

    return confidence_list if confidence_list else None


def get_medication_taken_confidence(
    insight_model_data: InsightModelData,
) -> Optional[Extension]:
    """Returns the medication take confidence, if the confidence exists

    This score is likely to be high for statements such as:
    * The patient is taking aspirin
    But low for variations like:
    * The patient considered taking aspirin
    """
    try:
        taken_score = insight_model_data.medication.usage.taken_score
    except AttributeError:
        return None

    return alvearie_ext.create_confidence_extension(
        alvearie_ext.create_scoring_method_extension(
            acd_scoring_method.SCORING_METHOD_ACD_CODE_SYSTEM,
            acd_scoring_method.MEDICATION_TAKEN_SCORE,
        ),
        taken_score,
        description="Medication Taken Score",
    )


def get_derived_medication_confidences(
    insight_model_data: InsightModelData,
) -> Optional[List[Extension]]:
    """Returns confidences for a derived medication

    Args: insight_model_data - model data from the attribute's concept
    Returns: a list of extensions, or none if confidences could not be computed.
    """
    if not insight_model_data:
        return None

    confidence_list = []
    conf = get_medication_taken_confidence(insight_model_data)
    if conf:
        confidence_list.append(conf)

    return confidence_list if confidence_list else None
