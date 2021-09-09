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
"""Utilities to find the object that contains the CUI that is the source of an attribute of interest.

This has the functionality to decide what is an attribute of interest in an ACD response, and also
how to find the source CUI for the attribute. There is always a single source CUI object for an attribute, and
that object is where most of the coding information and extensions come from.

Different flows may have different attributes of interest for an NLP request.
The object for the source CUI could be a number of types with similar structure and information.
In addition, the object may be stored within different properties of the container for different flows.

An AttributeNameAndSourceMap determines which attributes to use and where to look for source CUI objects.

"""
from collections import OrderedDict
from collections import defaultdict
from enum import Enum
import logging
from typing import DefaultDict
from typing import Dict, Type
from typing import Generator
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Union

from fhir.resources.resource import Resource
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from text_analytics.insight_source.fields_of_interest import CodeableConceptRefType

# The context of an NLP request is either a Resource that is being created,
# or a type of codeableConcept that is being enriched.
AnnotationContextType = Union[Type[Resource], CodeableConceptRefType]

# This represents the data types that a source CUI object/concept may be
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


class AcdAttrSourceLoc(NamedTuple):
    """Binds an attribute name/type to the fields to search for the source CUI(s)

    attr_name - attribute names with relevant associated concepts
               may be None if umls types should be used to find concepts instead
               of attributes.
    source_prop_names: Properties in the container annotation to search for concepts
                       associated with the attribute name.
    concept_types: if not None, resulting concepts are filtered by this value.
    """

    attr_name: Optional[str]
    source_prop_names: List[AttrSourcePropName]
    concept_types: Optional[List[str]] = None


# Instances of this type tell the engine which attribute to look at, and where
# to look for the source CUI.
# For example: Consider the dictionary entry:
# MedicationStatement : [AcdAttrSourceLoc(attr_name="PrescribedMedication",
#                                         source_prop_names=[AttrSourcePropName.MEDICATION_IND)]
#
# The above says that when processing NLP to create a medication statement, look at the
# 'PrescribeMedication' annotations, and find the associated CUI object in the MedicationInd section
# of the container.
# The concept is identified by matching the uid of the attribute's concept with the uid of
# the concept in the Medication_Ind section.
#
# In some cases an attribute may not be defined, in that case, the relevant concepts can be located
# like this:
# CodeableConceptRefType.VACCINE : [AcdAttrSourceLoc(
#                                                 attr_name=None,
#                                                 source_prop_names=[AttrSourcePropName.CONCEPTS],
#                                                 concept_types=VACCINE_TYPES,
#                                   )]
# In the above case, there is no attribute name to match. All concepts with distinct cuis
# in the specified section that match the provided types will be returned.
#
AttributeNameAndSourceMap = Dict[AnnotationContextType, List[AcdAttrSourceLoc]]


logger = logging.getLogger(__name__)


class AttributeWithCuiSources(NamedTuple):
    """Binds an attribute with it's source CUIS

    attr may be None if the attribute was found by
         searching umls types instead of an attribute

    sources: Mapping of property -> source CUI object
             If multiple parts of the document have
             a CUI for the attribute, this may have multiple
             entries. The first entry is the highest priority
             one and usually the one to use.
    """

    attr: Optional[acd.AttributeValueAnnotation]
    sources: OrderedDict[AttrSourcePropName, AttrSourceConcept]


def _is_type_match(
    cui_obj: AttrSourceConcept, valid_types: Optional[List[str]]
) -> bool:
    """Determines if the cui_obj has a type that matches the request"""
    if valid_types and hasattr(cui_obj, "type"):
        actual_types = set(cui_obj.type.split(","))
        return any((at in valid_types for at in actual_types))

    return bool(not valid_types)


