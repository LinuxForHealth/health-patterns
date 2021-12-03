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
Defines source information for an insight
"""
from typing import NamedTuple
from nlp_insights.insight.span import Span
from nlp_insights.insight_source.unstructured_text import UnstructuredText


class TextFragment(NamedTuple):
    """Location of unstructured data used to produce an insight

    This unstructured data is expected to be attachment text,
    such as clinical notes.
    """

    text_source: UnstructuredText
    text_span: Span
