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
"""Utilities for creating fhir resources for test"""

import base64
from typing import List, Dict, Any, Optional

from fhir.resources.allergyintolerance import (
    AllergyIntolerance,
    AllergyIntoleranceReaction,
)
from fhir.resources.attachment import Attachment
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import DocumentReference
from fhir.resources.immunization import Immunization
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource


def make_patient_reference() -> Reference:
    """Makes a patient reference"""
    return Reference.construct(reference="Patient/1234567890")


def make_patient() -> Patient:
    """Returns a patient resource"""
    return Patient.parse_obj({"id": "1234567890", "name": [{"text": "Nick"}]})


def make_diag_report(
    subject: Reference = None, attachments: List[Attachment] = None
) -> DiagnosticReport:
    """Creates a FHIR diagnostic report"""
    report = DiagnosticReport.parse_obj(
        {
            "id": "12345",
            "status": "final",
            "code": {
                "coding": [{"code": "1487", "display": "ECHO CARDIOGRAM COMPLETE"}],
                "text": "ECHO CARDIOGRAM COMPLETE",
            },
        }
    )
    if subject:
        report.subject = subject

    if attachments:
        report.presentedForm = attachments

    return report


def make_codeable_concept(
    text: Optional[str], codings: Optional[List[Coding]] = None
) -> CodeableConcept:
    """Creates a codeable concept with the specified text"""
    concept = CodeableConcept.construct()
    if codings:
        concept.coding = codings
    if text:
        concept.text = text

    return concept


def make_condition(
    subject: Reference, code: CodeableConcept, rid: str = "12345"
) -> Condition:
    """Constructs a condition"""
    return Condition.construct(id=rid, subject=subject, code=code)


def make_docref_report(
    attachments: List[Attachment], subject: Reference = None
) -> DocumentReference:
    """Creates a FHIR document reference"""
    report = DocumentReference.parse_obj(
        {
            "id": "12345",
            "status": "current",
            "category": [
                {
                    "coding": [
                        {
                            "code": "68607-1",
                            "display": "Progress note",
                            "system": "http://loinc.org",
                        }
                    ]
                }
            ],
            "content": [{"attachment": a.dict()} for a in attachments],
        }
    )

    if subject:
        report.subject = subject

    return report


def make_immunization(
    patient: Reference, vaccine_code: CodeableConcept, rid="54321"
) -> Immunization:
    """Builds an Immunization"""
    return Immunization.parse_obj(
        {
            "id": rid,
            "status": "completed",
            "occurrenceDateTime": "2017",
            "patient": patient,
            "vaccineCode": vaccine_code,
        }
    )


def make_attachment(unencoded_text_data: str, content_type: str = "text/plain"):
    """Creates a FHIR attachment element"""
    dattachment: Dict[str, Any] = {}
    if unencoded_text_data:
        dattachment["data"] = base64.b64encode(
            unencoded_text_data.encode("utf-8")
        ).decode("utf-8")
    if content_type:
        dattachment["contentType"] = content_type
    return Attachment.parse_obj(dattachment)


def make_allergy_intolerance(
    patient: Reference,
    code: Optional[CodeableConcept] = None,
    rid: str = "67890",
) -> AllergyIntolerance:
    """Builds an allergy intolerance"""
    allergy = AllergyIntolerance.parse_obj({"patient": patient, "id": rid})

    if code:
        allergy.code = code

    return allergy


def make_bundle(resources: List[Resource]) -> Bundle:
    """Makes a bundle of resources for test"""

    bundle = Bundle.construct()
    bundle.type = "transaction"
    bundle.entry = []

    for index, resource in enumerate(resources):
        bundle_entry = BundleEntry.construct()
        bundle_entry.resource = resource
        request = BundleEntryRequest.parse_obj(
            {"url": f"{type(resource).__name__}/{index}", "method": "POST"}
        )
        bundle_entry.request = request
        bundle.entry.append(bundle_entry)

    return bundle
