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
"""Utilities for building and manipulating FHIR objects"""
import base64  # noqa: F401 pylint: disable=unused-import
from collections import defaultdict
import json  # noqa: F401 pylint: disable=unused-import
from typing import DefaultDict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set

from fhir.resources.attachment import (  # noqa: F401 pylint: disable=unused-import
    Attachment,
)
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import (  # noqa: F401 pylint: disable=unused-import
    Condition,
)
from fhir.resources.diagnosticreport import (  # noqa: F401 pylint: disable=unused-import
    DiagnosticReport,
)
from fhir.resources.documentreference import (  # noqa: F401 pylint: disable=unused-import
    DocumentReference,
)
from fhir.resources.element import Element
from fhir.resources.extension import Extension
from fhir.resources.medicationstatement import (  # noqa: F401 pylint: disable=unused-import
    MedicationStatement,
)
from fhir.resources.meta import Meta
from fhir.resources.reference import (  # noqa: F401 pylint: disable=unused-import
    Reference,
)
from fhir.resources.resource import Resource

from nlp_insights.fhir import alvearie_ext
from nlp_insights.fhir import alvearie_ext_url
from nlp_insights.fhir import create_coding
from nlp_insights.fhir.code_system import category
from nlp_insights.insight.span import Span  # noqa: F401 pylint: disable=unused-import
from nlp_insights.insight.text_fragment import (  # noqa: F401 pylint: disable=unused-import
    TextFragment,
)
from nlp_insights.insight_source.unstructured_text import (  # noqa: F401 pylint: disable=unused-import
    UnstructuredText,
)


def find_codings(
    codeable_concept: CodeableConcept, system: str, code: str
) -> List[Coding]:
    """Returns a list of coding elements that match the system url and id."""
    if codeable_concept.coding is None:
        return []

    return list(
        filter(lambda c: c.system == system and c.code == code, codeable_concept.coding)
    )


def _get_extension(element: Element, extension_url: str) -> Optional[Extension]:
    """Returns the extension for the element with the provided url"""
    if element.extension:
        return next(
            filter(
                lambda extension: extension is not None
                and extension.url == extension_url,
                element.extension,
            ),
            None,
        )
    return None


def get_derived_by_nlp_extension(element: Element) -> Optional[Extension]:
    """Returns a derived by NLP extension if the element has one"""
    extension = _get_extension(
        element, extension_url=alvearie_ext_url.INSIGHT_CATEGORY_URL
    )
    if (
        extension
        and extension.valueCodeableConcept
        and extension.valueCodeableConcept.coding
        and any(
            coding
            and coding.system
            and coding.code
            and coding.system == category.INSIGHT_CATEGORY_CODE_SYSTEM
            and coding.code == category.CATEGORY_DERIVED_CODE
            for coding in extension.valueCodeableConcept.coding
        )
    ):
        return extension

    return None


def append_coding(
    codeable_concept: CodeableConcept, system: str, code: str, display: str = None
) -> bool:
    """Append the coding to the codebale concept, if the coding does not exist

    This method will not append a new coding if the coding exists, even if the
    existing coding has an extension area indicating it is derived by NLP.

    A derived by NLP extension will NOT be added to the new coding

    Example:
     >>> concept = CodeableConcept.construct()
     >>> append_coding(concept,
     ...               'http://example_system',
     ...               'Code_12345',
     ...               'example display string')
     True
     >>> print(concept.json(indent=2))
     {
       "coding": [
         {
           "code": "Code_12345",
           "display": "example display string",
           "system": "http://example_system"
         }
       ]
     }
    """
    if codeable_concept.coding is None:
        codeable_concept.coding = []

    existing_codings = find_codings(codeable_concept, system, code)
    if not existing_codings:
        new_coding = create_coding.create_coding(
            system, code, display, derived_by_nlp=False
        )
        codeable_concept.coding.append(new_coding)
        return True

    return False


def append_derived_by_nlp_coding(
    codeable_concept: CodeableConcept,
    system: str,
    code: str,
    display: Optional[str] = None,
) -> bool:
    """Creates a coding and adds it to the codeable concept if the coding does not exist

    If the coding exists, but does not have the derived by NLP extension, a new coding
    is added.

    Args:
        codeable_concept - concept to append to
        system - system for the new code
        code - code id
        display - display text
    Returns:
        true if the coding was appended, false if the coding already existed

    Example:
     >>> concept = CodeableConcept.construct()
     >>> append_derived_by_nlp_coding(concept,
     ...                             'http://example_system',
     ...                             'Code_12345',
     ...                             'example display string')
     True
     >>> print(concept.json(indent=2))
     {
       "coding": [
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
           "code": "Code_12345",
           "display": "example display string",
           "system": "http://example_system"
         }
       ]
     }

     Second append doesn't append a new coding
     >>> append_derived_by_nlp_coding(concept,
     ...                             'http://example_system',
     ...                             'Code_12345',
     ...                             'example display string')
     False
     >>> print(concept.json(indent=2))
     {
       "coding": [
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
           "code": "Code_12345",
           "display": "example display string",
           "system": "http://example_system"
         }
       ]
     }
    """
    if codeable_concept.coding is None:
        codeable_concept.coding = []

    existing_codings = find_codings(codeable_concept, system, code)
    if existing_codings and any(
        get_derived_by_nlp_extension(coding) for coding in existing_codings
    ):
        # there is already a derived extension on at least one coding
        return False

    # coding exists, but no derived extension, or coding does not exist add
    # new coding
    new_coding = create_coding.create_coding(system, code, display, derived_by_nlp=True)
    codeable_concept.coding.append(new_coding)
    return True


