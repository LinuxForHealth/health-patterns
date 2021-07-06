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

class TestConceptValueAnnotation(object):

    @staticmethod
    def test_concept_value(annotation_list=None):
        if annotation_list is not None:
            for annotation in annotation_list:
                if annotation.id is not None:
                    assert len(annotation.id) > 0
                if annotation.type is not None:
                    assert len(annotation.type) > 0
                assert annotation.begin is not None
                assert annotation.end is not None
                assert annotation.covered_text is not None
                if annotation.uid is not None:
                 assert annotation.uid > 0
                if annotation.preferred_name is not None:
                    assert len(annotation.preferred_name) > 0
                if annotation.source is not None:
                    assert len(annotation.source) > 0
                if annotation.cui is not None:
                    assert len(annotation.cui) > 0
                if annotation.dimension is not None:
                    assert len(annotation.dimension) > 0
                if annotation.trigger is not None:
                    assert len(annotation.trigger) > 0
                if annotation.value is not None:
                    assert len(annotation.value) > 0
                if annotation.section_normalized_name is not None:
                    assert len(annotation.section_normalized_name) > 0
                if annotation.section_surface_form is not None:
                    assert len(annotation.section_surface_form) > 0
