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

"""Functions to append codings that appear in an ACD style CUI"""

import logging
from typing import Optional
from typing import cast

from fhir.resources.codeableconcept import CodeableConcept
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from nlp_insights.fhir import fhir_object_utils
from nlp_insights.insight import insight_constants
from nlp_insights.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    AttrSourceConcept,
)


logger = logging.getLogger(__name__)


def _append_coding_entries_with_extension(
    codeable_concept: CodeableConcept,
    system: str,
    csv_code_id: str,
    display: str = None,
) -> int:
    """Separates each code from a csv string and appends the code to the codeable concept

    Args:
        codeable_concept - concept to update
        system - system to use for the code(s)
        csv_code_id - code(s) to append
    Returns: number of codes added
    """
    codes_added = 0
    for code_id in csv_code_id.split(","):
        codes_added += fhir_object_utils.append_derived_by_nlp_coding(
            codeable_concept, system, code_id, display
        )

    return codes_added


def _append_coding_entries(
    codeable_concept: CodeableConcept,
    system: str,
    csv_code_id: str,
    display: str = None,
) -> int:
    """Appends multiple codings when the id may be a csv list of codes

    An NLP derived extension is NOT added.
    A code will not be added if a code with the same system and id already exists

    Args:
        codeable_concept - concept to add code to
        system - system for the code
        csv_code_id - an id for csv of ids to add codings
    """
    codes_added: int = 0
    for code_id in csv_code_id.split(","):
        codes_added += fhir_object_utils.append_coding(
            codeable_concept, system, code_id, display
        )
    return codes_added


def get_concept_display_text(concept: AttrSourceConcept) -> Optional[str]:
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

    logger.debug("display text for concept is %s", display_text)
    return display_text


def append_codings(
    concept: AttrSourceConcept,
    codeable_concept: CodeableConcept,
    add_nlp_extension: bool,
) -> int:
    """
     Adds codes from the concept to the codeable_concept.

     Parameters:
        concept - ACD concept
        codeable_concept - FHIR codeable concept the codes will be added to
        add_nlp_extension - if true, adds extension indicating the code is derived.

    Returns:
        number of codes added
    """
    codes_added: int = 0

    if add_nlp_extension:
        append = _append_coding_entries_with_extension
    else:
        append = _append_coding_entries

    if hasattr(concept, "cui") and concept.cui is not None:
        # For CUIs, we do not handle comma-delimited values (have not seen that we ever have more than one value)
        # We use the preferred name from UMLS for the display text
        codes_added += append(
            codeable_concept,
            insight_constants.UMLS_URL,
            concept.cui,
            get_concept_display_text(concept),
        )

    if hasattr(concept, "snomed_concept_id") and concept.snomed_concept_id:
        codes_added += append(
            codeable_concept,
            insight_constants.SNOMED_URL,
            concept.snomed_concept_id,
        )

    if hasattr(concept, "nci_code") and concept.nci_code:
        codes_added += append(
            codeable_concept, insight_constants.NCI_URL, concept.nci_code
        )
    if hasattr(concept, "loinc_id") and concept.loinc_id:
        codes_added += append(
            codeable_concept, insight_constants.LOINC_URL, concept.loinc_id
        )
    if hasattr(concept, "mesh_id") and concept.mesh_id:
        codes_added += append(
            codeable_concept, insight_constants.MESH_URL, concept.mesh_id
        )
    if hasattr(concept, "icd9_code") and concept.icd9_code:
        codes_added += append(
            codeable_concept, insight_constants.ICD9_URL, concept.icd9_code
        )
    if hasattr(concept, "icd10_code") and concept.icd10_code:
        codes_added += append(
            codeable_concept, insight_constants.ICD10_URL, concept.icd10_code
        )

    if hasattr(concept, "rx_norm_id") and concept.rx_norm_id:
        codes_added += append(
            codeable_concept, insight_constants.RXNORM_URL, concept.rx_norm_id
        )

    return codes_added
