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

from collections import namedtuple
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import cast

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.dosage import Dosage, DosageDoseAndRate
from fhir.resources.extension import Extension
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.timing import Timing
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    InsightModelData,
)

from nlp_insights.fhir.alvearie_ig import (
    create_derived_from_unstructured_insight_detail_extension,
    create_insight_id_extension,
    create_confidence_extension,
    create_coding,
)
from nlp_insights.fhir.fhir_object_utils import (
    add_insight_to_meta,
    append_derived_by_nlp_extension,
    append_coding,
)
from nlp_insights.insight import insight_constants
from nlp_insights.insight.insight_id import insight_id_maker
from nlp_insights.insight.span import Span
from nlp_insights.insight.text_fragment import TextFragment
from nlp_insights.insight.util.medication import parse_dosage_with_units
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    get_attribute_sources,
    AttrSourceConcept,
)
from nlp_insights.nlp.nlp_config import AcdNlpConfig


logger = logging.getLogger(__name__)


def create_med_statements_from_insights(
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

    TrackerEntry = namedtuple("TrackerEntry", ["fhir_resource", "id_maker"])
    med_statement_tracker = {}  # key is UMLS ID, value is TrackerEntry

    for cui_source in get_attribute_sources(
        acd_output, MedicationStatement, source_loc_map
    ):
        if cui_source.sources:
            # some attributes have the cui in multiple places, if so
            # the first available source is the best one
            source: AttrSourceConcept = next(iter(cui_source.sources.values()))

            # only know how to handle the medication annotation at this time
            if not isinstance(source, acd.MedicationAnnotation):
                raise NotImplementedError(
                    "Only support MedicationAnnotation CUI source at this time"
                )

            med_ind: acd.MedicationAnnotation = cast(acd.MedicationAnnotation, source)

            if med_ind.cui not in med_statement_tracker:
                med_statement_tracker[med_ind.cui] = TrackerEntry(
                    fhir_resource=_create_minimum_medication_statement(
                        text_source.source_resource.subject, med_ind
                    ),
                    id_maker=insight_id_maker(start=nlp_config.insight_id_start),
                )

            med_statement, id_maker = med_statement_tracker[med_ind.cui]

            _add_insight_to_medication_statement(
                text_source,
                med_statement,
                cui_source.attr,
                med_ind,
                acd_output,
                next(id_maker),
                nlp_config,
            )
        else:
            logger.info(
                "Did not add codings because the attribute did not have an associated medication annotation %s",
                cui_source,
            )

    if not med_statement_tracker:
        return None

    med_statements = [
        trackedStmt.fhir_resource for trackedStmt in med_statement_tracker.values()
    ]
    for med_statement in med_statements:
        append_derived_by_nlp_extension(med_statement)

    return med_statements


def _add_insight_to_medication_statement(  # pylint: disable=too-many-arguments
    text_source: UnstructuredText,
    med_statement: MedicationStatement,
    attr: acd.AttributeValueAnnotation,
    med_ind: acd.MedicationAnnotation,
    acd_output: acd.ContainerAnnotation,
    insight_id_string: str,
    nlp_config: AcdNlpConfig,
) -> None:
    """Adds insight data to the medication statement"""

    insight_id_ext = create_insight_id_extension(
        insight_id_string, nlp_config.nlp_system
    )

    source = TextFragment(
        text_source=text_source,
        text_span=Span(begin=attr.begin, end=attr.end, covered_text=attr.covered_text),
    )

    if attr.insight_model_data:
        confidences = get_medication_confidences(attr.insight_model_data)
    else:
        confidences = None

    nlp_output_ext = nlp_config.create_nlp_output_extension(acd_output)

    unstructured_insight_detail = (
        create_derived_from_unstructured_insight_detail_extension(
            source=source,
            confidences=confidences,
            evaluated_output_ext=nlp_output_ext,
        )
    )

    add_insight_to_meta(med_statement, insight_id_ext, unstructured_insight_detail)

    _update_codings_and_administration_info(med_statement, med_ind)


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


def _update_codings_and_administration_info(  # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    med_statement: MedicationStatement, annotation: acd.MedicationAnnotation
) -> None:
    """
    Update the medication statement with the drug information from the ACD annotation
    """
    acd_drug = _get_drug_from_annotation(annotation)

    _add_codings_drug(acd_drug, med_statement.medicationCodeableConcept)

    if hasattr(annotation, "administration"):
        # Dosage
        dose_with_units = annotation.administration[0].get("dosageValue")
        if dose_with_units:
            dose = Dosage.construct()
            dose_rate = DosageDoseAndRate.construct()
            med_dosage = parse_dosage_with_units(dose_with_units)

            if med_dosage:
                dose_quantity = Quantity.construct()
                dose_quantity.value = med_dosage.dosage
                if med_dosage.units:
                    dose_quantity.unit = med_dosage.units
                dose_rate.doseQuantity = dose_quantity
                dose.doseAndRate = [dose_rate]

            if med_statement.dosage is None:
                med_statement.dosage = []
            med_statement.dosage.append(dose)

            # medication timing
            frequency = annotation.administration[0].get("frequencyValue")
            if frequency is not None:
                code = None
                display = None

                if frequency in ["Q AM", "Q AM.", "AM"]:
                    code = "AM"
                    display = "AM"
                elif frequency in ["Q PM", "Q PM.", "PM"]:
                    code = "PM"
                    display = "PM"

                if code is not None and display is not None:
                    timing = Timing.construct()
                    timing_codeable_concept = CodeableConcept.construct()
                    timing_codeable_concept.coding = [
                        create_coding(insight_constants.TIMING_URL, code, display)
                    ]
                    timing_codeable_concept.text = frequency
                    timing.code = timing_codeable_concept
                    dose.timing = timing


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
        append_coding(
            codeable_concept,
            insight_constants.UMLS_URL,
            acd_drug["cui"],
            acd_drug.get("drugSurfaceForm"),
        )

    if "rxNormID" in acd_drug:
        for code_id in acd_drug["rxNormID"].split(","):
            append_coding(codeable_concept, insight_constants.RXNORM_URL, code_id)


def get_medication_confidences(
    insight_model_data: InsightModelData,
) -> Optional[List[Extension]]:
    """Returns a list of confidence extensions

    The list is suitable to be added to the insight span extensions array.
     Args:
        insight_model_data - model data for the insight

     Returns:
        collection of confidence extensions, or None if no confidence info was available
    """
    confidence_list = []

    try:
        confidence_list.append(
            create_confidence_extension(
                insight_constants.CONFIDENCE_SCORE_MEDICATION_TAKEN,
                insight_model_data.medication.usage.taken_score,
            )
        )
    except AttributeError:
        pass

    try:
        confidence_list.append(
            create_confidence_extension(
                insight_constants.CONFIDENCE_SCORE_MEDICATION_CONSIDERING,
                insight_model_data.medication.usage.considering_score,
            )
        )
    except AttributeError:
        pass

    try:
        confidence_list.append(
            create_confidence_extension(
                insight_constants.CONFIDENCE_SCORE_MEDICATION_DISCUSSED,
                insight_model_data.medication.usage.discussed_score,
            )
        )
    except AttributeError:
        pass

    try:
        confidence_list.append(
            create_confidence_extension(
                insight_constants.CONFIDENCE_SCORE_MEDICATION_MEASUREMENT,
                insight_model_data.medication.usage.lab_measurement_score,
            )
        )
    except AttributeError:
        pass

    return confidence_list if confidence_list else None
