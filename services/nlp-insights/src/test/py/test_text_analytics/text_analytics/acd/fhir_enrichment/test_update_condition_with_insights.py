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
from fhir.resources.bundle import Bundle
from fhir.resources.condition import Condition
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    ContainerAnnotation,
)

from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics.insight_source.concept_text_adjustment import AdjustedConceptRef
from text_analytics.insight_source.fields_of_interest import (
    CodeableConceptRef,
    CodeableConceptRefType,
)
from text_analytics.nlp.acd.fhir_enrichment.enrich_fhir_resource import (
    enrich_resource_codeable_concepts,
)
from text_analytics.nlp.acd.fhir_enrichment.insights.update_codeable_concepts import (
    update_codeable_concepts_and_meta_with_insights,
    AcdConceptRef,
)

from text_analytics.nlp.nlp_config import ACD_NLP_CONFIG_CDP_V1_0


# Note: Not testing path where existing condition resource does not produce insights as this is common code with allergy and immunization
class EnhanceConditionWithInsightsTest(UnitTestUsingExternalResource):
    def _check_results(
        self, condition, acd_result, expected_output_condition, full_output
    ):
        """
        This method assumes a single FHIR resource will be updated, and verifies that resource against the expected resource.
        Parmeters:
          condition - FHIR condition to add insights to
          acd_result - ACD ContainerAnnotation, used for mock ACD output
          expected_output_condition - updated FHIR condition expected after insights added
          full_output (boolean) - if True, will output the full expected and actual results if they do not match
        """

        ai_results = [
            AcdConceptRef(
                adjusted_concept=AdjustedConceptRef(
                    concept_ref=CodeableConceptRef(
                        type=CodeableConceptRefType.CONDITION,
                        code_ref=condition.code,
                        fhir_path="Condition.code",
                    ),
                    adjusted_text=condition.code.text,
                ),
                acd_response=acd_result,
            )
        ]

        update_codeable_concepts_and_meta_with_insights(
            condition, ai_results, ACD_NLP_CONFIG_CDP_V1_0
        )

        differences = DeepDiff(
            expected_output_condition, condition, verbose_level=2
        ).pretty()
        if full_output:
            expected_str = "\n\nEXPECTED RESULTS:\n" + expected_output_condition.json()
            actual_str = "\n\nACTUAL RESULTS:\n" + condition.json()
            self.assertEqual(differences, "", expected_str + actual_str)
        else:
            self.assertEqual(differences, "")

    def test_insights_added(self):
        """
        Tests insights found for an condition.
        """
        input_resource = Condition.parse_file(
            self.resource_path + "/acd/mock_fhir/input/Condition_sleep_apnea.json"
        )
        expected_output = Condition.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/update_structured/Condition_sleep_apnea.json"
        )

        with open(
            self.resource_path + "/acd/mock_acd_output/condition_sleep_apnea.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_result = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._check_results(input_resource, acd_result, expected_output, True)

    def _condition_bundle_update(self, input_json, expected_json, acd_result):
        """
        Tests enrich_fhir_resource correctly identifies as Condition and creates bundle
        """
        condition = Condition.parse_file(input_json)

        if expected_json is not None:
            expected_bundle = Bundle.parse_file(expected_json)
        else:
            expected_bundle = None

        ai_results = [
            AcdConceptRef(
                adjusted_concept=AdjustedConceptRef(
                    concept_ref=CodeableConceptRef(
                        type=CodeableConceptRefType.CONDITION,
                        code_ref=condition.code,
                        fhir_path="Condition.code",
                    ),
                    adjusted_text=condition.code.text,
                ),
                acd_response=acd_result,
            )
        ]

        actual_bundle = enrich_resource_codeable_concepts(ai_results, condition)

        if expected_bundle is None:
            self.assertTrue(actual_bundle is None, "Expected no condition created")
        else:
            differences = DeepDiff(expected_bundle, actual_bundle, verbose_level=2)

            # Differences str should be empty if results match expected
            self.assertEqual(
                differences,
                {},
                "Results do not match expected.\nDIFFERENCES:\n"
                + str(differences)
                + "\nEXPECTED RESULTS:\n"
                + expected_bundle.json()
                + "\nACTUAL RESULTS:\n"
                + actual_bundle.json(),
            )

    def test_single_resource_update_condition(self):
        """
        Tests enrich_fhir_resource correctly identifies as condition and creates bundle
        """
        input_json = (
            self.resource_path + "/acd/mock_fhir/input/Condition_sleep_apnea.json"
        )
        expected_json = (
            self.resource_path
            + "/acd/mock_fhir/output/update_structured/Bundle_update_condition_sleep_apnea.json"
        )
        with open(
            self.resource_path + "/acd/mock_acd_output/condition_sleep_apnea.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_result = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._condition_bundle_update(input_json, expected_json, acd_result)


if __name__ == "__main__":
    unittest.main()
