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
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.medicationstatement import MedicationStatement

from nlp_insights import app
from nlp_insights.fhir import alvearie_ext_url
from test_nlp_insights.util import unstructured_text
from test_nlp_insights.util.compare import compare_actual_to_expected
from test_nlp_insights.util.fhir import (
    make_diag_report,
    make_attachment,
    make_bundle,
    make_patient_reference,
)
from test_nlp_insights.util.mock_service import (
    make_mock_acd_service_class,
    configure_acd,
    make_mock_quick_umls_service_class,
    configure_quick_umls,
)
from test_nlp_insights.util.resources import UnitTestUsingExternalResource


class TestDiagReportUsingAcd(UnitTestUsingExternalResource):
    """Unit tests where a diagnostic report is posted for insights"""

    def setUp(self) -> None:
        # The application is defined globally in the module, so this is a potentially
        # flawed way of reseting the state between test cases.
        # It should work "well-enough" in most cases.
        importlib.reload(app)
        app.config.set_mock_nlp_service_class(
            "acd",
            make_mock_acd_service_class(
                self.resource_path + "/acd/TestReportResponses.json"
            ),
        )

    def test_when_post_diag_with_no_text_then_empty_bundle(self):
        report = make_diag_report(subject=make_patient_reference())

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", json=report.dict())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            self.assertEqual(0, len(actual_bundle.entry))

    def test_when_post_diag_bundle_with_no_text_then_nothing_derived(self):
        bundle = make_bundle([make_diag_report(subject=make_patient_reference())])

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", json=bundle.dict())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            self.assertEqual(1, len(actual_bundle.entry))
            cmp = compare_actual_to_expected(
                expected_path=self.expected_output_path(),
                actual_resource=actual_bundle,
            )
            self.assertFalse(cmp, cmp.pretty())

    def test_when_post_diag_then_condition_derived(self):
        report = make_diag_report(
            subject=make_patient_reference(),
            attachments=[
                make_attachment(unstructured_text.TEXT_FOR_MULTIPLE_CONDITIONS)
            ],
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

    def test_when_post_diag_bundle_with_no_fullurl_then_medication_derived(self):
        # Most tests generate the full url because allowing nlp-insights to do
        # this would create non-repeatable values, so here we force nlp-insights
        # to generate the url. And we also do not supply an ID for the diagnostic
        # report
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(unstructured_text.TEXT_FOR_MEDICATION)
                    ],
                    id_val=None,
                )
            ],
            add_full_url=False,
        )

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", data=bundle.json())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())

            assert len(actual_bundle.entry) == 2
            diag_report_entry = next(
                filter(
                    lambda ent: isinstance(ent.resource, DiagnosticReport),
                    actual_bundle.entry,
                )
            )
            medication_entry = next(
                filter(
                    lambda ent: isinstance(ent.resource, MedicationStatement),
                    actual_bundle.entry,
                )
            )

            # Test that the full URL of the diagnostic report is used as the
            # reference in the condition's insight
            self.assertTrue(diag_report_entry.fullUrl)

            insight = next(
                filter(
                    lambda ext: ext.url == alvearie_ext_url.INSIGHT_URL,
                    medication_entry.resource.meta.extension,
                )
            )
            insight_detail = next(
                filter(
                    lambda ext: ext.url == alvearie_ext_url.INSIGHT_DETAIL_URL,
                    insight.extension,
                )
            )

            reference_ext = next(
                filter(
                    lambda ext: ext.url == alvearie_ext_url.INSIGHT_REFERENCE_URL,
                    insight_detail.extension,
                )
            )

            self.assertEqual(
                diag_report_entry.fullUrl, reference_ext.valueReference.reference
            )

    def test_when_post_diag_bundle_then_condition_derived(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(unstructured_text.TEXT_FOR_MULTIPLE_CONDITIONS)
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

    def test_when_post_diag_bundle_then_adverse_event_derived(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(unstructured_text.TEXT_FOR_ADVERSE_EVENT)
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

    def test_when_post_diag_bundle_then_medication_derived(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(unstructured_text.TEXT_FOR_MEDICATION)
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

    def test_when_post_diag_bundle_then_medication_and_condition_derived(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(
                            unstructured_text.TEXT_FOR_CONDITION_AND_MEDICATION
                        )
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


class TestDiagReportUsingQuickUmls(UnitTestUsingExternalResource):
    """Unit tests where a diagnostic report is posted to quickumls for insights"""

    def setUp(self) -> None:
        # The application is defined globally in the module, so this is a potentially
        # flawed way of reseting the state between test cases.
        # It should work "well-enough" in most cases.
        importlib.reload(app)
        app.config.set_mock_nlp_service_class(
            "quickumls",
            make_mock_quick_umls_service_class(
                self.resource_path + "/quickUmls/TestReportResponses.json"
            ),
        )

    def test_when_post_diag_with_no_text_then_empty_bundle(self):
        report = make_diag_report(subject=make_patient_reference())

        with app.app.test_client() as service:
            configure_quick_umls(service)
            insight_resp = service.post("/discoverInsights", json=report.dict())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            self.assertEqual(0, len(actual_bundle.entry))

    def test_when_post_diag_bundle_with_no_text_then_no_derived_resources(self):
        bundle = make_bundle([make_diag_report(subject=make_patient_reference())])

        with app.app.test_client() as service:
            configure_quick_umls(service)
            insight_resp = service.post("/discoverInsights", json=bundle.dict())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            self.assertEqual(1, len(actual_bundle.entry))

            cmp = compare_actual_to_expected(
                expected_path=self.expected_output_path(),
                actual_resource=actual_bundle,
            )
            self.assertFalse(cmp, cmp.pretty())

    def test_when_post_diag_then_condition_derived(self):
        report = make_diag_report(
            subject=make_patient_reference(),
            attachments=[
                make_attachment(unstructured_text.TEXT_FOR_MULTIPLE_CONDITIONS)
            ],
        )

        with app.app.test_client() as service:
            configure_quick_umls(service)
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
                    attachments=[
                        make_attachment(unstructured_text.TEXT_FOR_MULTIPLE_CONDITIONS)
                    ],
                )
            ]
        )

        with app.app.test_client() as service:
            configure_quick_umls(service)
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
                    attachments=[
                        make_attachment(unstructured_text.TEXT_FOR_MEDICATION)
                    ],
                )
            ]
        )

        with app.app.test_client() as service:
            configure_quick_umls(service)
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
                        make_attachment(
                            unstructured_text.TEXT_FOR_CONDITION_AND_MEDICATION
                        )
                    ],
                )
            ]
        )

        with app.app.test_client() as service:
            configure_quick_umls(service)
            insight_resp = service.post("/discoverInsights", data=bundle.json())
            self.assertEqual(200, insight_resp.status_code)

            actual_bundle = Bundle.parse_obj(insight_resp.get_json())
            cmp = compare_actual_to_expected(
                expected_path=self.expected_output_path(),
                actual_resource=actual_bundle,
            )
            self.assertFalse(cmp, cmp.pretty())
