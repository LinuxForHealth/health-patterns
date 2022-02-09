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
"""Methods for comparing expected vs actual test results"""
import base64

import difflib
import json
from json.decoder import JSONDecodeError
import logging
import os
from typing import Any

import deepdiff
from fhir.resources.resource import Resource


logger = logging.getLogger(__name__)


def pjson(j: str) -> str:
    try:
        jobj = json.loads(j)
        s = json.dumps(jobj, indent=2)
    except JSONDecodeError:
        s = j

    return s


def pdiff(a: Any, b: Any) -> str:
    if not a or not b:
        return ""

    if isinstance(a, bytes):
        a_str = pjson(base64.b64decode(a).decode("utf-8"))
    else:
        a_str = ""
    if isinstance(b, bytes):
        b_str = pjson(base64.b64decode(b).decode("utf-8"))
    else:
        b_str = ""

    if a_str and b_str:
        return "\n\tJSON_DIFF=" + "".join(
            difflib.ndiff(
                a_str.splitlines(keepends=True), b_str.splitlines(keepends=True)
            )
        )
    else:
        return ""


class ResourceDifferences:
    """Wraps differences for easier debug"""

    def __init__(
        self, expected: Resource, actual: Resource, exclude_types=frozenset({bytes})
    ) -> None:
        """Determines the differences between an expected resource and a test case actual

        args:
          expected - the expected resource
          actual   - the actual resource from the testcase
          exclude_types - data types to ignore differences in
                          The default is bytes because some resources contain serialized json byte strings,
                          because json does not have order, these strings are not consistent
        """
        self.diff = deepdiff.DeepDiff(
            expected.dict(),
            actual.dict(),
            view="tree",
            verbose_level=0,
            exclude_types=exclude_types,
        )

    def __bool__(self) -> bool:
        return bool(self.diff)

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return self.__str__()

    def pretty(self) -> str:
        """Pretty prints differences"""
        try:
            change_strings = [
                f"{ctype} at path {cv.path()} \n\tEXPECTED={cv.t1}\n\tACTUAL  ={cv.t2}{pdiff(cv.t1, cv.t2)}"
                for ctype, clist in self.diff.items()
                for cv in clist
            ]
            return "\n" + "\n".join(change_strings)
        except Exception as ex:  # pylint: disable=broad-except
            return str(ex) + "\n" + str(self.diff)


def compare_actual_to_expected(
    expected_path: str, actual_resource: Resource, create_expected_if_missing=True
) -> ResourceDifferences:
    """compares an actual resource resulting from a testcase to an expected resource in a json file

    args:
      expected_path - path to expected resource in json file
      actual_resource - actual resource produced from test
      create_expected_if_missing - if the expected file does not exist, create the file and use the actual as expected.
                                   This is quick way of generating expected test data, tester is responsible for verifying.

    returns:
      Differences between expected and actual
    """
    if not os.path.exists(expected_path) and create_expected_if_missing:
        os.makedirs(os.path.dirname(expected_path), exist_ok=True)
        with open(expected_path, "w", encoding="utf-8") as f:
            logger.warning("Writing file %s", expected_path)
            f.write(actual_resource.json(indent=2))

    expected_resource = type(actual_resource).parse_file(expected_path)

    return ResourceDifferences(expected=expected_resource, actual=actual_resource)
