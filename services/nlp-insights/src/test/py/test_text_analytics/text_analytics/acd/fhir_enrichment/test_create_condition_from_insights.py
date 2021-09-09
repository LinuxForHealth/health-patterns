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
from typing import List
from typing import cast
import unittest

from deepdiff import DeepDiff
from fhir.resources.bundle import Bundle
from fhir.resources.condition import Condition
from fhir.resources.diagnosticreport import DiagnosticReport
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    ContainerAnnotation,
)

from test_text_analytics.util.blank import (
    blank_acd_evidence_detail_in_bundle,
    blank_acd_evidence_detail_in_resource,
)
from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics.insight_source.unstructured_text import UnstructuredText
from text_analytics.nlp.acd.fhir_enrichment.enrich_fhir_resource import (
    create_new_resources_from_insights,
    create_conditions_from_insights,
)
from text_analytics.nlp.nlp_config import ACD_NLP_CONFIG_CDP_V1_0


class TestCreateConditionFromInsights(UnitTestUsingExternalResource):
    """Testcases for creating condition resources from reports"""

    def _create_condition_and_check_results(
        self,
        input_report: DiagnosticReport,
        acd_output: ContainerAnnotation,
        expected_condition: Condition,
        full_output: bool,
    ):
        """Creates conditions from the provided source report and verifies correctness

        This method assumes a single FHIR condition will be created, and verifies that
        condition against the expected resource.

        Args:
          input_report - FHIR DiagnosticReport used for NLP input
          acd_output - ACD ContainerAnnotation, used for mock ACD output
          expected_resource - FHIR Condition with expected results
          full_output (boolean) - if True, will output the full expected and actual results if they do not match
        """

        actual_results = create_conditions_from_insights(
            UnstructuredText(
                source_resource=input_report,
                fhir_path="DiagnosticReport.presentedForm[0].data",
                text=input_report.presentedForm[0].data,
            ),
            acd_output,
            ACD_NLP_CONFIG_CDP_V1_0,
        )

        self.assertTrue(
            actual_results and (len(actual_results) == 1),
            f"Multiple FHIR resources returned, only expecting 1 {str(actual_results)}",
        )
        actual_results = cast(List[Condition], actual_results)
        actual_results_dict = actual_results[0].dict()
        blank_acd_evidence_detail_in_resource(actual_results_dict)
        expected_output_dict = expected_condition.dict()
        differences = DeepDiff(
            expected_output_dict, actual_results_dict, verbose_level=2
        ).pretty()
        if full_output:
            expected_str = "\n\nEXPECTED RESULTS:\n" + expected_condition.json()
            actual_str = "\n\nACTUAL RESULTS:\n" + actual_results[0].json()
            self.assertEqual(differences, "", expected_str + actual_str)
        else:
            self.assertEqual(differences, "")

    def _create_bundle_and_check_results(
        self,
        input_report: DiagnosticReport,
        acd_output_file: str,
        expected_bundle: Bundle,
        full_output: bool,
    ) -> None:
        """Processes a report and ensures that the resulting bundle is as expected

        Args:
          input_report - FHIR DiagnosticReport used for NLP input
          acd_output_file - ACD ContainerAnnotation file with mock ACD output
          expected_output_bundle - FHIR Bundle with expected results
          full_output (boolean) - if True, will output the full expected and
                                  actual results if they do not match
        """
        # mock_acd_response = ContainerAnnotation()
        with open(acd_output_file, "r", encoding="utf-8") as f:
            acd_result = ContainerAnnotation.from_dict(json.loads(f.read()))

        actual_results = create_new_resources_from_insights(
            UnstructuredText(
                source_resource=input_report,
                fhir_path="DiagnosticReport.presentedForm[0].data",
                text=input_report.presentedForm[0].data,
            ),
            acd_result,
        )

        self.assertIsNotNone(actual_results)
        actual_results = cast(Bundle, actual_results)

        actual_results_dict = actual_results.dict()
        blank_acd_evidence_detail_in_bundle(actual_results_dict)

        expected_output_dict = expected_bundle.dict()

        differences = DeepDiff(
            expected_output_dict, actual_results_dict, verbose_level=2
        ).pretty()
        if full_output:
            expected_str = "\n\nEXPECTED RESULTS:\n" + expected_bundle.json()
            actual_str = "\n\nACTUAL RESULTS:\n" + actual_results.json()
            self.assertEqual(differences, "", expected_str + actual_str)
        else:
            self.assertEqual(differences, "")

    def test_single_condition_insight(self):
        """
        Create a new Condition FHIR resource from a single insight in a diagnostic report.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_output_condition = Condition.parse_file(
            self.resource_path + "/acd/mock_fhir/output/Condition.json"
        )

        with open(
            self.resource_path + "/acd/mock_acd_output/Condition.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_output = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._create_condition_and_check_results(
            input_diagnostic_report, acd_output, expected_output_condition, True
        )

    def test_single_resource_bundle(self):
        """
        Creates a bundle with a single Condition resource.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_bundle = Bundle.parse_file(
            self.resource_path + "/acd/mock_fhir/output/Bundle_create_Condition.json"
        )
        mock_acd_output_path = (
            self.resource_path + "/acd/mock_acd_output/Condition.json"
        )
        self._create_bundle_and_check_results(
            input_diagnostic_report, mock_acd_output_path, expected_bundle, True
        )

    def test_multiple_condition_spans(self):
        """
        Create a new Condition FHIR resource from a single insight in a diagnostic report.
        This tests a report with a single condition with multiple annotations (spans).
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_output_condition = Condition.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/Condition_MultipleAnnotations.json"
        )
        with open(
            self.resource_path
            + "/acd/mock_acd_output/Condition_MultipleAnnotations.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_output = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._create_condition_and_check_results(
            input_diagnostic_report, acd_output, expected_output_condition, True
        )

    def test_multiple_condition_insights(self):
        """
        Create new Condition FHIR resources for multiple insights in a diagnostic report.
        This test_text_analytics a report with multiple DIFFERENT conditions, each with a single annotation.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_bundle = Bundle.parse_file(
            self.resource_path + "/acd/mock_fhir/output/Condition_Multiple.json"
        )
        mock_acd_output_path = (
            self.resource_path + "/acd/mock_acd_output/Condition_Multiple.json"
        )
        self._create_bundle_and_check_results(
            input_diagnostic_report, mock_acd_output_path, expected_bundle, True
        )

    def test_multiple_conditions_and_multiple_spans(self):
        """
        Create new Condition FHIR resources from multiple insights in a diagnostic report.
        This test_text_analytics a report with mutliple conditions, each with multiple annotations (spans).
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_bundle = Bundle.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/Condition_Multiple_and_MultipleAnnotations.json"
        )
        mock_acd_output_path = (
            self.resource_path
            + "/acd/mock_acd_output/Condition_Multiple_and_MultipleAnnotations.json"
        )
        self._create_bundle_and_check_results(
            input_diagnostic_report, mock_acd_output_path, expected_bundle, True
        )

    def test_no_condition_insight(self):
        """
        Verify no Condition is created if no condition insights were found in the diagnostic report.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        with open(
            self.resource_path + "/acd/mock_acd_output/Condition_Nothing_Useful.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_output = ContainerAnnotation.from_dict(json.loads(f.read()))
        actual_results = create_conditions_from_insights(
            input_diagnostic_report, acd_output, ACD_NLP_CONFIG_CDP_V1_0
        )
        self.assertEqual(
            actual_results,
            None,
            "Expected no results but got something",
        )


if __name__ == "__main__":
    unittest.main()
