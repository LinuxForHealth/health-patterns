# coding: utf-8

# Copyright 2018 IBM All Rights Reserved.
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


class TestAnnotatorOutput(object):

    @staticmethod
    def test_annotator_output(annotation_list=None):
        if annotation_list is not None:
            for annotation in annotation_list:
                if annotation.id is not None:
                    assert len(annotation.id) > 0
                if annotation.type is not None:
                    assert len(annotation.type) > 0
                assert annotation.begin > 0
                assert annotation.end > annotation.begin
                assert annotation.covered_text is not None
                if annotation.uid is not None:
                    assert annotation.uid > 0
                if annotation.cui is not None:
                    assert annotation.cui > 0
                if annotation.preferred_name is not None:
                    assert len(annotation.preferred_name) > 0
                if annotation.source is not None:
                    assert len(annotation.source) > 0
                if annotation.source_version is not None:
                    assert len(annotation.source_version) > 0
                if annotation.name is not None:
                    assert len(annotation.name) > 0
                if annotation.icd9_code is not None:
                    assert len(annotation.icd9_code) > 0
                if annotation.icd10_code is not None:
                    assert len(annotation.icd10_code) > 0
                if annotation.nci_code is not None:
                    assert len(annotation.nci_code) > 0
                if annotation.snomed_concept_id is not None:
                    assert len(annotation.snomed_concept_id) > 0
                if annotation.mesh_id is not None:
                    assert len(annotation.mesh_id) > 0
                if annotation.rx_norm_id is not None:
                    assert len(annotation.rx_norm_id) > 0
                if annotation.loinc_id is not None:
                    assert len(annotation.loinc_id) > 0
                if annotation.vocabs is not None:
                    assert len(annotation.vocabs) > 0
                if annotation.section_normalized_name is not None:
                    assert len(annotation.section_normalized_name) > 0
                if annotation.section_surface_form is not None:
                    assert len(annotation.section_surface_form) > 0
                if annotation.cpt_code is not None:
                    assert len(annotation.cpt_code) > 0
                if annotation.hcc_code is not None:
                    assert len(annotation.hcc_code) > 0
                if annotation.trigegr is not None:
                    assert len(annotation.trigger) > 0
                if annotation.dimension is not None:
                    assert len(annotation.dimension) > 0
                if annotation.first_value is not None:
                    assert len(annotation.first_value) > 0
                if annotation.second_value is not None:
                    assert len(annotation.second_value) > 0
                if annotation.ef_alphabetic_value_normalized_name is not None:
                    assert len(annotation.ef_alphabetic_value_normalized_name) > 0
                if annotation.ef_alphabetic_value_surface_form is not None:
                    assert len(annotation.ef_alphabetic_value_surface_form) > 0
                if annotation.ef_term_normalized_name is not None:
                    assert len(annotation.ef_term_normalized_name) > 0
                if annotation.ef_term_surface_form is not None:
                    assert len(annotation.ef_term_surface_form) > 0
                if annotation.ef_suffix_normalized_name is not None:
                    assert len(annotation.ef_suffix_normalized_name) > 0
                if annotation.ef_suffix_surface_form is not None:
                    assert len(annotation.ef_suffix_surface_form) > 0
                if annotation.lab_type_normalized_name is not None:
                    assert len(annotation.lab_type_normalized_name) > 0
                if annotation.lab_type_surface_form is not None:
                    assert len(annotation.lab_type_surface_form) > 0
                if annotation.procedure_normalized_name is not None:
                    assert len(annotation.procedure_normalized_name) > 0
                if annotation.procedure_surface_form is not None:
                    assert len(annotation.procedure_surface_form) > 0
                if annotation.smoke_term_normalized_name is not None:
                    assert len(annotation.smoke_term_normalized_name) > 0
                if annotation.smoke_term_surface_form is not None:
                    assert len(annotation.smoke_term_surface_form) > 0
                if annotation.symptom_disease_normalized_name is not None:
                    assert len(annotation.symptom_disease_normalized_name) > 0
                if annotation.symptom_disease_surface_form is not None:
                    assert len(annotation.symptom_disease_surface_form) > 0
                if annotation.low_value is not None:
                    assert len(annotation.low_value) > 0
                if annotation.participation is not None:
                    assert len(annotation.participation) > 0
                if annotation.current is not None:
                    assert len(annotation.current) > 0
                if annotation.lab_value is not None:
                    assert len(annotation.lab_value) > 0
                if annotation.date_in_milliseconds is not None:
                    assert len(annotation.date_in_milliseconds) > 0
                if annotation.is_range is not None:
                    assert len(annotation.is_range) > 0
#            if annotation.negated is not None:
#                assert annotation.negated isinstance(bool)
#            if annotation.hypothetical is not None:
#                assert annotation.hypothetical isinstance(bool)
                if annotation.drug is not None:
                    for drug_obj in annotation.drug:
                        assert drug_obj is not None
                if annotation.values is not None:
                    for value in annotation.values:
                        assert value is not None
                if annotation.concept is not None:
                    TestAnnotatorOutput.test_annotator_output(annotation.concept)
                if annotation.disambiguation_data is not None:
                    assert annotation.disambiguation_data.validity is not None
                if annotation.cancer is not None:
                    for cancer_obj in annotation.cancer:
                        assert cancer_obj is not None
