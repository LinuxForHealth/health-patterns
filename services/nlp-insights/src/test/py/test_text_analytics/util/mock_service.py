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
"""Defines mock NLP services"""
import json
from typing import Dict, Any, Type

from flask.testing import FlaskClient
from ibm_whcs_sdk.annotator_for_clinical_data import (
    annotator_for_clinical_data_v1 as acd,
)

from text_analytics.nlp.acd import acd_service


def configure_acd(service: FlaskClient) -> None:
    """Configures nlp-insights flask service to use ACD"""

    rsp = service.post(
        "/config/definition",
        json={
            "name": "acdconfig1",
            "nlpServiceType": "acd",
            "config": {
                "apikey": "**invalid**",
                "endpoint": "https://invalid.ibm.com",
                "flow": "wh_acd.ibm_clinical_insights_v1.0_standard_flow",
            },
        },
    )

    if rsp.status_code != 200:
        raise RuntimeError(
            f"Failed to register config code = {rsp.status_code} {rsp.data}"
        )

    rsp = service.post("/config/setDefault?name=acdconfig1")
    if rsp.status_code != 200:
        raise RuntimeError(
            f"Failed to set default config code = {rsp.status_code} {rsp.data}"
        )


class MockAcdService(acd_service.ACDService):
    """Mock ACD Service to return pre-defined response given a specific input string

    Input strings are loaded from file as a json object with keys
    request-string -> json response
    """

    def __init__(self, config: Dict[str, Any], mapping_file_path: str):
        super().__init__(config)
        with open(mapping_file_path, "r", encoding="utf-8") as f:
            self.response_map = json.load(f)

    def _run_nlp(self, text: str) -> acd.ContainerAnnotation:
        json_obj = self.response_map[text]
        return acd.ContainerAnnotation.from_dict(json_obj)


def make_mock_acd_service_class(mapping_file_path: str) -> Type[MockAcdService]:
    """Creates a mock acd service that uses the responses in the specified file"""

    class MockAcdServiceWithFile(MockAcdService):
        """A Mock ACD service class that targets a specific file"""

        def __init__(self, config: Dict[str, Any]):
            super().__init__(config, mapping_file_path)

    return MockAcdServiceWithFile
