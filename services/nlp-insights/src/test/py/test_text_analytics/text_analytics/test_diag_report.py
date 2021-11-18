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
"""Testcases related to sending a diagnostic report to the service"""
# pylint: disable=missing-function-docstring
import importlib


from fhir.resources.bundle import Bundle

from test_text_analytics.util.compare import compare_actual_to_expected
from test_text_analytics.util.fhir import (
    make_diag_report,
    make_attachment,
    make_bundle,
    make_patient_reference,
)
from test_text_analytics.util.mock_service import (
    make_mock_acd_service_class,
    configure_acd,
)
from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics import app


DIAG_REPORT_TEXT_FOR_CONDITIONS = (
    "Patient has pneumonia and shows signs of heart attack"
)

DIAG_REPORT_TEXT_FOR_MEDICATIONS = "Patient started taking beta blockers"

DIAG_REPORT_TEXT_FOR_MEDICATIONS_AND_CONDITIONS = (
    ""
    + "Patient has pneumonia and shows signs of heart attack. Patient started taking beta blockers."
)


class TestDiagReportUsingAcd(UnitTestUsingExternalResource):
    """Unit tests where a diagnostic report is posted for insights"""

    def setUp(self) -> None:
        # The application is defined globally in the module, so this is a potentially
        # flawed way of reseting the state between test cases.
        # It should work "well-enough" in most cases.
        importlib.reload(app)
        app.all_nlp_services["acd"] = make_mock_acd_service_class(
            self.resource_path + "/acd/TestReportResponses.json"
        )

    def test_when_post_diag_with_no_text_then_empty_bundle(self):
        report = make_diag_report(subject=make_patient_reference())

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", json=report.dict())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            self.assertEqual(0, len(actual_bundle.entry))

    def test_when_post_diag_bundle_with_no_text_then_empty_bundle(self):
        bundle = make_bundle([make_diag_report(subject=make_patient_reference())])

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", json=bundle.dict())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            self.assertEqual(0, len(actual_bundle.entry))

    def test_when_post_diag_then_condition_derived(self):
        report = make_diag_report(
            subject=make_patient_reference(),
            attachments=[make_attachment(DIAG_REPORT_TEXT_FOR_CONDITIONS)],
        )

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", data=report.json())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            cmp = compare_actual_to_expected(
                expected_path=self.expected_output_path(),
                actual_resource=actual_bundle,
            )
            self.assertFalse(cmp, cmp.pretty())

    def test_when_post_diag_bundle_then_condition_derived(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[make_attachment(DIAG_REPORT_TEXT_FOR_CONDITIONS)],
                )
            ]
        )

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", data=bundle.json())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            cmp = compare_actual_to_expected(
                expected_path=self.expected_output_path(),
                actual_resource=actual_bundle,
            )
            self.assertFalse(cmp, cmp.pretty())

    def test_when_post_diag_bundle_then_medication_derived(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[make_attachment(DIAG_REPORT_TEXT_FOR_MEDICATIONS)],
                )
            ]
        )

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", data=bundle.json())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            cmp = compare_actual_to_expected(
                expected_path=self.expected_output_path(),
                actual_resource=actual_bundle,
            )
            self.assertFalse(cmp, cmp.pretty())

    def test_when_post_diag_bundle_then_medication_and_condition_derived(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(DIAG_REPORT_TEXT_FOR_MEDICATIONS_AND_CONDITIONS)
                    ],
                )
            ]
        )

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", data=bundle.json())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            cmp = compare_actual_to_expected(
                expected_path=self.expected_output_path(),
                actual_resource=actual_bundle,
            )
            self.assertFalse(cmp, cmp.pretty())
