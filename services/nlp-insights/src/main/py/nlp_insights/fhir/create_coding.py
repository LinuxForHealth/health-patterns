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
from nlp_insights.fhir import alvearie_ext


def create_coding(
    system: str, code: str, display: str = None, derived_by_nlp: bool = False
) -> Coding:
    """Creates an instance of a FHIR coding data type

    Args:
         system         - the url of the coding system
         code           - the code
         display        - the display text, if any
         derived_by_nlp - If true, a derived by NLP category extension will be added

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


     Code derived by NLP:
     >>> code = create_coding("http://hl7.org/fhir/ValueSet/timing-abbreviation",
     ...                      "WK",
     ...                      derived_by_nlp=True)
     >>> print(code.json(indent=2))
     {
       "extension": [
         {
           "url": "http://ibm.com/fhir/cdm/StructureDefinition/category",
           "valueCodeableConcept": {
             "coding": [
               {
                 "code": "natural-language-processing",
                 "display": "NLP",
                 "system": "http://ibm.com/fhir/cdm/CodeSystem/insight-category-code-system"
               }
             ],
             "text": "NLP"
           }
         }
       ],
       "code": "WK",
       "system": "http://hl7.org/fhir/ValueSet/timing-abbreviation"
     }
    """
    coding = Coding.construct()
    coding.system = system
    coding.code = code

    if display:
        coding.display = display

    if derived_by_nlp:
        coding.extension = [alvearie_ext.create_derived_by_nlp_category_extension()]

    return coding
