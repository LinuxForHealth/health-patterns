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
"""Utilities for creating a subset of FHIR extensions defined by Alvearie

   See: https://alvearie.io/alvearie-fhir-ig/artifacts.html for more information
   about the types of extensions that Alvearie defines.
"""


import base64
import json  # noqa: F401 pylint: disable=unused-import
from typing import List
from typing import Optional
from typing import Union

from fhir.resources.attachment import Attachment
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.diagnosticreport import (  # noqa: F401 pylint: disable=unused-import
    DiagnosticReport,
)
from fhir.resources.documentreference import (  # noqa: F401 pylint: disable=unused-import
    DocumentReference,
)
from fhir.resources.extension import Extension
from fhir.resources.identifier import Identifier
from fhir.resources.medicationstatement import (  # noqa: F401 pylint: disable=unused-import
    MedicationStatement,
)
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource

from nlp_insights.fhir import alvearie_ext_url
from nlp_insights.fhir.code_system import category
from nlp_insights.fhir.path import FhirPath
from nlp_insights.insight_source.unstructured_text import (  # noqa: F401 pylint: disable=unused-import
    UnstructuredText,
)


def create_insight_extension(
    insight_id: Extension,
    insight_path: Optional[Extension] = None,
    insight_details: Optional[List[Extension]] = None,
) -> Extension:
    """Creates an extension for an insight

    Params:
    insight_id - extension created by create_insight_id_extension
    insight_path - optional extension created by create_path_extension
    insight_details - optional list of extensions created by create_insight_details

    Example:
    >>> id = create_insight_id_extension("insight-1", "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/")
    >>> path = create_path_extension(FhirPath("Condition"))

    Insight Details:
    >>> visit_code = CodeableConcept.construct(text='Chief complaint Narrative - Reported')
    >>> report_text = 'Patient is diabetic'
    >>> report_attachment = Attachment.construct(contentType="text/plain",
    ...                                          data=base64.b64encode(report_text.encode("utf-8")))
    >>> report = DiagnosticReport.construct(id='12345',
    ...                                     status='final',
    ...                                     code=visit_code,
    ...                                     presentedForm=[report_attachment])

    >>> reference = create_reference_extension(report)
    >>> reference_path = create_reference_path_extension(FhirPath('DiagnosticReport.presentedForm[0].data'))
    >>> evaluated_output = create_evaluated_output_extension('{"NLP-Result": "some-data"}'.encode("utf-8"))
    >>> result = create_insight_result_extension(spans=[
    ...                create_span_extension(
    ...                      offset_begin=create_offset_begin_extension(0),
    ...                      offset_end=create_offset_end_extension(10),
    ...                      covered_text=create_covered_text_extension("hello world"),
    ...                      confidences=[]
    ...                )
    ... ])
    >>> detail=create_insight_detail_extension(reference, reference_path, evaluated_output, [result])

    Insight:
    >>> insight = create_insight_extension(id, path, [detail])
    >>> print(insight.json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
          "valueIdentifier": {
            "system": "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/",
            "value": "insight-1"
          }
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
          "valueString": "Condition"
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
              "valueString": "DiagnosticReport.presentedForm[0].data"
            },
            {
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
              "valueAttachment": {
                "contentType": "application/json",
                "data": "eyJOTFAtUmVzdWx0IjogInNvbWUtZGF0YSJ9"
              }
            },
            {
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                      "valueString": "hello world"
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                      "valueInteger": 0
                    },
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                      "valueInteger": 10
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
    """
    insight = Extension.construct()
    insight.url = alvearie_ext_url.INSIGHT_URL
    insight.extension = [insight_id]

    if insight_path:
        insight.extension.append(insight_path)

    if insight_details:
        insight.extension.extend(insight_details)

    return insight


