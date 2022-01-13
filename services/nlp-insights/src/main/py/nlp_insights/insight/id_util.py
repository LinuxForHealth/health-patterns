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
"""Utilities to generate insight ids"""
import hashlib
from typing import Type
from typing import Union

from fhir.resources.resource import Resource

from nlp_insights.insight_source.fields_of_interest import CodeableConceptRef
from nlp_insights.insight_source.unstructured_text import UnstructuredText


def make_hash(
    *args: Union[str, UnstructuredText, CodeableConceptRef, Type[Resource]]
) -> str:
    """Takes one or more objects and creates a hash for them.

    The returned hash will always be the same value given the same
    inputs, even across runtimes.

    Examples:
    >>> make_hash(Resource.construct(id='123'), 'cui1,cui2,cui3', 'Condition')
    '391491a32c17a41b6fd13be777fc8541c5e9ff09e45dcff1c596f8d0'
    """
    hash_input = ""
    for arg in args:
        if isinstance(arg, str):
            hash_input += arg
        elif isinstance(arg, UnstructuredText):
            hash_input += arg.source_ref.reference
            hash_input += arg.text_path
            hash_input += arg.text
        elif isinstance(arg, CodeableConceptRef):
            hash_input += str(arg.type)
            hash_input += str(arg.path)
            hash_input += str(arg.resource_ref.reference)
        elif isinstance(arg, type) and issubclass(arg, Resource):
            hash_input += arg.__name__

    return hashlib.sha224(hash_input.encode("utf-8")).hexdigest()
