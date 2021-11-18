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
"""Utilities for working with medication insights"""
import logging
import re
from typing import NamedTuple
from typing import Optional


class MedicationDosage(NamedTuple):
    """Represents a medication's dosage and units

    The units string will be empty if the units are unknown.
    """

    dosage: float
    units: str


logger = logging.getLogger(__name__)
_DOSE_AND_UNITS_PATTERN = re.compile(r"([0-9.][0-9,.]*)\s*([a-zA-Z0-9\^/]*)")


def parse_dosage_with_units(dosage_with_units: str) -> Optional[MedicationDosage]:
    """Parses a string into dosage and units

    Examples:
    >>> parse_dosage_with_units("2mg")
    MedicationDosage(dosage=2.0, units='mg')

    >>> parse_dosage_with_units("2 mg")
    MedicationDosage(dosage=2.0, units='mg')

    >>> parse_dosage_with_units("2.25 g/ml^3")
    MedicationDosage(dosage=2.25, units='g/ml^3')

    >>> parse_dosage_with_units("2,255.50 ml^3")
    MedicationDosage(dosage=2255.5, units='ml^3')

    """
    mch = re.search(_DOSE_AND_UNITS_PATTERN, dosage_with_units)

    if not mch:
        logger.warning("%s did not match the pattern of a dosage", dosage_with_units)
        return None

    dose_str = mch.group(1).replace(",", "")
    try:
        dose_amount = float(dose_str)
    except ValueError:
        logger.exception("%s was not a valid float", dose_str)
        return None
    except ArithmeticError:
        logger.exception("%s could not be converted to a float", dose_str)

    return MedicationDosage(dosage=dose_amount, units=mch.group(2))
