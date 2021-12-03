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
"""Utilities for creating FHIR extensions that are specific to the Alvearie IG

   Methods in this module should create alvearie extensions or related elements,
   they should not modify resources.

"""


import json  # noqa: F401 pylint: disable=unused-import
from typing import List
from typing import Optional

from fhir.resources.attachment import Attachment
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.diagnosticreport import (  # noqa: F401 pylint: disable=unused-import
    DiagnosticReport,
)
from fhir.resources.documentreference import (  # noqa: F401 pylint: disable=unused-import
    DocumentReference,
)
from fhir.resources.element import Element
from fhir.resources.extension import Extension
from fhir.resources.identifier import Identifier
from fhir.resources.medicationstatement import (  # noqa: F401 pylint: disable=unused-import
    MedicationStatement,
)
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource

from nlp_insights.insight import (
    insight_constants,
)  # noqa: F401 pylint: disable=unused-import

from nlp_insights.insight.span import Span
from nlp_insights.insight.text_fragment import TextFragment
from nlp_insights.insight_source.unstructured_text import (  # noqa: F401 pylint: disable=unused-import
    UnstructuredText,
)


def create_coding(
    system: str, code: str, display: str = None, derived_by_nlp: bool = False
) -> Element:
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
    coding_element = Coding.construct()
    coding_element.system = system
    coding_element.code = code

    if display:
        coding_element.display = display

    if derived_by_nlp:
        coding_element.extension = [create_derived_by_nlp_extension()]

    return coding_element


def create_reference_path_extension(path: str) -> Extension:
    """Creates an extension for an insight's reference path

    This is the location within the FHIR resource that
    caused the insight to be created.

    It is defined in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-reference-path.html

    Example:
    >>> ext = create_reference_path_extension('AllergyIntolerance.code')
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
      "valueString": "AllergyIntolerance.code"
    }
    """
    reference_ext = Extension.construct()
    reference_ext.url = insight_constants.INSIGHT_REFERENCE_PATH_URL
    reference_ext.valueString = path
    return reference_ext


def create_reference_to_resource_extension(resource: Resource) -> Extension:
    """Creates an extension to reference the provided resource

    This is used to explain where the passed resource came from.

    The insight reference in the IG is described at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-reference.html

    Args:
        resource - FHIR resource to reference

    Returns:
        the "based-on" extension

    Example:
    >>> visit_code = CodeableConcept.construct(text='Mental status Narrative')
    >>> d = DiagnosticReport.construct(id='12345',
    ...                                code=visit_code,
    ...                                text='crazy',
    ...                                status='final')
    >>> ext = create_reference_to_resource_extension(d)
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
      "valueReference": {
        "reference": "DiagnosticReport/12345"
      }
    }
    """
    reference_id = resource.id if resource.id else "_unknown_"
    reference = Reference.construct()
    reference.reference = resource.resource_type + "/" + reference_id

    based_on_extension = Extension.construct()
    based_on_extension.url = insight_constants.INSIGHT_BASED_ON_URL
    based_on_extension.valueReference = reference
    return based_on_extension


def create_confidence_extension(name: str, value: str) -> Extension:
    """Creates a FHIR extension element for insight confidence

    The insight-confidence extension is defined in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-confidence.html

    Example:
    >>> print(create_confidence_extension('insight', 1.0).json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
          "valueString": "insight"
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
          "valueDecimal": 1.0
        }
      ],
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
    }
    """
    confidence = Extension.construct()
    confidence.url = insight_constants.INSIGHT_CONFIDENCE_URL

    confidence_name = Extension.construct()
    confidence_name.url = insight_constants.INSIGHT_CONFIDENCE_NAME_URL
    confidence_name.valueString = name

    confidence_score = Extension.construct()
    confidence_score.url = insight_constants.INSIGHT_CONFIDENCE_SCORE_URL
    confidence_score.valueDecimal = value

    confidence.extension = [confidence_name]
    confidence.extension.append(confidence_score)
    return confidence