def create_insight_id_extension(
    insight_id_value: str, insight_system: str
) -> Extension:
    """Creates an extension for an insight-id with a valueIdentifier

       The insight id extension is defined in the IG at:
       https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-id.html

        Args:
            insight_id_value   - the value of the insight id
            insight_system     - urn for the system used to create the insight

        Returns: The insight id extension

    Example:
    >>> ext = create_insight_id_extension("insight-1", "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0")
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
      "valueIdentifier": {
        "system": "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0",
        "value": "insight-1"
      }
    }
    """
    insight_id_ext = Extension.construct()
    insight_id_ext.url = alvearie_ext_url.INSIGHT_ID_URL

    insight_id = Identifier.construct()
    insight_id.system = insight_system
    insight_id.value = insight_id_value

    insight_id_ext.valueIdentifier = insight_id
    return insight_id_ext


def create_path_extension(path: FhirPath) -> Extension:
    """Creates an extension for an insights path to a FHIR element

    This is defined by the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-path.html

    Example:
    >>> ext = create_path_extension(FhirPath("Condition.code.text"))
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/path",
      "valueString": "Condition.code.text"
    }
    """
    path_ext = Extension.construct()
    path_ext.url = alvearie_ext_url.INSIGHT_PATH_URL
    path_ext.valueString = path
    return path_ext


def create_insight_detail_extension(
    reference: Optional[Extension] = None,
    reference_path: Optional[Extension] = None,
    evaluated_output: Optional[Extension] = None,
    insight_results: Optional[List[Extension]] = None,
) -> Extension:
    """Creates an insight detail extension

    The insight detail extension is described in the IG by:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-detail.html

    Args:
    reference_ext -      optional reference to object with source text
    reference_path - optional path within reference to where the source text is
    evaluated_output - optional evaluated output from NLP
    insight_results - optional list of spans and confidences

    Returns:
    Insight detail extension

    >>> visit_code = CodeableConcept.construct(text='Chief complaint Narrative - Reported')
    >>> report_text = 'Patient is diabetic'
    >>> report_attachment = Attachment.construct(contentType="text/plain",
    ...                                          data=base64.b64encode(report_text.encode("utf-8")))
    >>> report = DiagnosticReport.construct(id='12345',
    ...                                     status='final',
    ...                                     code=visit_code,
    ...                                     presentedForm=[report_attachment])

    >>> reference = create_reference_extension(report)
    >>> reference_path = create_reference_path_extension(FhirPath('DiagnosticReport.presentedForm[0].data'))
    >>> evaluated_output = create_evaluated_output_extension('{"NLP-Result": "some-data"}'.encode("utf-8"))
    >>> result = create_insight_result_extension(spans=[
    ...                create_span_extension(
    ...                      offset_begin=create_offset_begin_extension(0),
    ...                      offset_end=create_offset_end_extension(10),
    ...                      covered_text=create_covered_text_extension("hello world"),
    ...                      confidences=[]
    ...                )
    ... ])
    >>> insight=create_insight_detail_extension(reference, reference_path, evaluated_output, [result])
    >>> print(insight.json(indent=2))
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
          "valueString": "DiagnosticReport.presentedForm[0].data"
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
          "valueAttachment": {
            "contentType": "application/json",
            "data": "eyJOTFAtUmVzdWx0IjogInNvbWUtZGF0YSJ9"
          }
        },
        {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                  "valueString": "hello world"
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                  "valueInteger": 0
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                  "valueInteger": 10
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
    """
    insight_detail = Extension.construct()
    insight_detail.url = alvearie_ext_url.INSIGHT_DETAIL_URL
    insight_detail.extension = []

    if reference:
        insight_detail.extension.append(reference)
    if reference_path:
        insight_detail.extension.append(reference_path)
    if evaluated_output:
        insight_detail.extension.append(evaluated_output)
    if insight_results:
        insight_detail.extension.extend(insight_results)
    return insight_detail


