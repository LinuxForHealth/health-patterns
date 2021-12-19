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
"""Defines a common mechanism for building insights

   The builder classes are designed to combine the alvearie extensions together in
   meaningful ways, and to simplify the construction of complex insights.

   The structure is mutable and may be modified prior to creating the extensions.

   Example for creating a condition from a diagnostics report:
    >>> import base64
    >>> from fhir.resources.attachment import Attachment
    >>> from fhir.resources.codeableconcept import CodeableConcept
    >>> from fhir.resources.diagnosticreport import DiagnosticReport

    >>> visit_code = CodeableConcept.construct(text='Chief complaint Narrative - Reported')
    >>> report_text = 'Patient is diabetic'
    >>> report_attachment = Attachment.construct(contentType="text/plain",
    ...                                          data=base64.b64encode(report_text.encode("utf-8")))
    >>> report = DiagnosticReport.construct(id='12345',
    ...                                     status='final',
    ...                                     code=visit_code,
    ...                                     presentedForm=[report_attachment])

    >>> insight = InsightBuilder(
    ...             identifier=InsightIdBuilder(system="urn:alvearie.io/health_patterns/services/nlp_insights/",
    ...                                         value="nlp-insight-1"),
    ...             path=FhirPath("Condition"),
    ...             details=[
    ...                 InsightDetailBuilder(
    ...                     reference=report,
    ...                     reference_path=FhirPath("DiagnosticReport.presentedForm[0].data"),
    ...                     insight_results=[
    ...                         InsightResultBuilder(spans=[InsightSpanBuilder(
    ...                                                         Span(begin=0,
    ...                                                              end=10,
    ...                                                              covered_text="hello_world"),
    ...                                                         confidences=[
    ...                                                                InsightConfidenceBuilder(
    ...                                                                     method=ConfidenceMethod("urn:confidence-system",
    ...                                                                                             "confidence-method"),
    ...                                                                     score=.99,
    ...                                                                     description="confidence score description"
    ...                                                                     )
    ...                                                         ]
    ...                                                     )
    ...                                                    ]
    ...                                             )
    ...                     ]
    ...                 )
    ...             ]
    ... )

    >>> print(insight.build_extension().json(indent=2))
    {
      "extension": [
        {
          "url": "http://ibm.com/fhir/cdm/StructureDefinition/insight-id",
          "valueIdentifier": {
            "system": "urn:alvearie.io/health_patterns/services/nlp_insights/",
            "value": "nlp-insight-1"
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
              "extension": [
                {
                  "extension": [
                    {
                      "url": "http://ibm.com/fhir/cdm/StructureDefinition/covered-text",
                      "valueString": "hello_world"
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
                                "code": "confidence-method",
                                "system": "urn:confidence-system"
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
                          "valueString": "confidence score description"
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
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import dataclasses
from typing import Optional, List, NamedTuple

from fhir.resources.extension import Extension
from fhir.resources.resource import Resource

from nlp_insights.fhir import alvearie_ext
from nlp_insights.fhir.path import FhirPath
from nlp_insights.insight.span import Span


class ConfidenceMethod(NamedTuple):
    """Method used to compute a confidence"""

    system: str
    method: str


class Builder(ABC):  # pylint: disable=too-few-public-methods

    """Root builder class"""

    @abstractmethod
    def build_extension(self) -> Extension:
        """Creates the alvearie extension associated with the builder"""


@dataclass
class InsightIdBuilder(Builder):
    """Identifier for an insight"""

    system: str
    value: str

    def build_extension(self) -> Extension:
        return alvearie_ext.create_insight_id_extension(self.value, self.system)


@dataclass
class InsightConfidenceBuilder(Builder):
    """confidence"""

    method: ConfidenceMethod
    score: float
    description: str

    def build_extension(self) -> Extension:
        description_ext = None

        if self.description:
            description_ext = alvearie_ext.create_scoring_description_extension(
                self.description
            )

        method_ext = None
        if self.method:
            method_ext = alvearie_ext.create_scoring_method_extension(
                self.method.system,
                self.method.method,
            )

        return alvearie_ext.create_insight_confidence_extension(
            scoring_method=method_ext,
            score=alvearie_ext.create_score_extension(self.score),
            scoring_description=description_ext,
        )


@dataclass
class InsightSpanBuilder(Builder):
    """Records Span and confidences"""

    span: Span
    confidences: List[InsightConfidenceBuilder] = dataclasses.field(
        default_factory=list
    )

    def build_extension(self) -> Extension:
        return self.span.create_alvearie_extension(
            confidences=[c.build_extension() for c in self.confidences]
        )


@dataclass
class InsightResultBuilder(Builder):
    """insight result"""

    spans: List[InsightSpanBuilder] = dataclasses.field(default_factory=list)

    def build_extension(self) -> Extension:
        return alvearie_ext.create_insight_result_extension(
            [s.build_extension() for s in self.spans]
        )


@dataclass
class InsightEvaluatedOutputBuilder(Builder):
    """Builds the evaluated output for an NLP response"""

    nlp_response_json: str

    def build_extension(self) -> Extension:
        return alvearie_ext.create_evaluated_output_extension(
            self.nlp_response_json.encode("utf-8")
        )


@dataclass
class InsightDetailBuilder(Builder):
    """insight detail extension"""

    reference: Resource
    reference_path: FhirPath
    evaluated_output: Optional[InsightEvaluatedOutputBuilder] = None
    insight_results: List[InsightResultBuilder] = dataclasses.field(
        default_factory=list
    )

    def build_extension(self) -> Extension:
        return alvearie_ext.create_insight_detail_extension(
            alvearie_ext.create_reference_extension(self.reference),
            alvearie_ext.create_reference_path_extension(self.reference_path),
            self.evaluated_output.build_extension() if self.evaluated_output else None,
            [result.build_extension() for result in self.insight_results],
        )


@dataclass
class InsightBuilder(Builder):
    """insight"""

    identifier: InsightIdBuilder
    path: Optional[FhirPath] = None
    details: Optional[List[InsightDetailBuilder]] = None

    def build_extension(self) -> Extension:
        details_ext = (
            [d.build_extension() for d in self.details] if self.details else None
        )
        return alvearie_ext.create_insight_extension(
            self.identifier.build_extension(),
            alvearie_ext.create_path_extension(self.path) if self.path else None,
            details_ext,
        )
