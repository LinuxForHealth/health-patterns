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
Test FHIR object builder utils
"""
import doctest
import pkgutil
import unittest

import text_analytics.fhir


def load_tests(loader, tests, pattern):
    """Used by unittest to discover tests

    This might not work with some custom test_text_analytics runners, and doesn't
    apply any patterns to the tests or doc-tests that are
    returned. It does work with the pydev test_text_analytics runner and the unittest CLI
    """
    del loader, pattern  # not used

    package = text_analytics
    prefix = package.__name__ + "."

    for _finder, modname, ispkg in pkgutil.walk_packages(package.__path__, prefix):
        print(f"Found submodule {modname} (is a package: {str(ispkg)})")
        module = __import__(modname, fromlist="dummy")
        tests.addTests(doctest.DocTestSuite(module))

    return tests


if __name__ == "__main__":
    unittest.main()