def create_reference_extension(resource: Union[Resource, str]) -> Extension:
    """Creates an extension to reference the provided resource

    This is used to explain where the passed resource came from.

    The insight reference in the IG is described at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-reference.html

    Args:
        resource - FHIR resource to reference. This could be the resource itself,
                   or a string containing one of the other reference types, such
                   as a logical URI (UUID).

    In the case where a FHIR resource is supplied, the resource id is used
    to construct the reference. e.g. "DiagnosticReport/12345"

    Returns:
        the "based-on" extension

    Example:
    >>> visit_code = CodeableConcept.construct(text='Chief complaint Narrative - Reported')
    >>> report_text = 'Patient is diabetic'
    >>> report_attachment = Attachment.construct(contentType="text/plain",
    ...                                          data=base64.b64encode(report_text.encode("utf-8")))
    >>> report = DiagnosticReport.construct(id='12345',
    ...                                     status='final',
    ...                                     code=visit_code,
    ...                                     presentedForm=[report_attachment])

    >>> ext = create_reference_extension(report)
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
      "valueReference": {
        "reference": "DiagnosticReport/12345"
      }
    }

    Examlpe #2:
    >>> ext = create_reference_extension("urn:uuid:05efabf0-4be2-4561-91ce-51548425acb9")
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
      "valueReference": {
        "reference": "urn:uuid:05efabf0-4be2-4561-91ce-51548425acb9"
      }
    }
    """
    reference = Reference.construct()
    if isinstance(resource, Resource):
        reference_id = resource.id if resource.id else ""
        reference.reference = resource.resource_type + "/" + reference_id
    elif isinstance(resource, str):
        reference.reference = resource
    else:
        raise TypeError("This method supports only string and resource")

    based_on_extension = Extension.construct()
    based_on_extension.url = alvearie_ext_url.INSIGHT_REFERENCE_URL
    based_on_extension.valueReference = reference
    return based_on_extension


def create_reference_path_extension(path: FhirPath) -> Extension:
    """Creates an extension for an insight's reference path

    This is the location within the reference FHIR resource that
    caused the insight to be created.

    It is defined in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-reference-path.html

    Example:
    >>> ext = create_reference_path_extension(FhirPath('AllergyIntolerance.code'))
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
      "valueString": "AllergyIntolerance.code"
    }
    """
    reference_ext = Extension.construct()
    reference_ext.url = alvearie_ext_url.INSIGHT_REFERENCE_PATH_URL
    reference_ext.valueString = path
    return reference_ext


def create_evaluated_output_extension(
    data: bytes, content_type: str = "application/json"
) -> Extension:
    """
    Creates an extension containing the nlp output.

    This is an evaluated output extension that is defined by the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-evaluated-output.html

    Returns: NLP output extension

    Example:
    >>> ext = create_evaluated_output_extension('nlp-response-text'.encode("utf-8"))
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
      "valueAttachment": {
        "contentType": "application/json",
        "data": "bmxwLXJlc3BvbnNlLXRleHQ="
      }
    }
    """
    attachment = Attachment.construct()
    attachment.contentType = content_type
    # attachment.data = base64.b64encode(data).decode("utf-8")
    attachment.data = base64.b64encode(data).decode("utf-8")
    nlp_output_ext = Extension.construct()
    nlp_output_ext.url = alvearie_ext_url.INSIGHT_EVALUATED_OUTPUT_URL
    nlp_output_ext.valueAttachment = attachment
    return nlp_output_ext


def create_insight_result_extension(spans: List[Extension]) -> Extension:
    """Returns an insight result extension

    This extension is described by the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-result.html

    Args:
    span - the span extension(s) for the insight

    The IG also includes value and based-on-value in the result section, but
    but these fields are not used by nlp-insights, and thus are not included as args.

    Returns an insight result extension

    Example:
    >>> confidence = create_insight_confidence_extension(
    ...                 score=create_score_extension(.99),
    ...                 scoring_method=create_scoring_method_extension('urn:method_system', 'score-method')
    ... )
    >>> result = create_insight_result_extension(spans=[
    ... create_span_extension(
    ...                      offset_begin=create_offset_begin_extension(0),
    ...                      offset_end=create_offset_end_extension(10),
    ...                      covered_text=create_covered_text_extension("hello world"),
    ...                      confidences=[confidence]
    ...                      )
    ... ])
    >>> print(result.json(indent=2))
    {
      "extension": [
        {
          "extension": [
            {
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
              "valueString": "hello world"
            },
            {
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
              "valueInteger": 0
            },
            {
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
              "valueInteger": 10
            },
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/method",
                  "valueCodeableConcept": {
                    "coding": [
                      {
                        "code": "score-method",
                        "system": "urn:method_system"
                      }
                    ]
                  }
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
                  "valueDecimal": 0.99
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

    """
    insight_result = Extension.construct()
    insight_result.url = alvearie_ext_url.INSIGHT_RESULT_URL
    insight_result.extension = spans
    return insight_result


