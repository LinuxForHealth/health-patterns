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
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.medicationstatement import MedicationStatement
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
    create_med_statements_from_insights,
)
from text_analytics.nlp.nlp_config import ACD_NLP_CONFIG_CDP_V1_0


class CreateMedStatementFromInsightTest(UnitTestUsingExternalResource):
    """Testcases for creating medication resources from reports"""

    def _check_results(
        self, input_diagnostic_report, acd_output, expected_med_statement, full_output
    ):
        """
        This method assumes a single FHIR resource will be created, and verifies that resource against the expected resource.
        Parmeters:
          input_diagnostic_report - FHIR DiagnosticReport used for NLP input
          acd_output_file - ACD ContainerAnnotation, used for mock ACD output
          expected_med_statement - FHIR MedicationStatement with expected results
          full_output (boolean) - if True, will output the full expected and actual results if they do not match
        """
        actual_results = create_med_statements_from_insights(
            UnstructuredText(
                source_resource=input_diagnostic_report,
                fhir_path="DiagnosticReport.presentedForm[0].data",
                text=input_diagnostic_report.presentedForm[0].data,
            ),
            acd_output,
            ACD_NLP_CONFIG_CDP_V1_0,
        )

        self.assertIsNotNone(actual_results)
        actual_results = cast(List[MedicationStatement], actual_results)

        self.assertEqual(
            len(actual_results), 1, "Multiple FHIR resources returned, only expecting 1"
        )
        actual_results_dict = actual_results[0].dict()
        blank_acd_evidence_detail_in_resource(actual_results_dict)
        expected_output_dict = expected_med_statement.dict()

        # Differences should be empty if results match expected
        differences = DeepDiff(
            expected_output_dict, actual_results_dict, verbose_level=2
        ).pretty()
        if full_output:
            expected_str = "\n\nEXPECTED RESULTS:\n" + expected_med_statement.json()
            actual_str = "\n\nACTUAL RESULTS:\n" + actual_results[0].json()
            self.assertEqual(differences, "", expected_str + actual_str)
        else:
            self.assertEqual(differences, "")

    def _check_results_in_bundle(
        self, input_diagnostic_report, acd_output_file, expected_bundle, full_output
    ):
        """
        Parameters:
          input_diagnostic_report - FHIR DiagnosticReport used for NLP input
          acd_output_file - ACD ContainerAnnotation, used for mock ACD output
          expected_bundle - FHIR Bundle with expected results
          full_output (boolean) - if True, will output the full expected and actual results if they do not match
        """
        mock_acd_response = ContainerAnnotation()
        with open(acd_output_file, "r", encoding="utf-8") as f:
            mock_acd_response = ContainerAnnotation.from_dict(json.loads(f.read()))

        # Call code to call ACD and add insights
        actual_results = create_new_resources_from_insights(
            UnstructuredText(
                source_resource=input_diagnostic_report,
                fhir_path="DiagnosticReport.presentedForm[0].data",
                text=input_diagnostic_report.presentedForm[0].data,
            ),
            mock_acd_response,
        )
        actual_results_dict = actual_results.dict()
        blank_acd_evidence_detail_in_bundle(actual_results_dict)

        expected_bundle_dict = expected_bundle.dict()

        # Differences should be empty if results match expected
        differences = DeepDiff(
            expected_bundle_dict, actual_results_dict, verbose_level=2
        ).pretty()
        if full_output:
            expected_str = "\n\nEXPECTED RESULTS:\n" + expected_bundle.json()
            actual_str = "\n\nACTUAL RESULTS:\n" + actual_results.json()
            self.assertEqual(differences, "", expected_str + actual_str)
        else:
            self.assertEqual(differences, "")

    def test_single_med_statement_insight(self):
        """
        Create a new MedicationStatement FHIR resource from a single insight in a diagnostic report.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_med_statement = MedicationStatement.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/MedicationStatement_metformin.json"
        )

        with open(
            self.resource_path + "/acd/mock_acd_output/medication_metformin.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_output = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._check_results(
            input_diagnostic_report, acd_output, expected_med_statement, True
        )

    def test_med_statement_no_dosage(self):
        """
        Create a new MedicationStatement FHIR resource when there is no dosage detected.
        """

        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_med_statement = MedicationStatement.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/MedicationStatement_no_dosage.json"
        )

        with open(
            self.resource_path + "/acd/mock_acd_output/medication_no_dosage.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_output = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._check_results(
            input_diagnostic_report, acd_output, expected_med_statement, True
        )

    def test_multiple_medication_spans(self):
        """
        Create a new Medication Statement FHIR resource from a single insight in a diagnostic report.
        This tests a report with a single medication with multiple annotations (spans).
        This report includes 3 instances of the medication, 2 of which have dosages associated with them.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_med_statement = MedicationStatement.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/MedicationStatement_metformin_multipleAnnotations.json"
        )

        with open(
            self.resource_path
            + "/acd/mock_acd_output/medication_metformin_multiple.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_output = ContainerAnnotation.from_dict(json.loads(f.read()))
        self._check_results(
            input_diagnostic_report, acd_output, expected_med_statement, True
        )

    def test_multiple_medication_insights(self):
        """
        :test_procedure: test_multiple_condition_insights
        Create new MedicationStatement FHIR resources for multiple insights in a diagnostic report.
        This test_text_analytics a report with multiple DIFFERENT medications, each with a single annotation.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_bundle = Bundle.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/Bundle_create_multiple_MedicationStatement.json"
        )
        mock_acd_output_path = (
            self.resource_path + "/acd/mock_acd_output/medication_multiple.json"
        )
        self._check_results_in_bundle(
            input_diagnostic_report, mock_acd_output_path, expected_bundle, True
        )

    def test_no_medication_insight(self):
        """
        Test no MedicationStatement is created if no medication insights were found in the diagnostic report.
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
        actual_results = create_med_statements_from_insights(
            input_diagnostic_report, acd_output, ACD_NLP_CONFIG_CDP_V1_0
        )
        self.assertEqual(actual_results, None, "Expected no results but got something")


if __name__ == "__main__":
    unittest.main()
