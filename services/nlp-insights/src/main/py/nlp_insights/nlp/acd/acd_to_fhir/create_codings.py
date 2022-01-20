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
Create Codings
"""
from typing import Optional, cast, List

from fhir.resources.coding import Coding
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from nlp_insights.fhir import create_coding
from nlp_insights.fhir.code_system import hl7
from nlp_insights.nlp.acd.flows import attribute


def get_concept_display_text(concept: attribute.AttrSourceConcept) -> Optional[str]:
    """Retrieve display text for concept"""
    display_text: Optional[str] = None
    if hasattr(concept, "preferred_name") and concept.preferred_name:
        display_text = concept.preferred_name
    elif (
        hasattr(concept, "symptom_disease_normalized_name")
        and concept.symptom_disease_normalized_name
    ):
        display_text = concept.symptom_disease_normalized_name
    elif isinstance(concept, acd.MedicationAnnotation):
        ann = cast(acd.MedicationAnnotation, concept)
        if (
            ann.drug
            and "name1" in ann.drug[0]
            and ann.drug[0]["name1"]
            and "drugNormalizedName" in ann.drug[0]["name1"]
        ):
            display_text = ann.drug[0].get("name1")[0]["drugNormalizedName"]

    return display_text


def create_codings(
    system: str, code: str, display: Optional[str] = None
) -> List[Coding]:
    """Create one or more codings

    Args:
        system - system to use for the coding
        code - code value, possibly a list of codes separated by a ','
        display - [optional], display text for the code
    Returns:
        List of Coding objects
    """

    return [create_coding.create_coding(system, c, display) for c in code.split(",")]


def derive_codings_from_acd_concept(
    concept: attribute.AttrSourceConcept,
) -> List[Coding]:
    """Derives Codings from the concept"""
    codes = []
    if hasattr(concept, "cui") and concept.cui is not None:
        codes += create_codings(
            hl7.UMLS_URL,
            concept.cui,
            get_concept_display_text(concept),
        )

    if hasattr(concept, "snomed_concept_id") and concept.snomed_concept_id:
        codes += create_codings(
            hl7.SNOMED_URL,
            concept.snomed_concept_id,
        )

    if hasattr(concept, "nci_code") and concept.nci_code:
        codes += create_codings(hl7.NCI_URL, concept.nci_code)
    if hasattr(concept, "loinc_id") and concept.loinc_id:
        codes += create_codings(hl7.LOINC_URL, concept.loinc_id)
    if hasattr(concept, "mesh_id") and concept.mesh_id:
        codes += create_codings(hl7.MESH_URL, concept.mesh_id)
    if hasattr(concept, "icd9_code") and concept.icd9_code:
        codes += create_codings(hl7.ICD9_URL, concept.icd9_code)
    if hasattr(concept, "icd10_code") and concept.icd10_code:
        codes += create_codings(hl7.ICD10_URL, concept.icd10_code)

    if hasattr(concept, "rx_norm_id") and concept.rx_norm_id:
        codes += create_codings(hl7.RXNORM_URL, concept.rx_norm_id)

    return codes
