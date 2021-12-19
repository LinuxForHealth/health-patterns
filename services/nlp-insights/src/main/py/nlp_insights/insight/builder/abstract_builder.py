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
Defines a base class for building insights specific to nlp-insights

Classes inheriting from this class build insights that use a specialized
version of the alveraie insight model. For example they might be designed
such that an insight has only a single details extension, and/or a single
results section per details.

The base class provides utility methods for assing the insight extensions
to the resource's meta, or adding summary extensions to resources or elements
or resources.

"""
from typing import Iterator
from typing import Optional
from typing import Union

from fhir.resources.element import Element
from fhir.resources.extension import Extension
from fhir.resources.meta import Meta
from fhir.resources.resource import Resource

from nlp_insights.fhir import alvearie_ext
from nlp_insights.fhir import alvearie_ext_url
from nlp_insights.fhir.insight_builder import InsightBuilder


def _has_matching_insight_id_extension(
    ext: Extension, id_system: str, id_value: str
) -> Optional[Extension]:
    """Finds an insight Id extension matching the system and id within an enclosing extension"""
    if not ext.extension:
        return None

    ident = next(
        filter(
            lambda candidate: candidate
            and candidate.url
            and (candidate.url == alvearie_ext_url.INSIGHT_ID_URL),
            ext.extension,
        ),
        None,
    )

    return (
        ident
        and ident.valueIdentifier.system == id_system
        and ident.valueIdentifier.value == id_value
    )


def find_all_summary_extensions(
    root: Union[Element, Extension, Resource]
) -> Iterator[Extension]:
    """Yields all summary extensions in root.extension"""
    if not root.extension:
        return iter([])

    return filter(
        lambda ext: (
            ext and ext.url and (ext.url == alvearie_ext_url.INSIGHT_SUMMARY_URL)
        ),
        root.extension,
    )


class ResourceInsightBuilder:
    """ "
    Base class for building insights specific to nlp-insights
    """

    # Subclass must define
    _builder: InsightBuilder

    @property
    def builder(self) -> InsightBuilder:
        """Returns the builder object, which the subclass must declare"""
        try:
            return self._builder
        except AttributeError as ex:
            raise NotImplementedError("Subclass must define a builder!") from ex

    def append_insight_to_resource_meta(self, resource: Resource) -> None:
        """Builds the insight extension and adds it to the resource's meta"""

        insight_extension = self.builder.build_extension()
        if resource.meta is None:
            resource.meta = Meta.construct()

        if resource.meta.extension is None:
            resource.meta.extension = []

        existing_insight = self._find_insight_extension_idx(resource.meta)
        if existing_insight is not None:
            resource.meta.extension[existing_insight] = insight_extension
        else:
            resource.meta.extension.append(insight_extension)

    def find_summary_extension(
        self, root: Union[Element, Extension, Resource]
    ) -> Optional[Extension]:
        """Searches for an existing summary extension for the insight"""
        return next(
            filter(
                lambda summary_ext: _has_matching_insight_id_extension(
                    summary_ext,
                    self.builder.identifier.system,
                    self.builder.identifier.value,
                ),
                find_all_summary_extensions(root),
            ),
            None,
        )

    def _find_insight_extension_idx(self, meta: Meta) -> Optional[int]:
        """Returns the index of the insight's extension in the meta, or None
        if the insight has not been added to the resource meta
        """
        if meta.extension is None:
            return None

        for idx, ext in enumerate(meta.extension):
            if ext.url == alvearie_ext_url.INSIGHT_URL and (
                self.find_summary_extension(ext) is not None
            ):
                return idx

        return None

    def append_summary_extension(
        self, element: Union[Element, Extension, Resource]
    ) -> None:
        """Appends a summary extension for the insight"""
        if element.extension is None:
            element.extension = []

        element.extension.append(
            alvearie_ext.create_insight_summary_extension(
                insight_id_extension=self.builder.identifier.build_extension(),
                category_extension=alvearie_ext.create_derived_by_nlp_category_extension(),
            )
        )
