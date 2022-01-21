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
Defines a span type used to represent a span
"""
from typing import NamedTuple, Optional, List
from fhir.resources.extension import Extension
from nlp_insights.fhir import alvearie_ext


class Span(NamedTuple):
    """
    A span is a selection of text of significance

    Typically a span is the source of an insight
    """

    begin: int
    end: int
    covered_text: str

    def create_alvearie_extension(
        self, confidences: Optional[List[Extension]] = None
    ) -> Extension:
        """Creates an extension from the span

        Args:
        confidences - list of alvearie confidence extensions for the span (optional)

        Returns an alvearie span extension
        """
        return alvearie_ext.create_span_extension(
            offset_begin=alvearie_ext.create_offset_begin_extension(self.begin),
            offset_end=alvearie_ext.create_offset_end_extension(self.end),
            covered_text=alvearie_ext.create_covered_text_extension(self.covered_text),
            confidences=confidences,
        )
