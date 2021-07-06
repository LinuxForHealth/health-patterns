# coding: utf-8

# Copyright 2019 IBM All Rights Reserved.
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

from typing import Dict, Optional

import json
import requests

class DetailedResponse:
    """Custom class for detailed response returned from APIs.

    Keyword Args:
        response: The response to the service request, defaults to None.
        headers: The headers of the response, defaults to None.
        status_code: The status code of there response, defaults to None.

    Attributes:
        response (requests.Response): The response to the service request.
        headers (dict): The headers of the response.
        status_code (int): The status code of the response.

    """
    def __init__(self,
                 *,
                 response: Optional[requests.Response] = None,
                 headers: Optional[Dict[str, str]] = None,
                 status_code: Optional[int] = None) -> None:
        self.result = response
        self.headers = headers
        self.status_code = status_code

    def get_result(self) -> requests.Response:
        """Get the HTTP response of the service request.

        Returns:
            The response to the service request
        """
        return self.result

    def get_headers(self) -> dict:
        """The HTTP response headers of the service request.

        Returns:
            A dictionary of response headers
        """
        return self.headers

    def get_status_code(self) -> int:
        """The HTTP status code of the service request.

        Returns:
            The status code of the service request.
        """
        return self.status_code

    def _to_dict(self) -> dict:
        _dict = {}
        if hasattr(self, 'result') and self.result is not None:
            _dict['result'] = self.result if isinstance(self.result, (dict, list)) else 'HTTP response'
        if hasattr(self, 'headers') and self.headers is not None:
            _dict['headers'] = self.headers
        if hasattr(self, 'status_code') and self.status_code is not None:
            _dict['status_code'] = self.status_code
        return _dict

    def __str__(self) -> str:
        return json.dumps(self._to_dict(), indent=4, default=lambda o: o.__dict__)
