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
Functions for creating codings
"""


from fhir.resources.coding import Coding


def create_coding(system: str, code: str, display: str = None) -> Coding:
    """Creates an instance of a FHIR coding data type

    Args:
         system         - the url of the coding system
         code           - the code
         display        - the display text, if any

    Returns: coding element

    Examples:


     Code without display text:
     >>> code = create_coding("http://hl7.org/fhir/ValueSet/timing-abbreviation", "BID")
     >>> print(code.json(indent=2))
     {
       "code": "BID",
       "system": "http://hl7.org/fhir/ValueSet/timing-abbreviation"
     }


     Code with display text:
     >>> code = create_coding("http://hl7.org/fhir/ValueSet/timing-abbreviation","WK","weekly")
     >>> print(code.json(indent=2))
     {
       "code": "WK",
       "display": "weekly",
       "system": "http://hl7.org/fhir/ValueSet/timing-abbreviation"
     }

    """
    coding = Coding.construct()
    coding.system = system
    coding.code = code

    if display:
        coding.display = display

    return coding
