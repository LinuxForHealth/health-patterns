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
Defines a data type for representing a FHIR Path expression.

The standard for FHIR path expressions can be found at:
https://www.hl7.org/fhir/fhirpath.html, which is based on
http://hl7.org/fhirpath/N1/

This defines only a data type to represent paths, and does not
implement any function for evaluation
"""


class FhirPath(str):
    """Special type of string that holds a FhirPath

    The string is expected to be a valid hl7 FHIR Path as
    defined by https://www.hl7.org/fhir/fhirpath.html

    No validation is performed to ensure that the string
    is in fact a FHIR path. The type is included for documentation.
    """
