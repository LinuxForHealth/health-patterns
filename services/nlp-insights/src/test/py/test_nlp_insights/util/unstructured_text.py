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
"""Constants for unstructured text"""

TEXT_FOR_TWO_CONDITIONS = (
    "Patient has pneumonia and has also been diagnosed with a heart attack."
)

TEXT_FOR_MEDICATION = "Patient started taking beta blockers"

TEXT_FOR_TWO_CONDITIONS_AND_MEDICATION = (
    ""
    + "Patient has pneumonia and has also been diagnosed with a heart attack. Patient started taking beta blockers."
)

TEXT_FOR_CONDITION_SUSPECTED_AND_FAM_HISTORY = (
    "suspect skin cancer because the patient's brother has skin cancer"
)

TEXT_FOR_MULTIPLE_ATTRIBUTES_SAME_RESOURCE = (
    "The patient had a heart attack in 2015 and started taking beta blockers. "
    + "He had another heart attack in 2021 and had to start taking beta blockers again."
)