def create_span_extension(
    offset_begin: Extension,
    offset_end: Extension,
    covered_text: Extension,
    confidences: Optional[List[Extension]],
) -> Extension:
    """Creates an extension for a span of text.


    The span extension is defined in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-span.html

    Example:
    >>> confidence = create_insight_confidence_extension(
    ...                  score=create_score_extension(.99),
    ...                  scoring_method=create_scoring_method_extension('urn:method_system', 'score-method')
    ... )
    >>> span = create_span_extension(
    ...                      offset_begin=create_offset_begin_extension(0),
    ...                      offset_end=create_offset_end_extension(10),
    ...                      covered_text=create_covered_text_extension("hello world"),
    ...                      confidences=[confidence]
    ...                      )
    >>> print(span.json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
          "valueString": "hello world"
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
          "valueInteger": 0
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
          "valueInteger": 10
        },
        {
          "extension": [
            {
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/method",
              "valueCodeableConcept": {
                "coding": [
                  {
                    "code": "score-method",
                    "system": "urn:method_system"
                  }
                ]
              }
            },
            {
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
              "valueDecimal": 0.99
            }
          ],
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
        }
      ],
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
    }
    """
    insight_span = Extension.construct()
    insight_span.url = alvearie_ext_url.INSIGHT_SPAN_URL
    insight_span.extension = [covered_text]
    insight_span.extension.append(offset_begin)
    insight_span.extension.append(offset_end)
    if confidences:
        insight_span.extension.extend(confidences)

    return insight_span


def create_offset_begin_extension(offset: int) -> Extension:
    """Returns an offset begin extension for the offset

    This extension is documented in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-offset-begin.html

    Args:
    offset - the begin offset

    Returns the offset begin extension
    """
    offset_begin_ext = Extension.construct()
    offset_begin_ext.url = alvearie_ext_url.INSIGHT_SPAN_OFFSET_BEGIN_URL
    offset_begin_ext.valueInteger = offset
    return offset_begin_ext


def create_offset_end_extension(offset: int) -> Extension:
    """Returns an offset end extension for the offset

    This extension is documented in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-offset-end.html

    Args:
    offset - the end offset

    Returns the offset end extension
    """
    offset_begin_ext = Extension.construct()
    offset_begin_ext.url = alvearie_ext_url.INSIGHT_SPAN_OFFSET_END_URL
    offset_begin_ext.valueInteger = offset
    return offset_begin_ext


def create_covered_text_extension(covered_text: str) -> Extension:
    """Returns an extension for the covered text of a span

    This extension is documented in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-covered-text.html

    Args:
    covered_text - the text that the span covers

    Returns: Covered text extension
    """
    covered_text_ext = Extension.construct()
    covered_text_ext.url = alvearie_ext_url.INSIGHT_SPAN_COVERED_TEXT_URL
    covered_text_ext.valueString = covered_text

    return covered_text_ext


def create_insight_confidence_extension(
    score: Extension,
    scoring_method: Optional[Extension] = None,
    scoring_description: Optional[Extension] = None,
) -> Extension:
    """Creates a FHIR extension element for insight confidence

    The insight-confidence extension is defined in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-confidence.html

    Params:
        scoring_method - method extension describing how the score was computed
        score  - the confidence score
        scoring_description - description extension

    Example:
    >>> method = create_scoring_method_extension(
    ...     "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method",
    ...     "Diagnosis_Explicit_Score"
    ... )
    >>> score = create_score_extension(1.0)
    >>> description = create_scoring_description_extension('explicitly stated diagnosis')
    >>> print(create_insight_confidence_extension(method, score, description).json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
          "valueDecimal": 1.0
        },
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
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
          "valueString": "explicitly stated diagnosis"
        }
      ],
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
    }
    """
    confidence = Extension.construct()
    confidence.url = alvearie_ext_url.INSIGHT_CONFIDENCE_URL

    confidence.extension = [scoring_method]
    confidence.extension.append(score)

    if scoring_description:
        confidence.extension.append(scoring_description)
    return confidence


