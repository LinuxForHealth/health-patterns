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
"""Constants for unstructured text

   The ACD and QuickUMLS NLP services' output for these text strings must
   be included in resources/acd/TestReportResponses.json and
   resources/quickUmls/TestReportResponses.json

"""

TEXT_FOR_MULTIPLE_CONDITIONS = (
    "Patient reports that they recently had pneumonia "
    + "and is now having chest pain. "
    + "The patient was diagnosed with a myocardial infarction."
)

TEXT_FOR_MEDICATION = "Patient is taking Cisplatin."

TEXT_FOR_CONDITION_AND_MEDICATION = (
    ""
    + "Patient had pneumonia a month ago and has now been diagnosed with "
    + "a myocardial infarction. Prescribed Acebutolol."
)

TEXT_FOR_CONDITION_SUSPECTED_AND_FAM_HISTORY = (
    "suspect skin cancer because the patient's brother has skin cancer"
)

# Important thing with this text is that there are multiple spans over the same
# condition and medication
# With the condition, "myocardial infarction" == "heart attack"
TEXT_FOR_MULTIPLE_ATTRIBUTES_SAME_RESOURCE = (
    "The patient had a myocardial infarction in 2015 and was prescribed Losartan. "
    + "His prescription was changed to Irbesartan in 2019. "
    + "He had a second heart attack in 2021, and is now taking Losartan again."
)
