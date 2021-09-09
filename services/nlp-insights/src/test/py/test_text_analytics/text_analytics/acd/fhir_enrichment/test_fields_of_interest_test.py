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
"""Tests related to ensuring that the right concepts are used for insights"""

from typing import Iterable
import unittest

from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.condition import Condition
from fhir.resources.immunization import Immunization

from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics.insight_source.fields_of_interest import (
    get_concepts_for_nlp_analysis,
    CodeableConceptRef,
    CodeableConceptRefType,
)


class FieldsOfInterestTest(UnitTestUsingExternalResource):
    """Tests related to ensuring that the right concepts are used for insights"""

    def test_allergy(self):
        """Allergy intolerance should result in two concepts of interst"""

        allergy_intolerance = AllergyIntolerance.parse_file(
            self.resource_path + "/acd/mock_fhir/input/AllergyIntolerance_peanuts.json"
        )

        actual: Iterable[CodeableConceptRef] = get_concepts_for_nlp_analysis(
            allergy_intolerance
        )

        allergen = next(
            filter(
                lambda ref: ref.type == CodeableConceptRefType.ALLERGEN,
                actual,
            )
        )

        self.assertTrue(isinstance(allergen.code_ref, CodeableConcept))
        self.assertEqual(allergen.code_ref.coding[0].system, None)
        self.assertEqual(allergen.code_ref.coding[0].code, "2221")
        self.assertEqual(allergen.code_ref.coding[0].display, "Peanuts")
        self.assertEqual(allergen.fhir_path, "AllergyIntolerance.code")
        self.assertEqual(allergen.code_ref.text, "Peanuts")

        manifestation = next(
            filter(
                lambda ref: ref.type == CodeableConceptRefType.MANIFESTATION,
                actual,
            )
        )

        self.assertTrue(isinstance(allergen.code_ref, CodeableConcept))

        self.assertEqual(
            manifestation.fhir_path, "AllergyIntolerance.reaction[0].manifestation[0]"
        )
        self.assertEqual(manifestation.code_ref.text, "Anaphylactic Shock")

    def test_allergy_multiple_manifestations(self):
        """Tests an allergy intolerance with multiple manifestations"""

        allergy_intolerance = AllergyIntolerance.parse_file(
            self.resource_path + "/acd/mock_fhir/input/AllergyIntolerance_penicillin.json"
        )

        concepts = get_concepts_for_nlp_analysis(allergy_intolerance)

        allergen = next(
            filter(
                lambda ref: ref.type == CodeableConceptRefType.ALLERGEN,
                concepts,
            )
        )

        self.assertTrue(isinstance(allergen.code_ref, CodeableConcept))
        self.assertEqual(allergen.code_ref.coding, None)
        self.assertEqual(allergen.fhir_path, "AllergyIntolerance.code")
        self.assertEqual(allergen.code_ref.text, "PENICILLIN")

        manifestations = filter(
            lambda ref: ref.type == CodeableConceptRefType.MANIFESTATION,
            concepts,
        )

        manifestation = next(manifestations)
        self.assertTrue(isinstance(manifestation.code_ref, CodeableConcept))
        self.assertEqual(manifestation.code_ref.coding, None)
        self.assertEqual(
            manifestation.fhir_path, "AllergyIntolerance.reaction[0].manifestation[0]"
        )
        self.assertEqual(manifestation.code_ref.text, "PRODUCES HIVES")

        manifestation = next(manifestations)
        self.assertTrue(isinstance(manifestation.code_ref, CodeableConcept))
        self.assertEqual(manifestation.code_ref.coding, None)
        self.assertEqual(
            manifestation.fhir_path, "AllergyIntolerance.reaction[0].manifestation[1]"
        )
        self.assertEqual(manifestation.code_ref.text, "RASH")

    def test_condition(self):
        """Correct concepts must be retrieved from a condition resource"""
        condition = Condition.parse_file(
            self.resource_path + "/acd/mock_fhir/input/Condition_sleep_apnea.json"
        )

        concepts = get_concepts_for_nlp_analysis(condition)

        cnd = next(
            filter(
                lambda ref: ref.type == CodeableConceptRefType.CONDITION,
                concepts,
            )
        )
        self.assertTrue(isinstance(cnd.code_ref, CodeableConcept))
        self.assertEqual(
            cnd.code_ref.coding[0].system, "http://hl7.org/fhir/sid/icd-10-cm"
        )
        self.assertEqual(cnd.code_ref.coding[0].code, "G47.31")
        self.assertEqual(cnd.code_ref.coding[0].display, "Primary central sleep apnea")
        self.assertEqual(cnd.fhir_path, "Condition.code")
        self.assertEqual(cnd.code_ref.text, "Primary central sleep apnea")

    def test_immunization(self):
        """Retrieves correct concepts from an immunization resource"""
        immunization = Immunization.parse_file(
            self.resource_path + "/acd/mock_fhir/input/Immunization.json"
        )

        concepts = get_concepts_for_nlp_analysis(immunization)
        imz = next(
            filter(
                lambda ref: ref.type == CodeableConceptRefType.VACCINE,
                concepts,
            )
        )

        self.assertTrue(isinstance(imz.code_ref, CodeableConcept))

        self.assertEqual(imz.code_ref.coding[0].system, "http://hl7.org/fhir/sid/cvx")
        self.assertEqual(imz.code_ref.coding[0].code, "20")
        self.assertEqual(imz.code_ref.coding[0].display, "DTaP")
        self.assertEqual(imz.fhir_path, "Immunization.vaccineCode")
        self.assertEqual(imz.code_ref.text, "DTaP")


if __name__ == "__main__":
    unittest.main()
