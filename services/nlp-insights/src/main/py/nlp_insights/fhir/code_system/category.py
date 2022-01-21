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
"""Alvearie Insight Category Code system and value set"""

# Alvearie Category Code system
# See https://alvearie.io/alvearie-fhir-ig/CodeSystem-insight-category-code-system.html
INSIGHT_CATEGORY_CODE_SYSTEM = (
    "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
)

# Constants for INSIGHT_CATEGORY_CODE_SYSTEM value set
# See https://alvearie.io/alvearie-fhir-ig/ValueSet-insight-category-values.html
CATEGORY_DERIVED_CODE = "natural-language-processing"
CATEGORY_DERIVED_DISPLAY = "NLP"
