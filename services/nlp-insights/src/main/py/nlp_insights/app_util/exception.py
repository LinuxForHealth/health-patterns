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
from typing import Optional, Any
from flask import Response
from werkzeug.exceptions import HTTPException


logger = logging.getLogger(__name__)


def _safe_loads(json_details: str) -> Any:
    """Loads a json string into an object

       If the json is not valid, error is logged and {} is returned

    Args:
    json_details - a serialized json

    Returns Python object for the json
    """

    try:
        return json.loads(json_details)
    except JSONDecodeError as err:
        logger.exception("Could not build json for %s %s", json_details, str(err))
        return {}


class UserError(HTTPException):
    """Behaves like a BadRequest, with json mimetype and potential for details"""

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
        rmessage = {"message": message}
        if json_details:
            rmessage["details"] = _safe_loads(json_details)

        super().__init__(
            response=Response(
                json.dumps(rmessage), status=400, mimetype="application/json"
            )
        )
