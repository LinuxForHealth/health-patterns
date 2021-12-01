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
"""These testcases test error responses"""
# pylint: disable=missing-function-docstring
import importlib

from test_text_analytics.util.fhir import (
    make_condition,
    make_codeable_concept,
    make_bundle,
    make_patient_reference,
)
from test_text_analytics.util.mock_service import (
    make_mock_acd_service_class,
    configure_acd,
    make_mock_quick_umls_service_class,
)
from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics import app


class TestErrorResponses(UnitTestUsingExternalResource):
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
        app.all_nlp_services["quickumls"] = make_mock_quick_umls_service_class(
            [
                str(self.resource_path) + "/quickUmls/TestReportResponses.json",
                str(self.resource_path) + "/quickUmls/TestEnrichResponses.json",
            ]
        )

    def test_when_invalid_json_then_bad_request(self):

        with app.app.test_client() as service:
            configure_acd(service)
            insight_resp = service.post("/discoverInsights", data="not valid json")
            self.assertEqual(400, insight_resp.status_code)

    def test_when_empty_bundle_then_ok(self):

        with app.app.test_client() as service:
            configure_acd(service)
            rsp = service.post(
                "/discoverInsights",
                data="""{
            "type": "transaction",
            "resourceType": "Bundle"
            }
            """,
            )
            self.assertEqual(200, rsp.status_code)

    def test_when_no_config_then_bad_request(self):
        bundle = make_bundle(
            [
                make_condition(
                    subject=make_patient_reference(),
                    code=make_codeable_concept(text="Heart Attack"),
                )
            ]
        )

        with app.app.test_client() as service:
            # configure_acd(service)
            rsp = service.post("/discoverInsights", json=bundle.dict())
            self.assertEqual(400, rsp.status_code)

    def test_when_bad_bundle_then_error(self):

        with app.app.test_client() as service:
            configure_acd(service)
            # Post fails because condition is required to have a subject
            rsp = service.post(
                "/discoverInsights",
                data="""
{
    "entry": [
        {
            "request": {
                "method": "PUT",
                "url": "Condition/12345"
            },
            "resource": {
                "id": "12345",
                "resourceType": "Condition"
            }
        }
    ],
    "type": "transaction",
    "resourceType": "Bundle"
}
            """,
            )
            self.assertEqual(400, rsp.status_code)
            self.assertEqual(rsp.json[0]["type"], "value_error.missing")

    def test_when_bad_resource_then_error(self):

        with app.app.test_client() as service:
            configure_acd(service)
            # Post fails because condition is required to have a subject
            rsp = service.post(
                "/discoverInsights",
                data="""
    {
        "resourceType": "I don't know what this is"
    }
                """,
            )
            self.assertEqual(400, rsp.status_code)
