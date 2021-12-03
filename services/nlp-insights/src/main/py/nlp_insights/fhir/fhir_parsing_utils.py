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
"""
Utilities for parsing fhir resources into objects
"""
import json
from json.decoder import JSONDecodeError
from typing import Callable
from typing import Dict
from typing import Type
from typing import TypeVar

from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.bundle import Bundle
from fhir.resources.condition import Condition
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import DocumentReference
from fhir.resources.immunization import Immunization
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.resource import Resource
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Response


def parse_fhir_resource_from_payload(doc: bytes) -> Resource:
    """Parses user provided json into an object

       Args: doc - the json document string (as bytes)
       Returns: Fhir Resource

    raises BadRequest if the provided data is not valid
    """
    T = TypeVar("T", bound=Resource)
    parsers: Dict[str, Callable[[Type[T]], T]] = {
        "Bundle": Bundle.parse_obj,
        "MedicationStatement": MedicationStatement.parse_obj,
        "Condition": Condition.parse_obj,
        "DocumentReference": DocumentReference.parse_obj,
        "DiagnosticReport": DiagnosticReport.parse_obj,
        "AllergyIntolerance": AllergyIntolerance.parse_obj,
        "Immunization": Immunization.parse_obj,
    }

    try:
        obj = json.loads(doc.decode("utf-8"))
    except JSONDecodeError as jderr:
        raise BadRequest(
            description=f"Resource was not valid json: {str(jderr)}"
        ) from jderr

    if "resourceType" in obj and obj["resourceType"] in parsers:
        try:
            return parsers[obj["resourceType"]](obj)
        except ValidationError as verr:
            raise BadRequest(
                response=Response(
                    verr.json(), content_type="application/json", status=400
                )
            ) from verr

    else:
        resource_type = (
            obj["resourceType"] if "resourceType" in obj else "<not specified> "
        )
        raise BadRequest(
            description=f"The resource type {resource_type} is not supported"
        )