def create_scoring_method_extension(system: str, code: str) -> Extension:
    """Creates a FHIR extension for a scoring method.

    The scoring method extension is documented in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-method.html

    Params:
        system - code system for the method code
        code   - code for the method used to determine the confidence

    Example:
    >>> print(create_scoring_method_extension(
    ...     "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method",
    ...     "Diagnosis_Explicit_Score"
    ... ).json(indent=2))
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
    }
    """
    method_ext = Extension.construct()
    method_ext.url = alvearie_ext_url.INSIGHT_CONFIDENCE_SCORING_METHOD_URL

    method_coding = Coding.construct()
    method_coding.system = system
    method_coding.code = code

    method_value = CodeableConcept.construct()
    method_value.coding = [method_coding]

    method_ext.valueCodeableConcept = method_value
    return method_ext


def create_score_extension(score: float) -> Extension:
    """Creates a confidence score extnsion

    This structure is documented in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-score.html

    Args:
    score - the score value

    Returns the score Extension
    """
    score_ext = Extension.construct()
    score_ext.url = alvearie_ext_url.INSIGHT_CONFIDENCE_SCORE_URL
    score_ext.valueDecimal = score
    return score_ext


def create_scoring_description_extension(description: str) -> Extension:
    """Creates a FHIR extension for a description of a scoring method.

    The scoring description extension is documented in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-description.html

    Params:
        description - plain text description of the insight score result

    Example:
    >>> ext = create_scoring_description_extension("Explicit confidence score from NLP")
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
      "valueString": "Explicit confidence score from NLP"
    }
    """
    score_description = Extension.construct()
    score_description.url = alvearie_ext_url.INSIGHT_CONFIDENCE_DESCRIPTION_URL
    score_description.valueString = description
    return score_description


def create_insight_summary_extension(
    insight_id_extension: Optional[Extension] = None,
    category_extension: Optional[Extension] = None,
) -> Extension:
    """Creates an insight summary extension

    See the IG documentation for the definition of this structure.
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-summary.html

    Example:
    >>> ext = create_insight_summary_extension(
    ...    create_insight_id_extension(insight_id_value="nlp-insight-1",
    ...                                insight_system="urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0"),
    ...    create_derived_by_nlp_category_extension()
    ... )
    >>> print(ext.json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
          "valueIdentifier": {
            "system": "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0",
            "value": "nlp-insight-1"
          }
        },
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
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-summary"
    }
    """
    summary_ext = Extension.construct()
    summary_ext.url = alvearie_ext_url.INSIGHT_SUMMARY_URL
    summary_ext.extension = []

    if insight_id_extension:
        summary_ext.extension.append(insight_id_extension)
    if category_extension:
        summary_ext.extension.append(category_extension)
    return summary_ext


def create_derived_by_nlp_category_extension() -> Extension:
    """Creates a category extension indicating the element is derived from NLP

    See the IG Documentation for the structure of the category:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-category.html

    Example:
    >>> print(create_derived_by_nlp_category_extension().json(indent=2))
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
    """
    classification_ext = Extension.construct()
    classification_ext.url = alvearie_ext_url.INSIGHT_CATEGORY_URL

    classification_coding = Coding.construct()
    classification_coding.system = category.INSIGHT_CATEGORY_CODE_SYSTEM
    classification_coding.code = category.CATEGORY_DERIVED_CODE
    classification_coding.display = category.CATEGORY_DERIVED_DISPLAY

    classification_value = CodeableConcept.construct()
    classification_value.coding = [classification_coding]
    classification_value.text = category.CATEGORY_DERIVED_DISPLAY
    classification_ext.valueCodeableConcept = classification_value
    return classification_ext
