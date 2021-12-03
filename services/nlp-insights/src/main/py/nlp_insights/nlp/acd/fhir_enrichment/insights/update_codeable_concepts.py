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
"""Functions to update codeable concepts with derived codings"""

import logging
from typing import Generator
from typing import List
from typing import NamedTuple

from fhir.resources.resource import Resource
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from nlp_insights.fhir import fhir_object_utils
from nlp_insights.insight.insight_id import insight_id_maker
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.nlp.acd.fhir_enrichment.insights.append_codings import (
    append_codings,
)
from nlp_insights.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    get_attribute_sources,
    AttrSourceConcept,
)

from nlp_insights.nlp.nlp_config import AcdNlpConfig


logger = logging.getLogger(__name__)


class AcdConceptRef(NamedTuple):
    """Binding between reference to a codeable concept with adjusted text, and an ACD NLP Response"""

    adjusted_concept: AdjustedConceptRef
    acd_response: acd.ContainerAnnotation


def _add_codeable_concept_insight(
    fhir_resource: Resource,
    insight: AcdConceptRef,
    id_maker: Generator[str, None, None],
    nlp_config: AcdNlpConfig,
) -> int:
    """Updates a codeable concept and resource meta with ACD insights.

    The codeable concept referenced by the insight is updated with codings that were
    derived from the text.

    The meta extension for the supplied resource is updated with the insight id and
    reference path.

    Args:
        fhir_resource - the resource to update the meta with the new insight
        insight - binding between the concept text that was analyzed by ACD-NLP and the
                  ACD response for that analysis.
        id_maker - generator for producing ids for insights
        nlp_config - nlp configuration

    Returns: the number of codings added to the codeable concept.
    """
    concept_ref = insight.adjusted_concept.concept_ref
    source_loc_map = nlp_config.acd_attribute_source_map

    total_num_codes_added: int = 0

    for cui_source in get_attribute_sources(
        insight.acd_response, concept_ref.type, source_loc_map
    ):

        if cui_source.sources:
            # First available source is the best one
            source: AttrSourceConcept = next(iter(cui_source.sources.values()))
            logger.debug("Appending codings from %s", source)

            num_codes_appended: int = append_codings(
                source, concept_ref.code_ref, add_nlp_extension=True
            )

            if num_codes_appended > 0:
                logger.debug(
                    "Adding new insight to meta because %s codes were appended",
                    num_codes_appended,
                )
                total_num_codes_added += num_codes_appended
                fhir_object_utils.append_insight_with_path_expr_to_resource_meta(
                    fhir_resource=fhir_resource,
                    insight_id=next(id_maker),
                    system=nlp_config.nlp_system,
                    fhir_path=insight.adjusted_concept.concept_ref.fhir_path,
                    nlp_output_uri=nlp_config.get_nlp_output_loc(insight.acd_response),
                )

    return total_num_codes_added


def update_codeable_concepts_and_meta_with_insights(
    fhir_resource: Resource,
    concept_insights: List[AcdConceptRef],
    nlp_config: AcdNlpConfig,
) -> int:
    """Updates the resource with derived insights

    Each element in concept insights contains a reference a codeable concept within the resource to
    enrich, as well as the adjusted text and ACD response for the NLP.

    The codings are updated with additional codings derived by ACD.
    The meta of the FHIR resource is updated with the insight details extension.

    Args:
        fhir_resource - the fhir resource to update the meta
        concept_insights - collection of concepts to enrich with insights.
                           These concepts should be contained within the FHIR resource.
        nlp_config - NLP configuration

    Returns: total number of derived codings added to the resource, across all provided
             codeable concepts.
    """
    id_maker = insight_id_maker(start=nlp_config.insight_id_start)

    num_codes_added: int = 0

    for concept_insight in concept_insights:
        num_codes_added += _add_codeable_concept_insight(
            fhir_resource, concept_insight, id_maker, nlp_config
        )

    return num_codes_added
