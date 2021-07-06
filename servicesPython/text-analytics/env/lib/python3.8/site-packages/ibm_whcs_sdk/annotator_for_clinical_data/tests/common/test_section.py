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

class TestSectionAnnotation(object):

    @staticmethod
    def test_section_annotation(annotation_list=None):
        if annotation_list is not None:
            for annotation in annotation_list:
                assert annotation.type is not None
                if annotation.section_type is not None:
                    assert len(annotation.section_type) > 0
                assert annotation.begin > 0
                assert annotation.end > annotation.begin
                if annotation.covered_text is not None:
                    assert len(annotation.covered_text) > 0
                if annotation.trigger is not None:
                    section_trigger = annotation.trigger
                    assert section_trigger.begin > 0
                    assert section_trigger.end > section_trigger.begin
                    assert section_trigger.covered_text is not None
                    assert section_trigger.source is not None
                    assert section_trigger.section_normalized_name is not None
                    assert section_trigger.type is not None
