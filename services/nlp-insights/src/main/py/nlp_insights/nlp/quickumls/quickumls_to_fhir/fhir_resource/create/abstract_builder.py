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
Defines an abstract class to build a new resource from QuickUMLS concepts.

This allows code to be shared when deriving new resource types using QuickUMLS.
The abstract class handles common details such as iterating over relevant attributes,
building insight extensions in the new resource, updating the insight extensions with
new spans, etc.

Concrete classes implement the specific details as to how to create the new resource,
and to set the derived codings from QuickUMLS into the resource.
"""
import abc
from typing import Dict
from typing import Generic
from typing import List
from typing import NamedTuple
from typing import Type
from typing import TypeVar

from fhir.resources.resource import Resource

from nlp_insights.fhir.insight_builder import InsightConfidenceBuilder
from nlp_insights.insight import id_util
from nlp_insights.insight.builder.derived_resource_builder import (
    DerivedResourceInsightBuilder,
)
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.nlp_config import NlpConfig
from nlp_insights.nlp.quickumls.concept_container import (
    QuickUmlsConceptContainer,
    QuickUmlsConcept,
)


class _TrackerEntry(NamedTuple):
    """For a given CUI, this binds the resource being derived to the
    insight containing the evidence.
    """

    resource: Resource
    insight_builder: DerivedResourceInsightBuilder


T = TypeVar("T", bound=Resource)


class ResourceBuilder(abc.ABC, Generic[T]):
    """Base class for building new resources from NLP output

    Generic type "T" is the type of resource that will be constructed.
    This defines a general flow for creating new resources based on QuickUMLS output. Concrete classes
    will implement the abstract methods with resource specific details.
    """

    def __init__(
        self,
        text_source: UnstructuredText,
        concept_container: QuickUmlsConceptContainer,
        nlp_config: NlpConfig,
        resource_type: Type[T],
    ):
        self.text_source = text_source
        self.concept_container = concept_container
        self.nlp_config = nlp_config
        self.resource_type = resource_type

    def build_resources(self) -> List[T]:
        """Returns resources derived by NLP, or empty list if there are no resources

        Building resources consists of iterating over all concepts that are
        relevant to resource type being constructed. For each concept, either a new
        resource is created representing the attribute, or a previously created resource
        that represents the attribute is updated with the information in the new attribute.
        """

        # tracker maps the insight id -> (resource, insight builder)
        # This map is what we use to determine if we've already seen the
        # resource that should go with this concept. The id
        # is computed from (source path & object, cui, resource type) so if we get a
        # duplicate, we can assume this attribute is a new span of the same idea and we
        # should be updating the previously created resource rather than creating a new resource.
        tracker: Dict[str, _TrackerEntry] = {}

        concepts = self.concept_container.get_most_relevant_concepts(self.resource_type)

        for concept in concepts:
            if insight_id := self.compute_insight_id(concept):

                if insight_id not in tracker:
                    # Create a new resource + insight and store in the tracker
                    resource = self.create_resource(concept)
                    insight_builder = DerivedResourceInsightBuilder(
                        resource_type=self.resource_type,
                        text_source=self.text_source,
                        insight_id_value=insight_id,
                        insight_id_system=self.nlp_config.nlp_system,
                        nlp_response_json=self.concept_container.service_resp,
                    )
                    tracker[insight_id] = _TrackerEntry(
                        resource=resource, insight_builder=insight_builder
                    )

                # Retrieve resource and insight extension builder from tracker,
                resource, insight_builder = tracker[insight_id]

                # Update codings
                # This is most likely a no-op for any attributes after the first one
                # that causes the condition to be created. (CUI is the same).
                # Still, we should let ACD decide whether the codes are the same or not
                # between two attributes and not assume.
                self.update_codings(resource, concept)

                # Update insight with span and confidences
                insight_builder.add_span(
                    span=concept.span, confidences=self.get_confidences(concept)
                )

        if not tracker:
            return []

        for resource, insight in tracker.values():
            insight.append_insight_to_resource_meta(resource)
            insight.append_insight_summary_to_resource(resource)

        return [entry.resource for entry in tracker.values()]

    def compute_insight_id(self, concept: QuickUmlsConcept) -> str:
        """Computes an insight ID for the insight

        The insight id must be:
        - deterministic, the same attribute must result in the same id on all invocations
        - unique (for practical purposes) for each (source object & path, cui, resource type)

        The reason for these requirements is so that when an insight has multiple spans in the
        same source text, these attributes are seen as the same insight with multiple spans. The id must also
        ensure that different insights create different resources.
        """

        return id_util.make_hash(self.text_source, concept.cui, self.resource_type)

    @abc.abstractmethod
    def update_codings(self, resource: T, concept: QuickUmlsConcept) -> None:
        """Updates the resource with codings from the concept.

        The method will be called for each concept associated with the insight.
        This method will only add new codings that do not already exist in the resource.

        Args:
            resource - resource to be updated
            concept - concept containing the code
        """
        raise NotImplementedError

    # pylint: disable=no-self-use, unused-argument
    def get_confidences(
        self, concept: QuickUmlsConcept
    ) -> List[InsightConfidenceBuilder]:
        """Retrieves confidences associated with a concept

        This is called each time a span is added to an insight.
        Empty list is returned if there are no confidence scores that
        should be included in the insight.

        The default implementation always returns empty list. The
        'similarity' score that is returned by QuickUMLS has different
        meanings (and values) depending on how the service is configured.
        Enhancing nlp-insights so that we know what that value means and
        assigning a confidence method to it was not MVP. For this reason,
        we did not default to similarity score.

        Args:
        concept - the model data for the insight

        Returns list of confidence builders, or empty list if there are
        no confidence scores.

        """
        return []

    @abc.abstractmethod
    def create_resource(
        self,
        first_concept: QuickUmlsConcept,
    ) -> T:
        """Creates a derived resource.

        This method does the initial creation of the resource.
        The returned resource will not be 'complete', but should be valid.
        Other methods this builder will called on the resource to update codings after
        creation.

        Args:
        first_concept - The concept that caused this resource to be created.
        Returns the new resource
        """
        raise NotImplementedError
