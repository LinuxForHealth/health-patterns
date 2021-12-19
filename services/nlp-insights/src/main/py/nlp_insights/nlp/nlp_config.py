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
import dataclasses

from nlp_insights.nlp.acd.fhir_enrichment.insights.attribute import (
    SourceSearchMap,
)
from nlp_insights.nlp.acd.flows.default_attribute_source_info import (
    RELEVANT_ANNOTATIONS_STANDARD_V1_0,
)


@dataclass
class NlpConfig:
    """NLP Configuration Settings"""

    nlp_system: str


@dataclass
class AcdNlpConfig(NlpConfig):
    """NLP Configuration with specific features for ACD"""

    acd_attribute_source_map: SourceSearchMap = dataclasses.field(
        default_factory=RELEVANT_ANNOTATIONS_STANDARD_V1_0.copy
    )


ACD_NLP_CONFIG_STANDARD_V1_0 = AcdNlpConfig(
    nlp_system="urn:alvearie.io/health_patterns/services/nlp_insights/acd",
)


QUICK_UMLS_NLP_CONFIG = NlpConfig(
    nlp_system="urn:alvearie.io/health_patterns/services/nlp_insights/quickumls",
)
