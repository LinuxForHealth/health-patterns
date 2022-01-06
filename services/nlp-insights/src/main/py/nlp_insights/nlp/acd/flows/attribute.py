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
"""Utilities to find the object that is the source of the attribute of interest.  The source contains information
about the CUI for the attribute, as well as other "low-level" information.

This has the functionality to decide what is an attribute of interest in an ACD response, and also
how to find the source for that attribute. There is always a single source CUI object for an attribute, and
that object is where most of the coding information and extensions come from.

Although nlp-inisghts supports only a single flow, in the future different flows may
define different attributes of interest. Additional flows might be necessary when/if the
ACD pipeline is customized so that it returns additional attributes that are of interest
to nlp-insights.

The source may be stored within different properties of the container for different flows,
it can be a number of different types, depending on the attribute.
Each of these types has similar properties.

A SourceSearchMap determines which attributes to use and where to look for source CUI objects.

"""
# The context of an NLP request is either a Resource that is being created,
# or a type of codeableConcept that is being enriched.
from enum import Enum
import logging
from typing import Dict
from typing import Generator
from typing import List, Set
from typing import NamedTuple
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union
from typing import cast

from fhir.resources.resource import Resource
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from nlp_insights.insight.span import Span
from nlp_insights.insight_source.fields_of_interest import CodeableConceptRefType


AnnotationContextType = Union[Type[Resource], CodeableConceptRefType]

# This represents the data types that a source object/concept may be
AttrSourceConcept = Union[
    acd.Concept,
    acd.SymptomDisease,
    acd.MedicationAnnotation,
]


class AttrSourcePropName(Enum):
    """Possible values for fields in an acd response that may contain the source CUI"""

    CONCEPTS = "concepts"
    SYMPTOM_DISEASE_IND = "symptom_disease_ind"
    MEDICATION_IND = "medication_ind"


class AcdAttrSourceDfn(NamedTuple):
    """Binds an attribute name/type to the field(s) containing the source Objects

    attr_name - attribute names with relevant associated concepts
                May also be a collection of valid names
    source_prop_names: Properties in the container annotation to search for source
                       associated with the attribute name.
    concept_types: if not None, resulting concepts are filtered by this value.
    """

    attr_name: Union[str, Set[str]]
    source_prop_names: List[AttrSourcePropName]


class AnnotationContext(NamedTuple):
    """Definition of how to search for source cuis

    Attributes matching attributes in the attribute_mapping will be
    used to locate sources in the specified section of the response.
    """

    attribute_mapping: List[AcdAttrSourceDfn]


SourceSearchMap = Dict[AnnotationContextType, AnnotationContext]

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AttributeSource(NamedTuple):
    """Representation of the source information for an attribute

    location - description of where the source was found
    source  - the cource object, which could be different
              data types depending on the attribute and concept.
    """

    location: AttrSourcePropName
    source: AttrSourceConcept

    def source_as(self, clazz: Type[T]) -> T:
        """Returns the source, casted to the specified type

        If the source is not of the specified type,
        raises ValueError
        """
        if not isinstance(self.source, clazz):
            raise ValueError(f"source must be a {clazz.__name__}")
        return cast(T, self.source)


class AttributeWithSource(NamedTuple):
    """Binds an attribute with it's source CUIS

    attr attribute annotation

    sources: source of the attribute
    """

    attr: acd.AttributeValueAnnotation
    best_source: AttributeSource

    def get_attribute_span(self) -> Optional[Span]:
        """Returns the attribute span.

        ACD doc states that the span is optional,
        a None result is possible.
        """

        if (
            self.attr.begin is not None
            and self.attr.end is not None
            and self.attr.covered_text is not None
        ):
            return Span(
                begin=self.attr.begin,
                end=self.attr.end,
                covered_text=self.attr.covered_text,
            )

        return None


def _create_attribute_with_source(
    attr: acd.AttributeValueAnnotation,
    container: acd.ContainerAnnotation,
    source_prop_names: List[AttrSourcePropName],
) -> Optional[AttributeWithSource]:
    """For the given attribute value annotation, find the source for the annotation.

    Args: attr - the attribute value annotation
          container - the complete response
          source_prop_names - properties in the container to look for the cuis
    Returns: attribute with source, if a source was found, else None
    """
    uid = attr.concept.uid

    for prop_name in source_prop_names:
        if hasattr(container, prop_name.value) and getattr(container, prop_name.value):
            for source in getattr(container, prop_name.value):
                if hasattr(source, "uid") and getattr(source, "uid") == uid:
                    # The first source found using the order defined by the list
                    # is the best one
                    return AttributeWithSource(
                        attr=attr,
                        best_source=AttributeSource(location=prop_name, source=source),
                    )

    return None


def get_attribute_sources(
    container: acd.ContainerAnnotation,
    context: AnnotationContextType,
    search_map: SourceSearchMap,
) -> Generator[AttributeWithSource, None, None]:
    """Generator to filter attributes by name of attribute

       Returned attributes include source information.
       Only one source object per attribute per location is returned.

    Args:
       container - the acd nlp response
       context   - either the resource being created or concept type being enriched
       search_map - definition for how to find sources
    """
    if not container.attribute_values:
        return

    attribute_values: List[acd.AttributeValueAnnotation] = container.attribute_values
    annotation_context = search_map.get(context, None)
    if not annotation_context:  # Is a mapping even defined?
        return

    if annotation_context.attribute_mapping:
        for attr in attribute_values:
            for loc in annotation_context.attribute_mapping:
                if (isinstance(loc.attr_name, str) and attr.name == loc.attr_name) or (
                    isinstance(loc.attr_name, set) and (attr.name in loc.attr_name)
                ):
                    source = _create_attribute_with_source(
                        attr, container, loc.source_prop_names
                    )
                    if source:
                        yield source
