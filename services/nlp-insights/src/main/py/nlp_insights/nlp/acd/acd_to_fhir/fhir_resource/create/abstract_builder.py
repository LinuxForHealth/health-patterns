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
Defines an abstract class to build a new resource from a ACD attribute and source.

This allows code to be shared when deriving new resource types from ACD insights.
The abstract class handles common details such as iterating over relevant attributes,
building insight extensions in the new resource, updating the insight extensions with
new spans, etc.

Concrete classes implement the specific details as to how to create the new resource,
and to set the derived codings from ACD into the resource.
"""
import abc
import json
from typing import Dict
from typing import Generic
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Type
from typing import TypeVar

from fhir.resources.resource import Resource
from ibm_whcs_sdk.annotator_for_clinical_data import ContainerAnnotation
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    InsightModelData,
)

from nlp_insights.fhir.insight_builder import InsightConfidenceBuilder
from nlp_insights.insight import id_util
from nlp_insights.insight.builder.derived_resource_builder import (
    DerivedResourceInsightBuilder,
)
from nlp_insights.insight_source.unstructured_text import UnstructuredText
from nlp_insights.nlp.acd.flows import attribute
from nlp_insights.nlp.nlp_config import AcdNlpConfig


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
    This defines a general flow for creating new resources based on ACD output. Concrete classes
    will implement the abstract methods with resource specific details.
    """

    def __init__(
        self,
        text_source: UnstructuredText,
        acd_output: ContainerAnnotation,
        nlp_config: AcdNlpConfig,
        resource_type: Type[T],
    ):
        self.text_source = text_source
        self.acd_output = acd_output
        self.nlp_config = nlp_config
        self.resource_type = resource_type

    def build_resources(self) -> List[T]:
        """Returns resources derived by NLP, or empty list if there are no resources

        Building resources consists of iterating over all ACD attributes that are
        relevant to resource type being constructed. For each attribute, either a new
        resource is created representing the attribute, or a previously created resource
        that represents the attribute is updated with the information in the new attribute.
        """

        # tracker maps the insight id -> (resource, insight builder)
        # This map is what we use to determine if we've already seen the
        # resource that should go with this ACD attribute. The id
        # is computed from (source path & object, cui, resource type) so if we get a
        # duplicate, we can assume this attribute is a new span of the same idea and we
        # should be updating the previously created resource rather than creating a new resource.
        tracker: Dict[str, _TrackerEntry] = {}

        attrs = attribute.get_attribute_sources(
            self.acd_output,
            self.resource_type,
            self.nlp_config.acd_attribute_source_map,
        )
        for attr in attrs:
            if insight_id := self.compute_insight_id(attr):

                if insight_id not in tracker:
                    # Create a new resource + insight and store in the tracker
                    resource = self.create_resource(attr)
                    insight_builder = DerivedResourceInsightBuilder(
                        resource_type=self.resource_type,
                        text_source=self.text_source,
                        insight_id_value=insight_id,
                        insight_id_system=self.nlp_config.nlp_system,
                        nlp_response_json=json.dumps(self.acd_output.to_dict()),
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
                self.update_codings(resource, attr)

                # Update insight with span and confidence information
                span = attr.get_attribute_span()
                if span:
                    if attr.attr.insight_model_data:
                        confidences = self.get_confidences(attr.attr.insight_model_data)
                    else:
                        confidences = []
                    insight_builder.add_span(span=span, confidences=confidences)

        if not tracker:
            return []

        for resource, insight in tracker.values():
            insight.append_insight_to_resource_meta(resource)
            insight.append_insight_summary_to_resource(resource)

        return [entry.resource for entry in tracker.values()]

    def compute_insight_id(
        self, acd_attr: attribute.AttributeWithSource
    ) -> Optional[str]:
        """Computes an insight ID for the insight

        The insight id must be:
        - deterministic, the same attribute must result in the same id on all invocations
        - unique (for practical purposes) for each (source object & path, cui, resource type)

        The reason for these requirements is so that when an insight has multiple spans in the
        same source text, these attributes are seen as the same insight with multiple spans. The id must also
        ensure that different insights create different resources.

        Will return None if the attribute should not be considered as an insight.
        Returning None should be used for cases where the id cannot be computed, such as for an
        attribute without a CUI.
        """
        if (
            hasattr(acd_attr.best_source.source, "cui")
            and acd_attr.best_source.source.cui
        ):
            return id_util.make_hash(
                self.text_source, acd_attr.best_source.source.cui, self.resource_type
            )

        return None

    @abc.abstractmethod
    def update_codings(
        self, resource: T, acd_attr: attribute.AttributeWithSource
    ) -> None:
        """Updates the resource with codings from the ACD attribute.

        The method will be called for each attribute associated with the insight.
        This method will only add new codings that do not already exist in the resource.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_confidences(
        self, insight_model_data: InsightModelData
    ) -> List[InsightConfidenceBuilder]:
        """Retrieves confidences associated with an InsightModelData

        This is called each time a span is added to an insight.
        Empty list is returned if there are no confidence scores that
        should be included in the insight.

        Args:
        insight_model_data - the model data for the insight

        Returns list of confidence builders, or empty list if there are
        no confidence scores.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_resource(
        self,
        first_acd_attr: attribute.AttributeWithSource,
    ) -> T:
        """Creates a derived resource.

        This method does the initial creation of the resource.
        The returned resource will not be 'complete', but should be valid.
        Other methods this builder will called on the resource to update codings after
        creation.

        Args:
        first_acd_attr - The attribute that caused this resource to be created.
        Returns the new resource
        """
        raise NotImplementedError