def append_derived_by_nlp_category_extension(resource: Resource) -> None:
    """Append resource-level extension to resource, indicating resource was derived

    Does not check if the extension already exists

    Args:
         resource - entire resource created from insights

    Example:
    Prior medication resource:
     >>> resource_json = json.loads('''
     ... {
     ...    "medicationCodeableConcept": {
     ...      "coding": [
     ...             {
     ...                 "code": "C0025598",
     ...                 "display": "Metformin",
     ...                 "system": "http://terminology.hl7.org/CodeSystem/umls"
     ...             }
     ...      ],
     ...      "text": "Metformin"
     ...    },
     ...    "status": "unknown",
     ...    "subject": {
     ...      "reference": "Patient/7c33b82a-4efc-4082-9fe9-8122d6791552"
     ...    },
     ...    "resourceType": "MedicationStatement"
     ... }''')

     >>> resource = MedicationStatement.parse_obj(resource_json)

     Function Call:
     >>> append_derived_by_nlp_category_extension(resource)

     Updated Resource:
     >>> print(resource.json(indent=2))
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
       "medicationCodeableConcept": {
         "coding": [
           {
             "code": "C0025598",
             "display": "Metformin",
             "system": "http://terminology.hl7.org/CodeSystem/umls"
           }
         ],
         "text": "Metformin"
       },
       "status": "unknown",
       "subject": {
         "reference": "Patient/7c33b82a-4efc-4082-9fe9-8122d6791552"
       },
       "resourceType": "MedicationStatement"
     }
    """
    classification_ext = alvearie_ext.create_derived_by_nlp_category_extension()
    if resource.extension is None:
        resource.extension = []

    resource.extension.append(classification_ext)


def append_insight_with_path_expr_to_resource_meta(
    fhir_resource: Resource,
    insight_id: str,
    system: str,
    fhir_path: str,
    nlp_output_uri: Optional[str] = None,
) -> None:
    """Updates the meta section of a resource with extensions for the insight

    Args:
        fhir_resource - resource to update meta
        insight_id - identifier for the new insight
        system - the nlp system used to compute the insight id
        fhir_path - location of the codeable concept that the insight pertains to
        nlp_output_uri - (optional) where is the NLP output stored
    """
    insight_id_ext = alvearie_ext.create_insight_id_extension(insight_id, system)

    if nlp_output_uri:
        evaluated_output_ext = alvearie_ext.create_nlp_output_extension(nlp_output_uri)
    else:
        evaluated_output_ext = None

    insight_path = alvearie_ext.create_path_extension(fhir_path + ".coding")
    insight_reference_path = alvearie_ext.create_reference_path_extension(
        fhir_path + ".text"
    )
    insight_detail = alvearie_ext.create_derived_from_concept_insight_detail_extension(
        reference_ext=None,
        reference_path_ext=insight_reference_path,
        evaluated_output_ext=evaluated_output_ext,
    )

    add_insight_to_meta(
        fhir_resource,
        insight_id_ext,
        insight_detail,
        insight_path,
    )


