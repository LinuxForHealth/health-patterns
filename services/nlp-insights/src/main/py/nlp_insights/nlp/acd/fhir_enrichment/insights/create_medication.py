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

import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import cast

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.reference import Reference
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from nlp_insights.fhir import fhir_object_utils
from nlp_insights.fhir.code_system import hl7
from nlp_insights.insight import id_util
from nlp_insights.insight.builder.derived_resource_builder import (
    DerivedResourceInsightBuilder,
)
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.fhir_enrichment.insights import attribute
from nlp_insights.nlp.acd.fhir_enrichment.insights import confidence
from nlp_insights.nlp.nlp_config import AcdNlpConfig


logger = logging.getLogger(__name__)


class TrackerEntry(NamedTuple):
    """For a given CUI, this binds the resource being derived to the
    insight containing the evidence.
    """

    resource: MedicationStatement
    insight_builder: DerivedResourceInsightBuilder


def create_med_statements(
    text_source: UnstructuredText,
    acd_output: acd.ContainerAnnotation,
    nlp_config: AcdNlpConfig,
) -> Optional[List[MedicationStatement]]:
    """Creates medication statements, given acd data from the text source

    Args:
        text_source - the resource that NLP was run over (must be unstructured)
        acd_output - the acd output
        nlp_config - the configuration to use

    Returns medication statements derived from NLP, or None if there are no such statements
    """
    source_loc_map = nlp_config.acd_attribute_source_map

    # Tracks the medications that have been created for a cui
    # If ACD produces multiple insights for the same CUI, we want to reuse the
    # same insight (with an additional span).
    # The key is the insight id value, which is a hash of the source of the
    # insight combined with the causing the new resource to be
    # created, plus the new resource type.
    # This creates a globally unique id value that will be the same
    # for multiple occurrences of the same derived concept.
    med_statement_tracker: Dict[str, TrackerEntry] = {}

    for attr in attribute.get_attribute_sources(
        acd_output, MedicationStatement, source_loc_map
    ):
        # only know how to handle the medication annotation at this time
        if not isinstance(attr.best_source.source, acd.MedicationAnnotation):
            raise NotImplementedError(
                "Only support MedicationAnnotation CUI source at this time"
            )

        med_ind: acd.MedicationAnnotation = cast(
            acd.MedicationAnnotation, attr.best_source.source
        )

        if med_ind.cui:
            key = id_util.make_hash(text_source, med_ind.cui, MedicationStatement)
            if key not in med_statement_tracker:
                # Create a new medication statement + insight and store in tracker
                med_stmt = _create_minimum_medication_statement(
                    text_source.source_resource.subject, med_ind
                )
                insight_builder = DerivedResourceInsightBuilder(
                    resource_type=MedicationStatement,
                    text_source=text_source,
                    insight_id_value=key,
                    insight_id_system=nlp_config.nlp_system,
                    nlp_response_json=json.dumps(acd_output.to_dict()),
                )

                med_statement_tracker[key] = TrackerEntry(
                    resource=med_stmt,
                    insight_builder=insight_builder,
                )

            # retrieve medication statement + insight
            med_statement, insight_builder = med_statement_tracker[key]

            # Update codings
            _update_codings(med_statement, med_ind)

            # Update Insight span
            span = attr.get_attribute_span()
            if span:
                confidences = []
                if attr.attr.insight_model_data:
                    confidences = confidence.get_derived_medication_confidences(
                        attr.attr.insight_model_data
                    )
                insight_builder.add_span(span=span, confidences=confidences)

    if not med_statement_tracker:
        return None

    for medication, builder in med_statement_tracker.values():
        builder.append_insight_to_resource_meta(medication)
        builder.append_insight_summary_to_resource(medication)

    return [entry.resource for entry in med_statement_tracker.values()]


def _create_minimum_medication_statement(
    subject: Reference,
    annotation: acd.MedicationAnnotation,
) -> MedicationStatement:
    """Creates a new medication statement, with minimum fields set

    The object is created with a status of 'unknown' and a
    medicationCodeableConcept with text set based on the
    drug information in the provided annotation.

    Args:
        subject: The subject of the medication statement
        annotation - the annotation to use to set the codeable concept

    Returns the new medication statement
    """
    acd_drug = _get_drug_from_annotation(annotation)

    codeable_concept = CodeableConcept.construct()

    codeable_concept.text = acd_drug.get("drugSurfaceForm")
    codeable_concept.coding = []

    return MedicationStatement.construct(
        subject=subject, medicationCodeableConcept=codeable_concept, status="unknown"
    )


def _get_drug_from_annotation(annotation: acd.MedicationAnnotation) -> dict:
    """Returns a dictionary of drug information

    Args:
       annotation - the ACD annotation to get the drug info from

    Return a dictionary
    """
    try:
        return cast(dict, annotation.drug[0].get("name1")[0])
    except (TypeError, IndexError, AttributeError):
        logger.exception(
            "Unable to retrieve drug information for attribute %s",
            annotation.json(indent=2),
        )
        return {}


def _update_codings(  # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    med_statement: MedicationStatement, annotation: acd.MedicationAnnotation
) -> None:
    """
    Update the medication statement with the drug information from the ACD annotation
    """
    acd_drug = _get_drug_from_annotation(annotation)

    _add_codings_drug(acd_drug, med_statement.medicationCodeableConcept)


def _add_codings_drug(
    acd_drug: Dict[Any, Any], codeable_concept: CodeableConcept
) -> None:
    """Add codes from the drug concept to the codeable_concept.

    To be used for resources created from insights - does not add an extension indicating the code is derived.
    Parameters:
        acd_drug - ACD concept for the drug
        codeable_concept - FHIR codeable concept the codes will be added to
    """
    if acd_drug.get("cui") is not None:
        # For CUIs, we do not handle comma-delimited values (have not seen that we ever have more than one value)
        fhir_object_utils.append_coding(
            codeable_concept,
            hl7.UMLS_URL,
            acd_drug["cui"],
            acd_drug.get("drugSurfaceForm"),
        )

    if "rxNormID" in acd_drug:
        for code_id in acd_drug["rxNormID"].split(","):
            fhir_object_utils.append_coding(codeable_concept, hl7.RXNORM_URL, code_id)