def _create_attribute_sources(
    attr: acd.AttributeValueAnnotation,
    container: acd.ContainerAnnotation,
    source_prop_names: List[AttrSourcePropName],
    concept_types: Optional[List[str]],
) -> AttributeWithCuiSources:
    """For the given attribute value annotation, find the source CUI(s) for the annotation.

    Args: attr - the attribute value annotation
          container - the complete response
          source_prop_names - properties in the container to look for the cuis
          concept_types - if supplied, concepts returned must have one of these types
    Returns: attribute and source CUI(s)
    """

    result: OrderedDict[AttrSourcePropName, AttrSourceConcept] = OrderedDict()
    uid = attr.concept.uid

    for prop_name in source_prop_names:
        logger.debug("Considering %s as the source of an attribute %s", prop_name, attr)
        if hasattr(container, prop_name.value) and getattr(container, prop_name.value):
            for cui_obj in getattr(container, prop_name.value):
                if hasattr(cui_obj, "uid") and getattr(cui_obj, "uid") == uid:
                    if _is_type_match(cui_obj, concept_types):
                        result[prop_name] = cui_obj
                    else:
                        logger.debug(
                            "CUI OBJ was rejected because not a type match %s", cui_obj
                        )
        else:
            logger.debug("Container does not have a property %s", prop_name)

    return AttributeWithCuiSources(attr=attr, sources=result)


def _create_attribute_sources_no_attr(
    container: acd.ContainerAnnotation,
    source_prop_names: List[AttrSourcePropName],
    concept_types: Optional[List[str]],
) -> List[AttributeWithCuiSources]:
    """For the specified concept list, find the source CUI(s) with one of the the requested types

    Args:
          container - the complete response
          source_prop_names - properties in the container to look for the cuis
          concept_types - if supplied, concepts returned must have one of these types
    Returns: List of attribute (None) and source CUI(s)
    """

    cui_to_sources: DefaultDict[
        str, OrderedDict[AttrSourcePropName, AttrSourceConcept]
    ] = defaultdict(OrderedDict)

    for prop_name in source_prop_names:
        if hasattr(container, prop_name.value) and getattr(container, prop_name.value):
            for cui_obj in getattr(container, prop_name.value):
                if (
                    hasattr(cui_obj, "cui")
                    and cui_obj.cui
                    and _is_type_match(cui_obj, concept_types)
                ):
                    cui_to_sources[cui_obj.cui][prop_name] = cui_obj

    return [
        AttributeWithCuiSources(attr=None, sources=srcs)
        for srcs in cui_to_sources.values()
    ]


def get_attribute_sources(
    container: acd.ContainerAnnotation,
    context: AnnotationContextType,
    ann_names_map: AttributeNameAndSourceMap,
) -> Generator[AttributeWithCuiSources, None, None]:
    """Generator to filter attributes by name of attribute

       Returned attributes include source CUI information.
       Only one CUI object per attribute per location is returned.

    Args:
        attribute_values - list of attribute value annotations from ACD
        values - allowed names for returned attributes
        ann_type_map - mapping of context to list of attribute names to search for
    """
    logger.debug("Retrieving sources for %s => %s", context, container)
    if not container.attribute_values:
        return

    attribute_values: List[acd.AttributeValueAnnotation] = container.attribute_values
    annotation_locs: List[AcdAttrSourceLoc] = ann_names_map.get(context, [])
    attr_found: bool = False

    for attr in attribute_values:
        for loc in annotation_locs:
            if loc.attr_name and attr.name == loc.attr_name:
                logger.debug(
                    "Found attribute %s for %s",
                    loc.attr_name,
                    attr.values if attr.values else "",
                )
                sources = _create_attribute_sources(
                    attr, container, loc.source_prop_names, loc.concept_types
                )
                logger.debug(
                    "Yielding attribute %s for examination of sources %s",
                    attr.name,
                    sources,
                )

                attr_found = True
                yield sources

    if not attr_found:
        # Looked at all the matching attributes and didn't find any attributes that matched
        # So check if there are concepts that we should match
        # In the case where the CUI was created by an attribute, there is only one CUI that we need,
        # (each attribute is a unique idea). But here each CUI of a specific type is a unique idea...
        # So we need to output all the concepts with cuis.
        for loc in annotation_locs:
            if not loc.attr_name:  # filter by umls type only
                concepts = _create_attribute_sources_no_attr(
                    container, loc.source_prop_names, loc.concept_types
                )
                for source_concept in concepts:
                    logger.debug(
                        "Yielding source concept with no attribute %s", source_concept
                    )
                    yield source_concept

                if concepts:
                    # Never keep processing different locations for CUIs after a CUI is found
                    break
