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
"""Common way of constructing insight IDs for all NLP pipelines"""

from typing import Generator


def insight_id_maker(
    insight_id_string_prefix: str = "insight-", start: int = 1
) -> Generator[str, None, None]:
    """Generator to return the next insight id for a resource

    Args:
        insight_id_string_prefix - string value to prepend to each id
        count to start at

    Example:
    >>> maker = insight_id_maker()
    >>> next(maker)
    'insight-1'
    >>> next(maker)
    'insight-2'
    """
    insight_id_num = start
    while True:
        yield insight_id_string_prefix + str(insight_id_num)
        insight_id_num += 1
