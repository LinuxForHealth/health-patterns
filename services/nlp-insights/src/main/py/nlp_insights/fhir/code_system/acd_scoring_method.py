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
"""Code system and values for ACD Scoring method

   See example at:
   https://alvearie.io/alvearie-fhir-ig/Condition-ConditionInstanceWithNLPInsights.json.html
"""


SCORING_METHOD_ACD_CODE_SYSTEM = (
    "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method"
)

# Values for acd scoring method
DIAGNOSIS_EXPLICIT_SCORE = "Diagnosis_Explicit_Score"
DIAGNOSIS_PATIENT_REPORTED_SCORE = "Diagnosis_Patient_Reported_Score"
MEDICATION_TAKEN_SCORE = "Medication_Taken_Score"
