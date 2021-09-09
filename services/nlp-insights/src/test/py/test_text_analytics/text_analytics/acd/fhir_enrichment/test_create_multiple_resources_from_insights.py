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
"""Tests with a focus on multiple types of resources being derived from the same source resource.
"""

import json
import unittest

from deepdiff import DeepDiff
from fhir.resources.bundle import Bundle
from fhir.resources.diagnosticreport import DiagnosticReport
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    ContainerAnnotation,
)

from test_text_analytics.util.blank import blank_acd_evidence_detail_in_bundle
from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics.insight_source.unstructured_text import UnstructuredText
from text_analytics.nlp.acd.fhir_enrichment.enrich_fhir_resource import (
    create_new_resources_from_insights,
)


class CreateMutltipleResourceFromInsightTest(UnitTestUsingExternalResource):
    """Test cases that focus on multiple resource types being derived at the same time"""

    def _check_results_in_bundle(
        self,
        input_diagnostic_report,
        acd_output_file,
        expected_output_bundle,
        full_output,
    ):
        """
        Parmeters:
          input_diagnostic_report - FHIR DiagnosticReport used for NLP input
          acd_output_file - ACD ContainerAnnotation, used for mock ACD output
          expected_output_bundle - FHIR Bundle with expected results
          full_output (boolean) - if True, will output the full expected and actual results if they do not match
        """
        acd_result = ContainerAnnotation()
        with open(acd_output_file, "r", encoding="utf-8") as f:
            acd_result = ContainerAnnotation.from_dict(json.loads(f.read()))

        # Call code to call ACD and add insights
        actual_results = create_new_resources_from_insights(
            UnstructuredText(
                source_resource=input_diagnostic_report,
                fhir_path="DiagnosticReport.presentedForm[0].data",
                text=input_diagnostic_report.presentedForm[0].data,
            ), acd_result
        )
        actual_results_dict = actual_results.dict()
        blank_acd_evidence_detail_in_bundle(actual_results_dict)

        expected_output_dict = expected_output_bundle.dict()

        differences = DeepDiff(
            expected_output_dict, actual_results_dict, verbose_level=2
        ).pretty()
        if full_output:
            expected_str = "\n\nEXPECTED RESULTS:\n" + expected_output_bundle.json()
            actual_str = "\n\nACTUAL RESULTS:\n" + actual_results.json()
            self.assertEqual(differences, "", expected_str + actual_str)
        else:
            self.assertEqual(differences, "")

    def test_multiple_mixed_insights(self):
        """
        Create new Condition and Medication FHIR resources for multiple insights of mixed types in a diagnostic report.
        This tests a report with multiple kinds of insights which create different resource types.
        """
        input_diagnostic_report = DiagnosticReport.parse_file(
            self.resource_path + "/acd/mock_fhir/input/DiagnosticReport.json"
        )
        expected_bundle = Bundle.parse_file(
            self.resource_path + "/acd/mock_fhir/output/Multiple_Mixed_Insights.json"
        )
        mock_acd_output_path = (
            self.resource_path + "/acd/mock_acd_output/Multiple_Mixed.json"
        )
        self._check_results_in_bundle(
            input_diagnostic_report, mock_acd_output_path, expected_bundle, True
        )


if __name__ == "__main__":
    unittest.main()
