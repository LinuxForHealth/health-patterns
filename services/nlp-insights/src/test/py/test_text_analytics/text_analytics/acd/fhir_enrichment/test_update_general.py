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
import json
import unittest

from deepdiff import DeepDiff
from fhir.resources.immunization import Immunization
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    ContainerAnnotation,
)

from test_text_analytics.util.blank import (
    blank_acd_evidence_detail_in_resource,
)
from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics.insight_source.concept_text_adjustment import AdjustedConceptRef
from text_analytics.insight_source.fields_of_interest import (
    CodeableConceptRef,
    CodeableConceptRefType,
)

from text_analytics.nlp.acd.fhir_enrichment.insights.update_codeable_concepts import (
    update_codeable_concepts_and_meta_with_insights,
    AcdConceptRef,
)

from text_analytics.nlp.nlp_config import ACD_NLP_CONFIG_CDP_V1_0


class update_general_test(UnitTestUsingExternalResource):
    def _check_results(
        self, immunization, acd_output, expected_immunization, full_output
    ):
        """Tests that we handle a resource that already has a meta section correctly.  Issue found here when integrating with
        ingestion pipeline which generates a resource with a meta section.
        This method assumes a single FHIR resource will be updated, and verifies that resource against the expected resource.
        Parmeters:
          immunization - FHIR Immunization input before insights are added
          acd_output_file - ACD ContainerAnnotation, used for mock ACD output
          expected_immunization - updated FHIR Immunization expected after insights added
          full_output (boolean) - if True, will output the full expected and actual results if they do not match
        """
        acd_results = [
            AcdConceptRef(
                adjusted_concept=AdjustedConceptRef(
                    concept_ref=CodeableConceptRef(
                        type=CodeableConceptRefType.VACCINE,
                        code_ref=immunization.vaccineCode,
                        fhir_path="Immunization.vaccineCode",
                    ),
                    adjusted_text=immunization.vaccineCode.text,
                ),
                acd_response=acd_output,
            )
        ]

        update_codeable_concepts_and_meta_with_insights(
            immunization, acd_results, ACD_NLP_CONFIG_CDP_V1_0
        )
        actual_results_dict = immunization.dict()
        blank_acd_evidence_detail_in_resource(actual_results_dict)
        expected_output_dict = expected_immunization.dict()

        differences = DeepDiff(
            expected_output_dict, actual_results_dict, verbose_level=2
        ).pretty()
        if full_output:
            expected_str = "\n\nEXPECTED RESULTS:\n" + expected_immunization.json()
            actual_str = "\n\nACTUAL RESULTS:\n" + immunization.json()
            self.assertEqual(differences, "", expected_str + actual_str)
        else:
            self.assertEqual(differences, "")

    # Tests insights found for an immunization.
    def test_insights_added(self):
        input_resource = Immunization.parse_file(
            self.resource_path
            + "/acd/mock_fhir/input/MetaSectionExists_Immunization.json"
        )
        expected_output = Immunization.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/MetaSectionExists_Immunization.json"
        )
        with open(
            self.resource_path + "/acd/mock_acd_output/Immunization.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_output = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._check_results(input_resource, acd_output, expected_output, True)


if __name__ == "__main__":
    unittest.main()
