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
Define HTTP Error Classes
"""

from json import JSONDecodeError
import json
import logging
from typing import Optional

from flask import Response
from werkzeug.exceptions import HTTPException


logger = logging.getLogger(__name__)


def build_message(message: str, json_details: Optional[str] = None) -> str:
    """Builds a message json structure for a UserError

    Args:
    message - describes the error in human readable format
    json_details - (optional) if provided, is a serialized json that has
                   additional information about the error.
    """
    msg = {"message": message}

    if json_details:
        try:
            msg["details"] = json.loads(json_details)
        except JSONDecodeError:
            logger.exception(
                "Could not build message for %s / %s", message, json_details
            )

    return json.dumps(msg)


class UserError(HTTPException):
    """Behaves like a BadRequest, except the response is converted to a json string"""

    def __init__(
        self,
        message: str,
        json_details: Optional[str] = None,
    ):
        """Initializes with a string error message and optional json details

        the response will contain a json wrapper for the message.

        Args:
        message - describes the error in human readable format
        json_details - (optional) if provided, is a serialized json that has
                       additional information about the error.
        """
        super().__init__(
            response=Response(
                build_message(message, json_details),
                status=400,
                mimetype="application/json",
            )
        )
