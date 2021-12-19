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
""""
Defines the structure and contents of an insight that derives a new resource.

Using this module encourages consistent construction of insight extensions within derived
resources.

Example of a condition resource that was derived from a diagnostic report:
    Additional imports required for the example:
     >>> import base64
     >>> from fhir.resources.attachment import Attachment
     >>> from fhir.resources.codeableconcept import CodeableConcept
     >>> from fhir.resources.condition import Condition
     >>> from fhir.resources.diagnosticreport import DiagnosticReport
     >>> from fhir.resources.reference import Reference
     >>> from nlp_insights.fhir.insight_builder import ConfidenceMethod

    Create example diagnostic Report:
     >>> visit_code = CodeableConcept.construct(text='Chief complaint Narrative - Reported')
     >>> report_text = 'Patient is diabetic'
     >>> report_attachment = Attachment.construct(contentType="text/plain",
     ...                                          data=base64.b64encode(report_text.encode("utf-8")))
     >>> report = DiagnosticReport.construct(id='12345',
     ...                                     status='final',
     ...                                     code=visit_code,
     ...                                     subject=Reference.construct(reference="Patient/9999"),
     ...                                     presentedForm=[report_attachment])

    Create example derived Condition:
     >>> condition = Condition.construct(id="12345",
     ...                                 subject=Reference.construct(reference="Patient/9999"),
     ...                                 code=CodeableConcept.construct(text="Diabetes"))

    Create Insight:
     >>> insight = DerivedResourceInsightBuilder(
     ...               Condition,
     ...               UnstructuredText(source_resource=report,
     ...                                text_path=FhirPath("DiagnosticReport.presentedForm[0].data"),
     ...                                text=report_text),
     ...               insight_id_value="nlp-insights-1",
     ...               insight_id_system="urn:alvearie.io/health_patterns/services/nlp_insights/",
     ...               nlp_response_json='{"nlp_response_field" : "example nlp response data"}')

    Add Span with two confidence scores:
     >>> confidences=[
     ...              InsightConfidenceBuilder(
     ...                  method=ConfidenceMethod(
     ...                             system="http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method",
     ...                             method="Diagnosis_Explicit_Score"
     ...                         ),
     ...                  score=1.0,
     ...                  description="Diagnosis explicit score"
     ...              ),
     ...              InsightConfidenceBuilder(
     ...                  method=ConfidenceMethod(
     ...                             system="http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method",
     ...                             method="Diagnosis_Patient_Reported_Score"
     ...                         ),
     ...                  score=0.0,
     ...                  description="Diagnosis patient reported score"
     ...              ),
     ...             ]

     >>> insight.add_span(span=Span(begin=11, end=19, covered_text="diabetic"), confidences=confidences)

    Add insight to condidition's meta:
     >>> insight.append_insight_to_resource_meta(condition)

    Add an insight summary to the condition
     >>> insight.append_summary_extension(condition)

    Final Condition:
    >>> print(condition.json(indent=2))
    {
      "id": "12345",
      "meta": {
        "extension": [
          {
            "extension": [
              {
                "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
                "valueIdentifier": {
                  "system": "urn:alvearie.io/health_patterns/services/nlp_insights/",
                  "value": "nlp-insights-1"
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
                      "data": "eyJubHBfcmVzcG9uc2VfZmllbGQiIDogImV4YW1wbGUgbmxwIHJlc3BvbnNlIGRhdGEifQ=="
                    }
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
                            "valueInteger": 11
                          },
                          {
                            "url": "http://ibm.com/fhir/cdm/StructureDefinition/offset-end",
                            "valueInteger": 19
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
                                "valueDecimal": 1.0
                              },
                              {
                                "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
                                "valueString": "Diagnosis explicit score"
                              }
                            ],
                            "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-confidence"
                          },
                          {
                            "extension": [
                              {
                                "url": "http://ibm.com/fhir/cdm/StructureDefinition/method",
                                "valueCodeableConcept": {
                                  "coding": [
                                    {
                                      "code": "Diagnosis_Patient_Reported_Score",
                                      "system": "http://ibm.com/fhir/cdm/CodeSystem/1.0/acd-confidence-method"
                                    }
                                  ]
                                }
                              },
                              {
                                "url": "http://ibm.com/fhir/cdm/StructureDefinition/score",
                                "valueDecimal": 0.0
                              },
                              {
                                "url": "http://ibm.com/fhir/cdm/StructureDefinition/description",
                                "valueString": "Diagnosis patient reported score"
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
      "extension": [
        {
          "extension": [
            {
              "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
              "valueIdentifier": {
                "system": "urn:alvearie.io/health_patterns/services/nlp_insights/",
                "value": "nlp-insights-1"
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
      ],
      "code": {
        "text": "Diabetes"
      },
      "subject": {
        "reference": "Patient/9999"
      },
      "resourceType": "Condition"
    }
"""