def create_derived_by_nlp_extension() -> Extension:
    """Creates a category extension indicating the element is derived from NLP

    See the IG Documentation for the structure of the category:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-category.html

    Example:
    >>> print(create_derived_by_nlp_extension().json(indent=2))
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
    classification_ext.url = insight_constants.INSIGHT_CATEGORY_URL
    classification_coding = create_coding(
        insight_constants.CLASSIFICATION_DERIVED_SYSTEM,
        insight_constants.CLASSIFICATION_DERIVED_CODE,
        insight_constants.CLASSIFICATION_DERIVED_DISPLAY,
    )
    classification_value = CodeableConcept.construct()
    classification_value.coding = [classification_coding]
    classification_value.text = insight_constants.CLASSIFICATION_DERIVED_DISPLAY
    classification_ext.valueCodeableConcept = classification_value
    return classification_ext


def create_nlp_output_extension(output_url: str) -> Extension:
    """
    Creates an extension documenting the location of the NLP engine's output.

    This is an evaluated output extension that is defined by the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-evaluated-output.html

    Returns: NLP output extension

    Example:
    >>> ext = create_nlp_output_extension("uri://path/abc-123.json")
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
      "valueAttachment": {
        "url": "uri://path/abc-123.json"
      }
    }
    """
    attachment = Attachment.construct()
    attachment.url = output_url

    nlp_output_ext = Extension.construct()
    nlp_output_ext.url = insight_constants.INSIGHT_NLP_OUTPUT_URL
    nlp_output_ext.valueAttachment = attachment

    return nlp_output_ext


def create_derived_from_concept_insight_detail_extension(
    reference_path_ext: Extension,
    evaluated_output_ext: Optional[Extension] = None,
) -> Extension:
    """Creates an insight detail extension that includes NLP extensions

    This is used to indicate that a resource has been enhanced with
    additional codings/insights, by running NLP over existing concepts
    in the resource.

    The insight detail extension is described in the IG by:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-detail.html

    Args:
        reference_path_ext  - path to derived from source
        evaluated_output_ext - optional additional insight data from NLP

    Returns:
        the extension

    Example:
    >>> nlp_extensions = (
    ...                   Extension.construct(
    ...                    url='http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output')
    ...                  )
    >>> reference_path_ext = create_reference_path_extension('AllergyIntolerance.code')
    >>> ext = create_derived_from_concept_insight_detail_extension(reference_path_ext, nlp_extensions)
    >>> print(ext.json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output"
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
          "valueString": "AllergyIntolerance.code"
        }
      ],
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
    }
    """
    insight_detail = Extension.construct()
    insight_detail.url = insight_constants.INSIGHT_DETAIL_URL
    if insight_detail.extension is None:
        insight_detail.extension = []

    if evaluated_output_ext:
        insight_detail.extension.append(evaluated_output_ext)

    if reference_path_ext:
        insight_detail.extension.append(reference_path_ext)

    return insight_detail


def create_derived_from_unstructured_insight_detail_extension(
    source: TextFragment,
    confidences: Optional[List[Extension]] = None,
    evaluated_output_ext: Optional[Extension] = None,
) -> Extension:
    """Creates an insight detail extension for a derived resource

    The derived resource is expected to have been derived based on unstructured data in
    the source resource.

    The structure of the insight detail is defined in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-insight-detail.html

    Args:
        source - the resource containing the unstructured data used to derive the insight resource
        confidences - optional confidence extensions associated with the insight
        evaluated_output_ext - optional evaluated output extension
                        (contains the raw data structure returned from NLP)

    Example:
    >>> visit_code = CodeableConcept.construct(text='Mental status Narrative')
    >>> report_text = 'crazy, no other way to describe'
    >>> report = DiagnosticReport.construct(id='12345',
    ...                                     code=visit_code,
    ...                                     text=report_text)
    >>> source = TextFragment(text_source=UnstructuredText(report, "path_to_text", report_text),
    ...                       text_span=Span(begin=0,end=5,covered_text='crazy'))
    >>> confidences = [ create_confidence_extension('Suspected Score', .99) ]
    >>> nlp_extension = (
    ...                  Extension.construct(
    ...                   url='http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output')
    ...                 )
    >>> extension = create_derived_from_unstructured_insight_detail_extension(source,
    ...                                                                       confidences,
    ...                                                                       nlp_extension)
    >>> print(extension.json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output"
        },
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
          "valueReference": {
            "reference": "DiagnosticReport/12345"
          }
        },
        {
          "extension": [
            {
              "extension": [
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                  "valueString": "crazy"
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
                  "valueInteger": 0
                },
                {
                  "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                  "valueInteger": 5
                },
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
                      "valueString": "Suspected Score"
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
      ],
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-detail"
    }
    """
    insight_span_ext = create_insight_span_extension(source.text_span)

    if confidences:
        if insight_span_ext.extension is None:
            insight_span_ext.extension = []
        insight_span_ext.extension.extend(confidences)
    else:
        pass

    # Unstructured results extension
    insight_results = Extension.construct()
    insight_results.url = insight_constants.INSIGHT_RESULT_URL
    insight_results.extension = [insight_span_ext]

    # Create reference to unstructured report
    report_reference_ext = create_reference_to_resource_extension(
        source.text_source.source_resource
    )

    insight_detail = Extension.construct()
    insight_detail.url = insight_constants.INSIGHT_DETAIL_URL
    insight_detail.extension = [evaluated_output_ext] if evaluated_output_ext else []
    insight_detail.extension.extend([report_reference_ext, insight_results])

    return insight_detail


def create_insight_span_extension(span: Span) -> Extension:
    """Creates an extension for a span of text.

    The span is assumed to be from a reference source that was used as input for
    insight evaluation.

    The span extension is defined in the IG at:
    https://alvearie.io/alvearie-fhir-ig/StructureDefinition-span.html

    Example:
     >>> extension = create_insight_span_extension(
     ...                 Span(begin=100,
     ...                      end=123,
     ...                      covered_text='this is my covered Text')
     ...             )
     >>> print(extension.json(indent=2))
     {
       "extension": [
         {
           "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
           "valueString": "this is my covered Text"
         },
         {
           "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-begin",
           "valueInteger": 100
         },
         {
           "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
           "valueInteger": 123
         }
       ],
       "url": "http://ibm.com/fhir/cdm/StructureDefinition/span"
     }
    """
    offset_begin_ext = Extension.construct()
    offset_begin_ext.url = insight_constants.INSIGHT_SPAN_OFFSET_BEGIN_URL
    offset_begin_ext.valueInteger = span.begin

    offset_end_ext = Extension.construct()
    offset_end_ext.url = insight_constants.INSIGHT_SPAN_OFFSET_END_URL
    offset_end_ext.valueInteger = span.end

    covered_text_ext = Extension.construct()
    covered_text_ext.url = insight_constants.INSIGHT_SPAN_COVERED_TEXT_URL
    covered_text_ext.valueString = span.covered_text

    insight_span_ext = Extension.construct()
    insight_span_ext.url = insight_constants.INSIGHT_SPAN_URL
    insight_span_ext.extension = [covered_text_ext]
    insight_span_ext.extension.append(offset_begin_ext)
    insight_span_ext.extension.append(offset_end_ext)

    return insight_span_ext


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
    >>> ext = create_insight_id_extension("insight-1", "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/0.0.2")
    >>> print(ext.json(indent=2))
    {
      "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
      "valueIdentifier": {
        "system": "urn:id:alvearie.io/patterns/QuickUMLS_v1.4.0/0.0.2",
        "value": "insight-1"
      }
    }
    """
    insight_id_ext = Extension.construct()
    insight_id_ext.url = insight_constants.INSIGHT_ID_URL

    insight_id = Identifier.construct()
    insight_id.system = insight_system
    insight_id.value = insight_id_value

    insight_id_ext.valueIdentifier = insight_id
    return insight_id_ext
