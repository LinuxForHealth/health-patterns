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
"""Common way of constructing insight IDs for all NLP pipelines"""
import hashlib
from typing import Generator, Type, Optional

from fhir.resources.resource import Resource

from nlp_insights.insight_source import fields_of_interest
from nlp_insights.insight_source import unstructured_text


def insight_id_maker_update_concept(
    concept: fields_of_interest.CodeableConceptRef,
    resource: Resource,
    start: int = 1,
) -> Generator[str, None, None]:
    """Creates a insight id generator for insights related to updating a codeable concept of a resource

    The prefix of the generator is made (more) unique by hashing certain fields in the input parameters.

    Params:
      concept - the concept reference that is being updated
      resource - the resource that is being updated
      start - integer to start numbering insights with (default is 1)

    """
    prefix = resource.__class__.__name__
    if resource.id:
        prefix += resource.id
    prefix += concept.fhir_path

    prefix = "nlp-insight-" + hashlib.sha224(prefix.encode("utf-8")).hexdigest() + "-"

    return insight_id_maker(insight_id_string_prefix=prefix, start=start)


def insight_id_maker_derive_resource(
    source: unstructured_text.UnstructuredText,
    cui: Optional[str],
    derived: Type[Resource],
    start: int = 1,
) -> Generator[str, None, None]:
    """Creates a insight id generator prefix for deriving a resource

    The prefix of the generator is made (more) unique by hashing certain fields in the input parameters.

    Params:
        source - unstructured text that is being used to derive the resource
        cui    - the cui that is associated with the derived resource (optional)
        derived - the class of resource being derived
        start - integer to start numbering insights with (default is 1)
    """
    prefix = source.source_resource.__class__.__name__
    if source.source_resource.id:
        prefix += source.source_resource.id
    prefix += source.fhir_path
    if source.source_resource.subject and source.source_resource.subject.reference:
        prefix += source.source_resource.subject.reference

    if cui:
        prefix += cui
    else:
        prefix += "None"

    prefix += derived.__name__

    prefix = "nlp-insight-" + hashlib.sha224(prefix.encode("utf-8")).hexdigest() + "-"

    return insight_id_maker(insight_id_string_prefix=prefix, start=start)


def insight_id_maker(
    insight_id_string_prefix: str = "nlp-insight-",
    start: int = 1,
) -> Generator[str, None, None]:
    """Generator to return the next insight id for a resource

    Args:
        insight_id_string_prefix - string value to prepend to each id
        count to start at

    Example:
    >>> maker = insight_id_maker()
    >>> next(maker)
    'nlp-insight-1'
    >>> next(maker)
    'nlp-insight-2'
    """
    insight_id_num = start
    while True:
        yield insight_id_string_prefix + str(insight_id_num)
        insight_id_num += 1
