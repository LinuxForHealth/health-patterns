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
Implementation of the discover_insights API
"""

from typing import List
import uuid

from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.resource import Resource

from nlp_insights.app_util import config
from nlp_insights.fhir.create_bundle import BundleEntryDfn
from nlp_insights.fhir.reference import ResourceReference
from nlp_insights.insight_source import concept_text_adjustment
from nlp_insights.insight_source import unstructured_text
from nlp_insights.insight_source.fields_of_interest import (
    get_concepts_for_nlp_analysis,
)


def update_bundle_with_insights(resource: Bundle) -> None:
    """Updates a bundle with new insights

    - Resources in the bundle MAY be modified with additional codings
    - Additional derived resources may be added to the bundle
    - ONLY PUT and POST entries are considered for updates
    """
    if resource.entry:
        new_resources = []
        for entry in resource.entry:
            if isinstance(entry.resource, Bundle):
                # Technically bundles can be nested since a bundle is
                # a resource. In practice, this should not be common
                # https://stackoverflow.com/questions/37579152/nested-fhir-bundles
                update_bundle_with_insights(entry.resource)
            elif (
                entry.resource
                and entry.request
                and entry.request.method
                and entry.request.method in ["PUT", "POST"]
            ):
                assign_full_url(entry)
                reference = ResourceReference[Resource](entry)
                enrich_resource(reference)
                new_resources.extend(derive_new_resources(reference))

        resource.entry.extend(
            [
                derived_resource_entry.to_bundle_entry()
                for derived_resource_entry in new_resources
            ]
        )


def assign_full_url(entry: BundleEntry) -> None:
    """Assigns a UUID to a bundle entry.

    For a POST request, the FHIR spec allows but does not require full url.
    https://www.hl7.org/fhir/bundle.html#bundle-unique

    If not supplied, we'll assign one. This is so that insights can identify
    this resource, even though a FHIR server has not assigned an ID to the
    resource yet.

    A good description of how FHIR deals with references to resources created in
    the bundle can be found here:
    https://cloud.google.com/healthcare-api/docs/how-tos/fhir-bundles#resolving_references_to_resources_created_in_a_bundle

    """
    if entry.request.method == "POST" and not entry.fullUrl:
        entry.fullUrl = uuid.uuid4().urn


def enrich_resource(resource_ref: ResourceReference[Resource]) -> int:
    """Possibly enrich a resource

    Args: resource to enrich, must not be a bundle
    Returns: the number of codings that were added to the resource
    """
    if resource_ref.down_cast(Bundle):
        raise ValueError("Cannot enrich a bundle")

    nlp = config.get_nlp_service_for_resource(resource_ref.resource)
    concepts_to_enrich = get_concepts_for_nlp_analysis(resource_ref)
    if concepts_to_enrich:
        return nlp.enrich_codeable_concepts(
            concept_refs=[
                concept_text_adjustment.adjust_concept_text(concept)
                for concept in concepts_to_enrich
            ],
        )

    return 0


def derive_new_resources(
    resource_ref: ResourceReference[Resource],
) -> List[BundleEntryDfn]:
    """Derive new resources from a resource

    Args: resource to derive new resources from, must not be a bundle
    Returns: List (possibly empty) of derived resources
    """
    if resource_ref.down_cast(Bundle):
        raise ValueError("Cannot derive new resources from a bundle")

    nlp = config.get_nlp_service_for_resource(resource_ref.resource)
    new_resources = []

    text_for_new_resources: List[
        unstructured_text.UnstructuredText
    ] = unstructured_text.get_unstructured_text(resource_ref)

    if text_for_new_resources:
        new_resources.extend(nlp.derive_new_resources(text_for_new_resources))

    return new_resources
