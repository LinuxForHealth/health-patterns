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
"""Utilities for creating a transaction bundle"""


import json  # noqa: F401 pylint: disable=unused-import
from typing import List
from typing import NamedTuple

from fhir.resources.bundle import Bundle
from fhir.resources.bundle import BundleEntry
from fhir.resources.bundle import BundleEntryRequest
from fhir.resources.condition import (  # noqa: F401 pylint: disable=unused-import
    Condition,
)
from fhir.resources.resource import Resource


class BundleEntryDfn(NamedTuple):
    """Entry used by create_transaction_bundle to create a bundle"""

    resource: Resource
    method: str
    url: str

    def to_bundle_entry(self) -> BundleEntry:
        """Builds a bundle entry from the definition"""
        bundle_entry = BundleEntry.construct()
        bundle_entry.resource = self.resource
        request = BundleEntryRequest.parse_obj({"url": self.url, "method": self.method})
        bundle_entry.request = request
        return bundle_entry


def create_transaction_bundle(resource_action_list: List[BundleEntryDfn]) -> Bundle:
    """Creates a bundle from a list of bundle resources

    Args:
        resource_action_list - list of bundle resources

    Example:

    Build input list:
    >>> condition1 = Condition.parse_obj(json.loads(
    ... '''
    ... {
    ...     "code": {
    ...         "text": "Diabetes Mellitus, Insulin-Dependent"
    ...     },
    ...     "subject": {
    ...         "reference": "Patient/7c33b82a-4efc-4082-9fe9-8122d6791552"
    ...     },
    ...     "resourceType": "Condition"
    ... }'''))

    >>> condition2 = Condition.parse_obj(json.loads(
    ... '''
    ... {
    ...     "code": {
    ...         "text": "Something else"
    ...     },
    ...     "subject": {
    ...         "reference": "Patient/7c33b82a-4efc-4082-9fe9-8122d6791552"
    ...     },
    ...     "resourceType": "Condition"
    ... }'''))

    Result:
    >>> bundle = create_transaction_bundle([BundleEntryDfn(condition1, 'POST', 'http://url1'),
    ...                                     BundleEntryDfn(condition2, 'POST', 'http://url2')])
    >>> print(bundle.json(indent=2))
    {
      "entry": [
        {
          "request": {
            "method": "POST",
            "url": "http://url1"
          },
          "resource": {
            "code": {
              "text": "Diabetes Mellitus, Insulin-Dependent"
            },
            "subject": {
              "reference": "Patient/7c33b82a-4efc-4082-9fe9-8122d6791552"
            },
            "resourceType": "Condition"
          }
        },
        {
          "request": {
            "method": "POST",
            "url": "http://url2"
          },
          "resource": {
            "code": {
              "text": "Something else"
            },
            "subject": {
              "reference": "Patient/7c33b82a-4efc-4082-9fe9-8122d6791552"
            },
            "resourceType": "Condition"
          }
        }
      ],
      "type": "transaction",
      "resourceType": "Bundle"
    }
    """
    bundle = Bundle.construct()
    bundle.type = "transaction"
    bundle.entry = []

    for res_act in resource_action_list:
        bundle.entry.append(res_act.to_bundle_entry())

    return bundle
