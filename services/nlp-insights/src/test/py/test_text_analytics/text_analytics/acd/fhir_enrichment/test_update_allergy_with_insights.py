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

import json
import unittest

from deepdiff import DeepDiff
from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.bundle import Bundle
from ibm_whcs_sdk.annotator_for_clinical_data.annotator_for_clinical_data_v1 import (
    ContainerAnnotation,
)

from test_text_analytics.util.resources import UnitTestUsingExternalResource
from text_analytics.insight_source.concept_text_adjustment import AdjustedConceptRef
from text_analytics.insight_source.fields_of_interest import (
    CodeableConceptRef,
    CodeableConceptRefType,
)
from text_analytics.nlp.acd.fhir_enrichment.enrich_fhir_resource import (
    enrich_resource_codeable_concepts,
)

from text_analytics.nlp.acd.fhir_enrichment.insights.update_codeable_concepts import (
    update_codeable_concepts_and_meta_with_insights,
    AcdConceptRef,
)

from text_analytics.nlp.nlp_config import ACD_NLP_CONFIG_CDP_V1_0


class EnhanceAllergyWithInsightsTest(UnitTestUsingExternalResource):
    def _verify_insights_allergy(
        self, allergy, expected_allergy, ai_results, full_output
    ):
        num_updates = update_codeable_concepts_and_meta_with_insights(
            allergy, ai_results, ACD_NLP_CONFIG_CDP_V1_0
        )

        if expected_allergy is None:
            self.assertTrue(num_updates == 0, "Expected no allergy updated")
        else:
            differences = DeepDiff(expected_allergy, allergy, verbose_level=2).pretty()
            if full_output:
                expected_str = "\n\nEXPECTED RESULTS:\n" + expected_allergy.json()
                actual_str = "\n\nACTUAL RESULTS:\n" + allergy.json()
                self.assertEqual(differences, "", expected_str + actual_str)
            else:
                self.assertEqual(differences, "")

    def test_allergy_add_insights_manifestation(self):
        """
        This test_text_analytics is verifying a single manifestation from allergy is correctly run through ACD
        and the correct insights for this one manifestation are added to the FHIR resource.
        """
        allergy = AllergyIntolerance.parse_file(
            self.resource_path
            + "/acd/mock_fhir/input/AllergyIntolerance_oxycodone.json"
        )
        expected_allergy = AllergyIntolerance.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/AllergyIntolerance_oxycodone_insights.json"
        )

        mock_acd_response = {}
        with open(
            self.resource_path + "/acd/mock_acd_output/muscle_pain.json",
            "r",
            encoding="utf-8",
        ) as f:
            mock_acd_response = ContainerAnnotation.from_dict(json.loads(f.read()))

        ai_results = [
            AcdConceptRef(
                adjusted_concept=AdjustedConceptRef(
                    concept_ref=CodeableConceptRef(
                        type=CodeableConceptRefType.MANIFESTATION,
                        code_ref=allergy.reaction[0].manifestation[0],
                        fhir_path="AllergyIntolerance.reaction[0].manifestation[0]",
                    ),
                    adjusted_text=allergy.reaction[0].manifestation[0].text,
                ),
                acd_response=mock_acd_response,
            )
        ]

        self._verify_insights_allergy(allergy, expected_allergy, ai_results, True)

    def test_allergy_add_insights_allergen(self):
        """This test_text_analytics is verifying just the allergen text is correctly run through ACD
        and the correct insights for this allergen are added to the FHIR resource.
        """
        allergy = AllergyIntolerance.parse_file(
            self.resource_path
            + "/acd/mock_fhir/input/AllergyIntolerance_tree_pollen.json"
        )
        expected_allergy = AllergyIntolerance.parse_file(
            self.resource_path
            + "/acd/mock_fhir/output/AllergyIntolerance_tree_pollen_insights.json"
        )

        mock_acd_response = {}
        with open(
            self.resource_path + "/acd/mock_acd_output/allergy_tree_pollen.json",
            "r",
            encoding="utf-8",
        ) as f:
            mock_acd_response = ContainerAnnotation.from_dict(json.loads(f.read()))

        ai_results = [
            AcdConceptRef(
                adjusted_concept=AdjustedConceptRef(
                    concept_ref=CodeableConceptRef(
                        type=CodeableConceptRefType.ALLERGEN,
                        code_ref=allergy.code,
                        fhir_path="AllergyIntolerance.code",
                    ),
                    adjusted_text=allergy.code.text,
                ),
                acd_response=mock_acd_response,
            )
        ]

        self._verify_insights_allergy(allergy, expected_allergy, ai_results, True)

    def test_allergy_add_insights_no_allergen_found(self):
        allergy = AllergyIntolerance.parse_file(
            self.resource_path
            + "/acd/mock_fhir/input/AllergyIntolerance_not_valid_allergy.json"
        )

        mock_acd_response = {}
        with open(
            self.resource_path + "/acd/mock_acd_output/abcd.json", "r", encoding="utf-8"
        ) as f:
            mock_acd_response = ContainerAnnotation.from_dict(json.loads(f.read()))

        ai_results = [
            AcdConceptRef(
                adjusted_concept=AdjustedConceptRef(
                    concept_ref=CodeableConceptRef(
                        type=CodeableConceptRefType.ALLERGEN,
                        code_ref=allergy.code,
                        fhir_path="AllergyIntolerance.code",
                    ),
                    adjusted_text=allergy.code.text,
                ),
                acd_response=mock_acd_response,
            )
        ]

        self._verify_insights_allergy(allergy, None, ai_results, True)

    # Bundle level tests

    def _allergy_bundle_update(self, allergy, expected_json, ai_results):
        if expected_json is not None:
            expected_bundle = Bundle.parse_file(expected_json)
        else:
            expected_bundle = None

        result = enrich_resource_codeable_concepts(ai_results, allergy)

        if expected_bundle is None:
            self.assertTrue(result is None, "Expected no allergy created")
        else:
            differences = DeepDiff(expected_bundle, result, verbose_level=2)

            # Differences str should be empty if results match expected
            self.assertEqual(
                differences,
                {},
                "Results do not match expected.\nDIFFERENCES:\n"
                + str(differences)
                + "\nEXPECTED RESULTS:\n"
                + expected_bundle.json()
                + "\nACTUAL RESULTS:\n"
                + result.json(),
            )

    def test_single_resource_update_allergy_peanuts(self):
        input_json = (
            self.resource_path + "/acd/mock_fhir/input/AllergyIntolerance_peanuts.json"
        )
        expected_json = (
            self.resource_path
            + "/acd/mock_fhir/output/Bundle_update_allergy_peanuts.json"
        )

        allergy = AllergyIntolerance.parse_file(input_json)

        ai_results = []

        # Load ACD results for allergen of peanuts
        with open(
            self.resource_path + "/acd/mock_acd_output/allergy_peanuts.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_result_peanut = ContainerAnnotation.from_dict(json.loads(f.read()))
            ai_results.append(
                AcdConceptRef(
                    adjusted_concept=AdjustedConceptRef(
                        concept_ref=CodeableConceptRef(
                            type=CodeableConceptRefType.ALLERGEN,
                            code_ref=allergy.code,
                            fhir_path="AllergyIntolerance.code",
                        ),
                        adjusted_text=allergy.code.text,
                    ),
                    acd_response=acd_result_peanut,
                )
            )

        # Load ACD results for reaction of anaphylactic shock
        reaction_counter = 0
        for reaction in allergy.reaction:
            manifestation_counter = 0
            for mf in reaction.manifestation:
                with open(
                    self.resource_path + "/acd/mock_acd_output/anaphylactic_shock.json",
                    "r",
                    encoding="utf-8",
                ) as f:
                    acd_result_shock = ContainerAnnotation.from_dict(
                        json.loads(f.read())
                    )
                    fhirPath = f"AllergyIntolerance.reaction[{reaction_counter}].manifestation[{manifestation_counter}]"
                    ai_results.append(
                        AcdConceptRef(
                            adjusted_concept=AdjustedConceptRef(
                                concept_ref=CodeableConceptRef(
                                    type=CodeableConceptRefType.MANIFESTATION,
                                    code_ref=mf,
                                    fhir_path=fhirPath,
                                ),
                                adjusted_text=mf.text,
                            ),
                            acd_response=acd_result_shock,
                        )
                    )

                manifestation_counter += 1
            reaction_counter += 1

        self._allergy_bundle_update(allergy, expected_json, ai_results)

    def test_single_resource_update_allergy_penicillin(self):
        input_json = (
            self.resource_path
            + "/acd/mock_fhir/input/AllergyIntolerance_penicillin.json"
        )
        expected_json = (
            self.resource_path
            + "/acd/mock_fhir/output/Bundle_update_allergy_penicillin.json"
        )

        allergy = AllergyIntolerance.parse_file(input_json)

        ai_results = []

        # Load ACD results for allergen of penicillin
        with open(
            self.resource_path + "/acd/mock_acd_output/penicillin.json",
            "r",
            encoding="utf-8",
        ) as f:
            acd_result_penicillin = ContainerAnnotation.from_dict(json.loads(f.read()))
            ai_results.append(
                AcdConceptRef(
                    adjusted_concept=AdjustedConceptRef(
                        concept_ref=CodeableConceptRef(
                            type=CodeableConceptRefType.ALLERGEN,
                            code_ref=allergy.code,
                            fhir_path="AllergyIntolerance.code",
                        ),
                        adjusted_text=allergy.code.text,
                    ),
                    acd_response=acd_result_penicillin,
                )
            )

        # Load ACD results for reaction of anaphylactic shock
        for r_idx, reaction in enumerate(allergy.reaction):
            for m_idx, mf in enumerate(reaction.manifestation):
                if "HIVES" in mf.text:
                    with open(
                        self.resource_path + "/acd/mock_acd_output/hives.json",
                        "r",
                        encoding="utf-8",
                    ) as f:
                        acd_result_hives = ContainerAnnotation.from_dict(
                            json.loads(f.read())
                        )
                        ai_results.append(
                            AcdConceptRef(
                                adjusted_concept=AdjustedConceptRef(
                                    concept_ref=CodeableConceptRef(
                                        type=CodeableConceptRefType.MANIFESTATION,
                                        code_ref=mf,
                                        fhir_path=f"AllergyIntolerance.reaction[{r_idx}].manifestation[{m_idx}]",
                                    ),
                                    adjusted_text=mf.text,
                                ),
                                acd_response=acd_result_hives,
                            )
                        )
                elif "RASH" in mf.text:
                    with open(
                        self.resource_path + "/acd/mock_acd_output/rash.json",
                        "r",
                        encoding="utf-8",
                    ) as f:
                        acd_result_rash = ContainerAnnotation.from_dict(
                            json.loads(f.read())
                        )

                        ai_results.append(
                            AcdConceptRef(
                                adjusted_concept=AdjustedConceptRef(
                                    concept_ref=CodeableConceptRef(
                                        type=CodeableConceptRefType.MANIFESTATION,
                                        code_ref=mf,
                                        fhir_path=f"AllergyIntolerance.reaction[{r_idx}].manifestation[{m_idx}]",
                                    ),
                                    adjusted_text=mf.text,
                                ),
                                acd_response=acd_result_rash,
                            )
                        )

        self._allergy_bundle_update(allergy, expected_json, ai_results)

    def test_no_bundle_created(self):
        input_json = (
            self.resource_path
            + "/acd/mock_fhir/input/AllergyIntolerance_not_valid_allergy.json"
        )

        allergy = AllergyIntolerance.parse_file(input_json)
        ai_results = []
        with open(
            self.resource_path + "/acd/mock_acd_output/abcd.json", "r", encoding="utf-8"
        ) as f:
            acd_result_abcd = ContainerAnnotation.from_dict(json.loads(f.read()))
            ai_results.append(
                AcdConceptRef(
                    adjusted_concept=AdjustedConceptRef(
                        concept_ref=CodeableConceptRef(
                            type=CodeableConceptRefType.ALLERGEN,
                            code_ref=allergy.code,
                            fhir_path="AllergyIntolerance.code",
                        ),
                        adjusted_text=allergy.code.text,
                    ),
                    acd_response=acd_result_abcd,
                )
            )

        self._allergy_bundle_update(allergy, None, ai_results)


if __name__ == "__main__":
    unittest.main()