from typing import List
from typing import Optional, Type

from fhir.resources.resource import Resource

from nlp_insights.fhir import alvearie_ext
from nlp_insights.fhir.insight_builder import (
    InsightBuilder,
    InsightResultBuilder,
    InsightIdBuilder,
    InsightDetailBuilder,
    InsightEvaluatedOutputBuilder,
    InsightSpanBuilder,
    InsightConfidenceBuilder,
)
from nlp_insights.fhir.path import FhirPath
from nlp_insights.insight.builder.abstract_builder import ResourceInsightBuilder
from nlp_insights.insight.span import Span
from nlp_insights.insight_source.unstructured_text import UnstructuredText


class DerivedResourceInsightBuilder(
    ResourceInsightBuilder
):  # pylint disable=too-few-public-methods
    """Builder for insight information to be added to a derived FHIR resources's meta

    The insight structure assumes that the resource is derived from a single insight, and that insight
    has a single details section with a single result.

    The result may have zero or more spans, each span containing zero or more confidence scores.

    Spans can be added to the insight after initial construction.
    """

    builder: InsightBuilder

    def __init__(
        self,
        resource_type: Type[Resource],
        text_source: UnstructuredText,
        insight_id_value: str,
        insight_id_system: str,
        nlp_response_json: Optional[str] = None,
    ):  # pylint: disable=too-many-arguments
        """Initializes the builder

        Args:
        resource type - type of resource being derived,
        text_source - the source of the text being used to derive the resource
        insight_id_value - unique value for the insight id
        nlp_config - information about the nlp system in use
        nlp_response_json - raw nlp data
        """
        # create insight
        id_builder = InsightIdBuilder(
            system=insight_id_system,
            value=insight_id_value,
        )

        eval_response_builder = None
        if nlp_response_json:
            eval_response_builder = InsightEvaluatedOutputBuilder(nlp_response_json)

        self._builder = InsightBuilder(
            identifier=id_builder,
            path=FhirPath(resource_type.__name__),
            details=[
                InsightDetailBuilder(
                    reference=text_source.source_resource,
                    reference_path=text_source.text_path,
                    evaluated_output=eval_response_builder,
                    insight_results=[
                        InsightResultBuilder()  # Spans will be added to this
                    ],
                )
            ],
        )

    def add_span(self, span: Span, confidences: List[InsightConfidenceBuilder]) -> None:
        """Adds a span with optional confidences to the insight

        Args: span - span to add
              confidences - list of confidence builders (may be empty)
        """
        if not self.builder.details or not self.builder.details[0].insight_results:
            raise ValueError("Object was not constructed correctly")

        self.builder.details[0].insight_results[0].spans.append(
            InsightSpanBuilder(span=span, confidences=confidences)
        )

    def append_insight_summary_to_resource(self, resource: Resource) -> None:
        """Adds an insight summary extension to the resource indicating that
        this resource was derived by NLP.

        Args:
            resource - resource to add insight summary"""

        summary_ext = alvearie_ext.create_insight_summary_extension(
            insight_id_extension=self.builder.identifier.build_extension(),
            category_extension=alvearie_ext.create_derived_by_nlp_category_extension(),
        )

        if resource.extension is None:
            resource.extension = []

        resource.extension.append(summary_ext)
