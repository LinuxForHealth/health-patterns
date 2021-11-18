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
"""Low level NLP configuration"""
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Optional

from fhir.resources.extension import Extension

from text_analytics.fhir import fhir_object_utils

from text_analytics.nlp.acd.fhir_enrichment.insights.attribute_source_cui import (
    SourceCuiSearchMap,
)


from text_analytics.nlp.acd.flows.default_attribute_source_info import (
    RELEVANT_ANNOTATIONS_STANDARD_V1_0,
)


@dataclass
class NlpConfig:
    """NLP Configuration Settings"""

    nlp_system: str
    get_nlp_output_loc: Callable[[Any], Optional[str]]
    insight_id_start: int = 1
    acd_attribute_source_map: Optional[SourceCuiSearchMap] = None

    def create_nlp_output_extension(self, nlp_output: Any) -> Optional[Extension]:
        """Creates an NLP output extension

        This uses the get_nlp_output_loc method to build the extension.
        If the method does not supply a location, None is returned
        """
        nlp_output_url = self.get_nlp_output_loc(nlp_output)
        if nlp_output_url:
            return fhir_object_utils.create_nlp_output_extension(nlp_output_url)

        return None

    def get_valid_acd_attr_source_map(self) -> SourceCuiSearchMap:
        """Returns the attribute source map

        This option is only useful for ACD flows

        Raises TypeError if the map is not defined.
        """
        if self.acd_attribute_source_map is not None:
            return self.acd_attribute_source_map

        raise TypeError("The acd_attribute_source_map is None")


ACD_NLP_CONFIG_STANDARD_V1_0 = NlpConfig(
    nlp_system="urn:alvearie.io/patterns/wh_acd.ibm_clinical_insights_v1.0_standard_flow/0.0.2",
    get_nlp_output_loc=lambda x: None,
    acd_attribute_source_map=RELEVANT_ANNOTATIONS_STANDARD_V1_0,
)


QUICK_UMLS_NLP_CONFIG = NlpConfig(
    nlp_system="urn:alvearie.io/patterns/QuickUMLS_v1.4.0/0.0.2",
    get_nlp_output_loc=lambda x: None,
)
