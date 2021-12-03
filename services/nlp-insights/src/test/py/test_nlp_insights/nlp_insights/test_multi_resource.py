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
"""These testcases consider the case where the input bundle has more than one resource"""
# pylint: disable=missing-function-docstring
import importlib

from fhir.resources.bundle import Bundle

from test_nlp_insights.nlp_insights import test_diag_report
from test_nlp_insights.util.compare import compare_actual_to_expected
from test_nlp_insights.util.fhir import (
    make_diag_report,
    make_attachment,
    make_bundle,
    make_patient_reference,
    make_immunization,
    make_codeable_concept,
    make_patient,
)

from test_nlp_insights.util.mock_service import (
    make_mock_acd_service_class,
    configure_acd,
    make_mock_quick_umls_service_class,
    configure_quick_umls,
)
from test_nlp_insights.util.resources import UnitTestUsingExternalResource
from nlp_insights import app


class TestMultiResourceBundleUsingAcd(UnitTestUsingExternalResource):
    """Unit tests where a bundle has multiple resources"""

    def setUp(self) -> None:
        # The application is defined globally in the module, so this is a potentially
        # flawed way of reseting the state between test cases.
        # It should work "well-enough" in most cases.
        importlib.reload(app)
        app.all_nlp_services["acd"] = make_mock_acd_service_class(
            [
                str(self.resource_path) + "/acd/TestReportResponses.json",
                str(self.resource_path) + "/acd/TestEnrichResponses.json",
            ]
        )

    def test_when_post_multi_resources_then_bundle_is_returned(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(
                            test_diag_report.DIAG_REPORT_TEXT_FOR_MEDICATION_WITH_DOSAGE
                        )
                    ],
                ),
                make_immunization(
                    patient=make_patient_reference(),
                    vaccine_code=make_codeable_concept(text="DTaP"),
                ),
                # Patient is here to prove that resources that we don't know how to handle
                # will not cause a problem
                make_patient(),
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


class TestMultiResourceBundleUsingQuickUmls(UnitTestUsingExternalResource):
    """Unit tests where a bundle has multiple resources"""

    def setUp(self) -> None:
        # The application is defined globally in the module, so this is a potentially
        # flawed way of reseting the state between test cases.
        # It should work "well-enough" in most cases.
        importlib.reload(app)
        app.all_nlp_services["quickumls"] = make_mock_quick_umls_service_class(
            [
                str(self.resource_path) + "/quickUmls/TestReportResponses.json",
                str(self.resource_path) + "/quickUmls/TestEnrichResponses.json",
            ]
        )

    def test_when_post_multi_resources_then_bundle_is_returned(self):
        bundle = make_bundle(
            [
                make_diag_report(
                    subject=make_patient_reference(),
                    attachments=[
                        make_attachment(
                            test_diag_report.DIAG_REPORT_TEXT_FOR_MEDICATION_WITH_DOSAGE
                        )
                    ],
                ),
                make_immunization(
                    patient=make_patient_reference(),
                    vaccine_code=make_codeable_concept(text="DTaP"),
                ),
                # Patient is here to prove that resources that we don't know how to handle
                # will not cause a problem
                make_patient(),
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
