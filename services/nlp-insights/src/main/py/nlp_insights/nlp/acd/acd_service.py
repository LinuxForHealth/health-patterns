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
"""
Defines how to derive insights using ACD (IBM Watson Annotator for Clinical Data) for NLP functions

The formal documentation for the ACD service can be found at: https://cloud.ibm.com/apidocs/wh-acd

"""
import logging
from typing import Dict, Any
from typing import List

from fhir.resources.resource import Resource
import ibm_cloud_sdk_core
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)
from requests.exceptions import RequestException

from nlp_insights.fhir.create_bundle import BundleEntryDfn
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.abstract_nlp_service import NLPService, NLPServiceError
from nlp_insights.nlp.acd.acd_to_fhir.fhir_resource.create.create_condition import (
    ConditionBuilder,
)
from nlp_insights.nlp.acd.acd_to_fhir.fhir_resource.create.create_medication import (
    MedicationStatementBuilder,
)

from nlp_insights.nlp.acd.acd_to_fhir.fhir_resource.update.update_codeable_concepts import (
    update_codeable_concepts_and_meta_with_insights,
    AcdConceptRef,
)
from nlp_insights.nlp.nlp_config import ACD_NLP_CONFIG_STANDARD_V1_0


logger = logging.getLogger(__name__)


class ACDService(NLPService):
    """The ACD NLPService uses ACD to derive insights"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initializes the ACD service from a json configuration string"""
        super().__init__(config)
        self.acd_key = config["config"]["apikey"]
        self.acd_url = config["config"]["endpoint"]
        self.acd_flow = config["config"]["flow"]
        self.nlp_config = ACD_NLP_CONFIG_STANDARD_V1_0
        if config.get("version"):
            self.version = config.get("version")
        else:
            self.version = "2021-01-01"

    def _run_nlp(self, text: str) -> acd.ContainerAnnotation:
        """Sends text to NLP service and returns the output"""
        try:
            service = acd.AnnotatorForClinicalDataV1(
                authenticator=IAMAuthenticator(apikey=self.acd_key),
                version=self.version,
            )
            service.set_service_url(self.acd_url)
            logger.info("Calling ACD-%s with text %s", self.config_name, text)
            resp = service.analyze_with_flow(self.acd_flow, text)
            return resp
        except ibm_cloud_sdk_core.api_exception.ApiException as ex:
            raise NLPServiceError(
                description=f"NLP using config {self.config_name} "
                f"failed with error {ex.message}"
            ) from ex
        except RequestException as ex:
            raise NLPServiceError(
                description=f"NLP using config {self.config_name} "
                f"failed with an error {type(ex).__name__}"
            ) from ex

    def derive_new_resources(
        self, notes: List[UnstructuredText]
    ) -> List[BundleEntryDfn]:

        new_resources: List[Resource] = []

        for note in notes:
            container = self._run_nlp(note.text)

            new_resources.extend(
                ConditionBuilder(note, container, self.nlp_config).build_resources()
            )

            new_resources.extend(
                MedicationStatementBuilder(
                    note, container, self.nlp_config
                ).build_resources()
            )

        return [
            BundleEntryDfn(resource=resource, method="POST", url=resource.resource_type)
            for resource in new_resources
        ]

    def enrich_codeable_concepts(
        self, resource: Resource, concept_refs: List[AdjustedConceptRef]
    ) -> int:

        nlp_responses = [
            AcdConceptRef(concept_ref, self._run_nlp(concept_ref.adjusted_text))
            for concept_ref in concept_refs
        ]

        return update_codeable_concepts_and_meta_with_insights(
            nlp_responses, self.nlp_config
        )
