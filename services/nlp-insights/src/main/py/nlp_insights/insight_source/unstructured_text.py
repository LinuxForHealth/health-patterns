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
"""Constants and methods for understanding user provided FHIR resources

   These contain tools for parsing json into FHIR resources. Also contains
   utils for determining the characteristics of those resources in terms of
   how insights will be generated.

"""
import base64
from typing import List
from typing import NamedTuple

from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import DocumentReference
from fhir.resources.reference import Reference
from fhir.resources.resource import Resource

from nlp_insights.fhir.path import FhirPath
from nlp_insights.fhir.reference import ResourceReference


class UnstructuredText(NamedTuple):
    """Models text data that can be used to derive new FHIR resources"""

    source_ref: ResourceReference[Resource]
    text_path: FhirPath
    text: str

    @property
    def subject(self) -> Reference:
        """Returns a reference to the subject of this unstructured text"""
        return self.source_ref.resource.subject


def _decode_text(encoded_data: bytes) -> str:
    """decodes binary data to utf-8 string

    Args: encoded_data - utf-8 binary data
    Returns: utf-8 string
    """
    byte_text = base64.b64decode(encoded_data)
    text = byte_text.decode("utf8")
    return text


def _get_diagnostic_report_text(
    reference: ResourceReference[DiagnosticReport],
) -> List[UnstructuredText]:
    """Returns the (decoded) attached document(s) and path of the document text.

    The method ignores the content type field of the attachment and assumed plain text.

    Args:
       reference - reference to the report to retrieve presented form text from
    Returns:
       path and decoded text from the document, or empty if there is no text
    """
    if reference.resource.presentedForm:
        return [
            UnstructuredText(
                source_ref=reference,
                text_path=FhirPath(f"DiagnosticReport.presentedForm[{ix}].data"),
                text=_decode_text(attachment.data),
            )
            for ix, attachment in enumerate(reference.resource.presentedForm)
            if attachment.data
        ]

    return []


def _get_document_reference_data(
    reference: ResourceReference[DocumentReference],
) -> List[UnstructuredText]:
    """Returns the (decoded) attached document(s) and path of the document text.

    The method ignores the content type field of the attachment and assumed plain text.
    The document reference must have a subject, as a subject is required for all derived resources.

    Args:
       reference - reference to the report to retrieve presented form text from
    Returns:
       path and decoded text from the document, or empty if there is no text
    """
    if reference.resource.content and reference.resource.subject:
        return [
            UnstructuredText(
                source_ref=reference,
                text_path=FhirPath(f"DocumentReference.content[{ix}].attachment.data"),
                text=_decode_text(content.attachment.data),
            )
            for ix, content in enumerate(reference.resource.content)
            if content.attachment and content.attachment.data
        ]

    return []


def get_unstructured_text(
    resource_ref: ResourceReference[Resource],
) -> List[UnstructuredText]:
    """Returns unstructured text that can be used to derive new resources

    If the resource does not have text suitable for deriving new resources,
    an empty list is returned.

    Args:
        resource_ref - reference to the resource to search for unstructured text
    Returns: the unstructured text elements from the resource
    """
    if diag_report := resource_ref.down_cast(DiagnosticReport):
        return _get_diagnostic_report_text(diag_report)

    if doc_ref := resource_ref.down_cast(DocumentReference):
        return _get_document_reference_data(doc_ref)

    return []
