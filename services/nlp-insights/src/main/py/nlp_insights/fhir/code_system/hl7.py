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
"""Core FHIR and HL7 Code systems
   See https://terminology.hl7.org/codesystems.html and also
       https://www.hl7.org/fhir/terminologies-systems.html
"""

SNOMED_URL = "http://snomed.info/sct"  # SNOMED CT International Edition
RXNORM_URL = "http://www.nlm.nih.gov/research/umls/rxnorm"
LOINC_URL = "http://loinc.org"
NCI_URL = "http://ncimeta.nci.nih.gov"
ICD9_URL = "http://hl7.org/fhir/sid/icd-9-cm"
ICD10_URL = "http://hl7.org/fhir/sid/icd-10-cm"
UMLS_URL = (
    "http://terminology.hl7.org/CodeSystem/umls"  # Unified Medical Language System
)
MESH_URL = "http://terminology.hl7.org/CodeSystem/MSH"  # Medical Subject Headings
