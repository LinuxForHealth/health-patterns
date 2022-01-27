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
"""These testcases test the configuration apis, with the exception of insight discovery"""
# pylint: disable=missing-function-docstring
import importlib

from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.diagnosticreport import DiagnosticReport

from nlp_insights import app
from test_nlp_insights.util.mock_service import (
    make_mock_acd_service_class,
    configure_acd,
    make_mock_quick_umls_service_class,
    configure_quick_umls,
    configure_resource_nlp_override,
    set_default_nlp,
)
from test_nlp_insights.util.resources import UnitTestUsingExternalResource


class TestConfig(UnitTestUsingExternalResource):
    """Unit tests where a bundle has multiple resources"""

    def setUp(self) -> None:
        # The application is defined globally in the module, so this is a potentially
        # flawed way of reseting the state between test cases.
        # It should work "well-enough" in most cases.
        importlib.reload(app)
        app.config.set_mock_nlp_service_class(
            "acd",
            make_mock_acd_service_class(
                [
                    str(self.resource_path) + "/acd/TestReportResponses.json",
                    str(self.resource_path) + "/acd/TestEnrichResponses.json",
                ]
            ),
        )
        app.config.set_mock_nlp_service_class(
            "quickumls",
            make_mock_quick_umls_service_class(
                [
                    str(self.resource_path) + "/quickUmls/TestReportResponses.json",
                    str(self.resource_path) + "/quickUmls/TestEnrichResponses.json",
                ]
            ),
        )

    def test_when_acd_confg_then_acd_config_is_returned(self):

        with app.app.test_client() as service:
            cfg_acd = configure_acd(service, is_default=True)
            rsp = service.get(f"/config/{cfg_acd}")
            self.assertEqual(200, rsp.status_code)
            cfg = rsp.json
            self.assertEqual("acd", cfg["nlpServiceType"])
            self.assertEqual(cfg_acd, cfg["name"])

    def test_when_qu_confg_then_qu_config_is_returned(self):

        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=True)
            rsp = service.get(f"/config/{cfg_qu}")
            self.assertEqual(200, rsp.status_code)
            cfg = rsp.json
            self.assertEqual("quickumls", cfg["nlpServiceType"])
            self.assertEqual(cfg_qu, cfg["name"])

    def test_when_config_default_is_updated_then_get_current_config_returns_default(
        self,
    ):
        with app.app.test_client() as service:

            # Start with no configs, should get a 400 back for default
            rsp = service.get("/config")
            self.assertEqual(400, rsp.status_code)

            # Configure NLP, but no defaults so still 400
            cfg_qu = configure_quick_umls(service, is_default=False)
            cfg_acd = configure_acd(service, is_default=False)
            rsp = service.get("/config")
            self.assertEqual(400, rsp.status_code)

            # Make Quick umls default
            set_default_nlp(service, cfg_qu)
            rsp = service.get("/config")
            self.assertEqual(200, rsp.status_code)
            self.assertEqual(rsp.get_json()["config"], cfg_qu)

            # Make ACD the default
            set_default_nlp(service, cfg_acd)
            rsp = service.get("/config")
            self.assertEqual(200, rsp.status_code)
            self.assertEqual(rsp.get_json()["config"], cfg_acd)

            # Override does not change the default
            configure_resource_nlp_override(service, AllergyIntolerance, cfg_qu)
            rsp = service.get("/config")
            self.assertEqual(200, rsp.status_code)
            self.assertEqual(rsp.get_json()["config"], cfg_acd)

    def test_when_clear_default_config_then_no_current_config(self):
        with app.app.test_client() as service:
            cfg_acd = configure_acd(service, is_default=True)

            rsp = service.get("/config")
            self.assertEqual(200, rsp.status_code)
            self.assertEqual(rsp.get_json()["config"], cfg_acd)

            rsp = service.post("/config/clearDefault")
            rsp = service.get("/config")
            self.assertEqual(400, rsp.status_code)

    def test_when_override_then_all_resource_overrides_correct(self):
        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=False)
            configure_acd(service, is_default=True)
            configure_resource_nlp_override(service, AllergyIntolerance, cfg_qu)
            configure_resource_nlp_override(service, DiagnosticReport, cfg_qu)

            rsp = service.get("/config/resource")
            self.assertEqual(200, rsp.status_code)
            overrides = rsp.json
            self.assertEqual(overrides["AllergyIntolerance"], cfg_qu)
            self.assertEqual(overrides["DiagnosticReport"], cfg_qu)

    def test_when_override_then_resource_overrides_correct(self):
        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=False)
            configure_acd(service, is_default=True)
            configure_resource_nlp_override(service, AllergyIntolerance, cfg_qu)
            configure_resource_nlp_override(service, DiagnosticReport, cfg_qu)

            rsp = service.get("/config/resource/AllergyIntolerance")
            self.assertEqual(200, rsp.status_code)
            self.assertEqual(cfg_qu, rsp.json["AllergyIntolerance"])

    def test_when_delete_resource_override_then_resource_overrides_correct(self):
        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=False)
            configure_acd(service, is_default=True)
            configure_resource_nlp_override(service, AllergyIntolerance, cfg_qu)
            configure_resource_nlp_override(service, DiagnosticReport, cfg_qu)

            # verify setup OK
            rsp = service.get("/config/resource")
            self.assertEqual(200, rsp.status_code)
            overrides = rsp.json
            self.assertEqual(overrides["AllergyIntolerance"], cfg_qu)
            self.assertEqual(overrides["DiagnosticReport"], cfg_qu)

            # delete and verify
            rsp = service.delete("/config/resource/AllergyIntolerance")
            self.assertEqual(204, rsp.status_code)

            rsp = service.get("/config/resource")
            self.assertEqual(200, rsp.status_code)
            overrides = rsp.json
            self.assertEqual(overrides["DiagnosticReport"], cfg_qu)
            self.assertTrue("AllergyIntolerance" not in overrides)

    def test_when_delete_non_exist_resource_override_then_400(self):
        with app.app.test_client() as service:
            configure_acd(service, is_default=True)

            rsp = service.delete("/config/resource/AllergyIntolerance")
            self.assertEqual(400, rsp.status_code, rsp.data)

    def test_when_delete_all_resource_overrides_then_no_resource_overrides(self):
        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=False)
            configure_acd(service, is_default=True)
            configure_resource_nlp_override(service, AllergyIntolerance, cfg_qu)
            configure_resource_nlp_override(service, DiagnosticReport, cfg_qu)

            # verify setup OK
            rsp = service.get("/config/resource")
            self.assertEqual(200, rsp.status_code)
            overrides = rsp.json
            self.assertEqual(overrides["AllergyIntolerance"], cfg_qu)
            self.assertEqual(overrides["DiagnosticReport"], cfg_qu)

            # delete and verify
            rsp = service.delete("/config/resource")
            self.assertEqual(204, rsp.status_code)

            rsp = service.get("/config/resource")
            self.assertEqual(200, rsp.status_code)
            overrides = rsp.json
            self.assertTrue("DiagnosticReport" not in overrides)
            self.assertTrue("AllergyIntolerance" not in overrides)

    def test_when_get_all_configs_then_configs_returned(self):
        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=False)
            cfg_acd = configure_acd(service, is_default=False)

            rsp = service.get("/all_configs")
            services = set(rsp.json["all_configs"])
            self.assertTrue(cfg_qu in services)
            self.assertTrue(cfg_acd in services)

    def test_when_delete_config_then_config_deleted(self):
        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=False)
            cfg_acd = configure_acd(service, is_default=False)

            # verify setup ok
            rsp = service.get("/all_configs")
            services = set(rsp.json["all_configs"])
            self.assertTrue(cfg_qu in services)
            self.assertTrue(cfg_acd in services)

            rsp = service.delete(f"/config/{cfg_qu}")
            self.assertEqual(204, rsp.status_code)

            rsp = service.delete(f"/config/{cfg_acd}")
            self.assertEqual(204, rsp.status_code)

            rsp = service.get("/all_configs")
            services = set(rsp.json["all_configs"])
            self.assertTrue(cfg_qu not in services)
            self.assertTrue(cfg_acd not in services)

    def test_when_delete_default_config_then_fail(self):
        with app.app.test_client() as service:
            cfg_qu = configure_quick_umls(service, is_default=False)

            # Make Quick umls default
            set_default_nlp(service, cfg_qu)

            # verify setup ok
            rsp = service.get("/all_configs")
            services = set(rsp.json["all_configs"])
            self.assertTrue(cfg_qu in services)

            cfg_qu = configure_quick_umls(service, is_default=False)

            rsp = service.delete(f"/config/{cfg_qu}")
            self.assertEqual(400, rsp.status_code)

            # Test than after clearing the default we can delete
            rsp = service.post("/config/clearDefault")
            rsp = service.get("/config")
            self.assertTrue(rsp.status_code == 400)

            rsp = service.delete(f"/config/{cfg_qu}")
            self.assertEqual(204, rsp.status_code)