def add_insight_to_meta(
    resource: Resource,
    insight_id: Extension,
    insight_detail: Optional[Extension] = None,
    insight_path: Optional[Extension] = None,
) -> None:
    """Updates a resource with an insight extension in the meta

    The meta section of the resource is created if it does not exist.

    Args:
          resource - the resource to update with a new insight extension in meta
          insight_id - a resource id extension
                       see: create_insight_id_extension
          insight_detail - an insight details extension (optional)
          insight_path - path to the element in the FHIR resource that the insight pertains to (optional)
                         this is NOT the reference path. The reference path is in the insight_detail
                         and contains a path within the reference object.
                         This parameter will be None when the entire resource is derived.

    Example #1: (Derived condition from a diagnostic report):
    Source diagnostic report resource:
    >>> visit_code = CodeableConcept.construct(text='Chief complaint Narrative - Reported')
    >>> report_text = 'Suspect that patient may be diabetic'
    >>> report_attachment = Attachment.construct(contentType="text/plain",
    ...                                          data=base64.b64encode(report_text.encode("utf-8")))
    >>> report = DiagnosticReport.construct(subject=Reference.construct(reference="Patient/12345"),
    ...                                     id='12345',
    ...                                     status='final',
    ...                                     code=visit_code,
    ...                                     presentedForm=[report_attachment])

    Derived resource to update meta for:
    >>> cnd = Condition.construct(subject=Reference.construct(reference="Patient/12345"),
    ...                           code=CodeableConcept.construct(text="diabetic"))

    Create Insight id extension:
    >>> insight_id = alvearie_ext.create_insight_id_extension("nlp-insight-1",
    ...                                                       "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/0.0.2")

    Create Insight detail Extension:
    >>> source = TextFragment(text_source=UnstructuredText(report, "presentedForm[0].data", report_text),
    ...                       text_span=Span(begin=28,end=36,covered_text='diabetic'))
    >>> method = alvearie_ext.create_scoring_method_extension(
    ...     "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method",
    ...     "Diagnosis_Explicit_Score"
    ... )
    >>> confidences = [ alvearie_ext.create_confidence_extension(method, .99, 'Explicit Score') ]
    >>> insight_detail = alvearie_ext.create_derived_from_unstructured_insight_detail_extension(source,
    ...                                                                                         confidences)

    Add Insight to meta:
    >>> add_insight_to_meta(cnd, insight_id, insight_detail)
    >>> print(cnd.json(indent=2))
    {
      "meta": {
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/0.0.2",
                  "value": "nlp-insight-1"
                }
              },
              {
                "extension": [
                  {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                    "valueReference": {
                      "reference": "DiagnosticReport/12345"
                    }
                  },
                  {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                    "valueString": "presentedForm[0].data"
                  },
                  {
                    "extension": [
                      {
                        "extension": [
                          {
                            "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                            "valueString": "diabetic"
                          },
                          {
                            "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                            "valueInteger": 28
                          },
                          {
                            "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                            "valueInteger": 36
                          },
                          {
                            "extension": [
                              {
                                "url": "http://ibm.com/fhir/cdm/StructureDefinition/method",
                                "valueCodeableConcept": {
                                  "coding": [
                                    {
                                      "code": "Diagnosis_Explicit_Score",
                                      "system": "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method"
                                    }
                                  ]
                                }
                              },
                              {
                                "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
                                "valueDecimal": 0.99
                              },
                              {
                                "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
                                "valueString": "Explicit Score"
                              }
                            ],
                            "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
                          }
                        ],
                        "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
                      }
                    ],
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-result"
                  }
                ],
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
              }
            ],
            "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
          }
        ]
      },
      "code": {
        "text": "diabetic"
      },
      "subject": {
        "reference": "Patient/12345"
      },
      "resourceType": "Condition"
    }

    Example #2: (Insight for enriched condition)
    >>> cnd = Condition.construct(subject=Reference.construct(reference="Patient/12345"),
    ...                           code=CodeableConcept.construct(text="diabetic"))
    >>> insight_id = alvearie_ext.create_insight_id_extension("nlp-insight-2",
    ...                                                       "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/0.0.2")
    >>> insight_detail = alvearie_ext.create_derived_from_concept_insight_detail_extension(
    ...                      evaluated_output_ext=alvearie_ext.create_nlp_output_extension("http://nlp-output-is-here")
    ...                  )
    >>> insight_path = alvearie_ext.create_path_extension("code.text")
    >>> add_insight_to_meta(cnd, insight_id, insight_detail, insight_path)
    >>> print(cnd.json(indent=2))
    {
      "meta": {
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
                "valueString": "code.text"
              },
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/0.0.2",
                  "value": "nlp-insight-2"
                }
              },
              {
                "extension": [
                  {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                    "valueAttachment": {
                      "url": "http://nlp-output-is-here"
                    }
                  }
                ],
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
              }
            ],
            "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight"
          }
        ]
      },
      "code": {
        "text": "diabetic"
      },
      "subject": {
        "reference": "Patient/12345"
      },
      "resourceType": "Condition"
    }
    """

    insight_extension = Extension.construct()
    insight_extension.url = alvearie_ext_url.INSIGHT_URL
    insight_extension.extension = [insight_path] if insight_path else []
    insight_extension.extension.append(insight_id)
    if insight_detail:
        insight_extension.extension.append(insight_detail)

    if resource.meta is None:
        resource.meta = Meta.construct()

    if resource.meta.extension is None:
        resource.meta.extension = []

    resource.meta.extension.append(insight_extension)


def get_existing_codes_by_system(
    codings: Iterable[Coding],
) -> DefaultDict[str, Set[str]]:
    """Returns a mutable map of system to list of code values

    The returned map is a (mutable) default dict, and will contain empty list for coding
    systems that do not exist in the list of codings.

    Args: codings -  coding objects
    Returns: map of coding system to set of contained codes
    """
    existing_codes: DefaultDict[str, Set[str]] = defaultdict(set)
    for code in codings:
        if code.system:
            if code.system not in existing_codes:
                existing_codes[code.system] = set()

            existing_codes[code.system].add(code.code)

    return existing_codes
