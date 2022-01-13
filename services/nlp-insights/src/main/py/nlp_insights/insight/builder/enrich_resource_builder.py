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
Defines the structure and contents of an insight that enriched a coding of a resource.

Using this module encourages consistent construction of insights and codings within a
resource that has been enriched by NLP.

Example of a condition resource where NLP derived a UMLS coding.
    Additional imports required for the example:
     >>> from fhir.resources.condition import Condition
     >>> from fhir.resources.reference import Reference
     >>> from fhir.resources.coding import Coding
     >>> from fhir.resources.codeableconcept import CodeableConcept
     >>> from nlp_insights.insight_source.fields_of_interest import CodeableConceptRefType
     >>> from nlp_insights.fhir.path import FhirPath
     >>> from nlp_insights.fhir.reference import ResourceReference

    Create example Condition:
     >>> condition = Condition.construct(id="12345",
     ...                                 subject=Reference.construct(reference="Patient/9999"),
     ...                                 code=CodeableConcept.construct(text="Diabetes"))

    Concept to enrich:
     >>> concept = CodeableConceptRef(type=CodeableConceptRefType.CONDITION,
     ...                              code_ref=condition.code,
     ...                              path=FhirPath("Condition.code"),
     ...                              resource_ref=ResourceReference(condition))

    Derived codings:
     >>> derived_codings = [Coding.construct(
     ...                        system="http://terminology.hl7.org/CodeSystem/umls",
     ...                        code="C0011849",
     ...                        display="Diabetes"
     ...                    ),
     ...                   ]

    Create Insight:
     >>> insight = EnrichedResourceInsightBuilder(
     ...               enriched_concept=concept,
     ...               insight_id_value="nlp-insights-1",
     ...               insight_id_system="urn:alvearie.io/health_patterns/services/nlp_insights/",
     ...               nlp_response_json='{"nlp_response_field" : "example nlp response data"}')
     ...           )

     Add codings (with summary extension) to condition's code (defined by the concept reference):
     >>> insight.add_derived_codings(derived_codings)

    Retrieve number of summary extensions added to codings:
    >>> print(insight.num_summary_extensions_added)
    1

    The number of summary extensions might be different than the number of derived codings.
    For example no extension is added when:
    - The coding exists and was not derived
    - The coding exists and was derived for an insight with the same id (in other words rerun of this insight)
    An extension is added when:
    - The coding did not exist and was added for this insight
    - The coding exists and has a summary extension for a different insight id.

     Add insight to meta:
     >>> insight.append_insight_to_resource_meta()

    Final condition:
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
                "valueString": "Condition.code.coding"
              },
              {
                "extension": [
                  {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference",
                    "valueReference": {
                      "reference": "Condition/12345"
                    }
                  },
                  {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/reference-path",
                    "valueString": "Condition.code.text"
                  },
                  {
                    "url": "http://ibm.com/fhir/cdm/StructureDefinition/evaluated-output",
                    "valueAttachment": {
                      "contentType": "application/json",
                      "data": "eyJubHBfcmVzcG9uc2VfZmllbGQiIDogImV4YW1wbGUgbmxwIHJlc3BvbnNlIGRhdGEifQ=="
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
        "coding": [
          {
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
            "code": "C0011849",
            "display": "Diabetes",
            "system": "http://terminology.hl7.org/CodeSystem/umls"
          }
        ],
        "text": "Diabetes"
      },
      "subject": {
        "reference": "Patient/9999"
      },
      "resourceType": "Condition"
    }
"""
from typing import List
from typing import Optional
from typing import Union

from fhir.resources.coding import Coding
from fhir.resources.element import Element
from fhir.resources.extension import Extension
from fhir.resources.resource import Resource
from nlp_insights.fhir import fhir_object_utils
from nlp_insights.fhir.insight_builder import (
    InsightBuilder,
    InsightIdBuilder,
    InsightDetailBuilder,
    InsightEvaluatedOutputBuilder,
)

from nlp_insights.insight.builder import abstract_builder
from nlp_insights.insight_source.fields_of_interest import CodeableConceptRef


class EnrichedResourceInsightBuilder(
    abstract_builder.ResourceInsightBuilder
):  # pylint disable=too-few-public-methods
    """Builder for an enriched FHIR resource's insight

    Enrichement is assumed to involve a single insight, with a single details and results section.

    The result may have zero or more spans, each span containing zero or more confidence scores.

    """

    def __init__(
        self,
        enriched_concept: CodeableConceptRef,
        insight_id_value: str,
        insight_id_system: str,
        nlp_response_json: Optional[str] = None,
    ):  # pylint: disable=too-many-arguments
        """Initializes the builder

        Args:
        resource type - type of resource being derived,
        text_source - the source of the text being used to derive the resource
        cuis - cui or csv of cuis that caused the resource to be derived
        nlp_config - information about the nlp system in use
        nlp_response_json - raw nlp data
        """
        self.enriched_concept = enriched_concept
        self.num_summary_extensions_added = 0

        id_builder = InsightIdBuilder(system=insight_id_system, value=insight_id_value)

        eval_response_builder = None
        if nlp_response_json:
            eval_response_builder = InsightEvaluatedOutputBuilder(nlp_response_json)

        self._builder = InsightBuilder(
            identifier=id_builder,
            path=enriched_concept.path_coding,
            details=[
                InsightDetailBuilder(
                    resource_ref=enriched_concept.resource_ref,
                    reference_path=enriched_concept.path_text,
                    evaluated_output=eval_response_builder,
                )
            ],
        )

    def append_summary_extension(
        self, element: Union[Element, Extension, Resource]
    ) -> None:
        self.num_summary_extensions_added += 1
        super().append_summary_extension(element)

    def append_insight_to_resource_meta(
        self, resource: Optional[Resource] = None
    ) -> None:
        if resource is None or (
            resource == self.enriched_concept.resource_ref.resource
        ):
            super().append_insight_to_resource_meta(
                self.enriched_concept.resource_ref.resource
            )
        else:
            raise ValueError("Resource doesn't match the codeable concept resource!")

    def add_derived_codings(self, derived_codings: List[Coding]) -> None:
        """Enriches the concept"""
        if self.enriched_concept.code_ref.coding is None:
            self.enriched_concept.code_ref.coding = []

        codes = self.enriched_concept.code_ref.coding
        existing_codes = fhir_object_utils.index_codings(codes)

        for dcode in derived_codings:
            existing_code = existing_codes[dcode.system].get(dcode.code, None)
            if existing_code:
                if self.find_summary_extension(existing_code):
                    pass  # already derived this one once before
                elif next(
                    abstract_builder.find_all_summary_extensions(existing_code), None
                ):
                    # Derived by someone else, append us also
                    self.append_summary_extension(existing_code)
                else:
                    # This was not derived by anyone, leave it alone
                    pass
            else:
                # New derived code that we derived
                self.append_summary_extension(dcode)
                codes.append(dcode)
