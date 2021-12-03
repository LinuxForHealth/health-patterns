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
"""Defines abstract base class for an NLP service"""

from abc import ABC, abstractmethod
import json
from typing import Any
from typing import Dict
from typing import List

from fhir.resources.resource import Resource

from nlp_insights.fhir.create_bundle import BundleEntryDfn
from nlp_insights.insight_source.concept_text_adjustment import AdjustedConceptRef
from nlp_insights.insight_source.unstructured_text import UnstructuredText


class NLPServiceError(Exception):
    """Raised when an NLP Service API Call fails

    description should be suitable for external parties to view without
    security concerns as this value may be returned in a REST response.
    """

    def __init__(self, description: str):
        super().__init__()
        self.description = description


class NLPService(ABC):
    """Base NLP service

    An NLP service has two basic functions:
    - Given unstructured text, derive new resources
    - Given a reference to a concept (possibly with adjusted text for context), use the
      text to derive additional codings.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.json_string = json.dumps(config)
        self.config_name: str = config.get("name", self.__class__.__name__)

    @abstractmethod
    def derive_new_resources(
        self, notes: List[UnstructuredText]
    ) -> List[BundleEntryDfn]:
        """Invokes NLP on the unstructured text elements and derives new FHIR resources

        Args:
            notes: list of unstructured text objects to derive new resources. There is no requirement
            that all objects originated from the same source FHIR resource.
        Returns:
            list of bundle definition for the new resources

        Raises NLPServiceError
        """

    @abstractmethod
    def enrich_codeable_concepts(
        self, resource: Resource, concept_refs: List[AdjustedConceptRef]
    ) -> int:
        """Invokes NLP each concept's text, updates the concept's FHIR resource with derived codings

        The resource's meta is updated with insight detail. The insight id uses a starting value, and
        is incremented as insights are added. This means that additional care may be required to set the
        initial insight id, if another call to this method is used to derive other concepts for the same FHIR resource.
        As of 10/07/2021 there is no need for this feature since all concepts for the resource are provided in a
        single call.

        Args: resource - the resource containing the codeable concepts to derive new codings for
              concept_refs - the codeable concepts to derive new codings for (within resource)
        Returns: number of insights appended to the FHIR resource

        Raises NLPServiceError
        """
