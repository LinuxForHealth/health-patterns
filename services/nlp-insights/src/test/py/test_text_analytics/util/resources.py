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
"""Defines a base testcase class that can use external resources in tests"""
import inspect
import os
import unittest


class UnitTestUsingExternalResource(unittest.TestCase):
    """TestCase that uses external resources, either for comparison or input"""

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.resource_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/../../../resources"
        )

    def expected_output_path(self) -> str:
        for sf in inspect.stack():
            if sf[3].startswith("test_"):
                return f"{self.resource_path}/expected_results/{type(self).__name__}/{sf[3]}.json"
        raise RuntimeError('Must be called from within a "test_" method')
