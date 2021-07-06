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

class TestInsightModel(object):

    @staticmethod
    def test_insight_model_data(data=None):
        if data is not None:
            assert data is not None
            if data.diagnosis is not None:
                assert len(data.diagnosis._to_dict()) > 0
                if data.diagnosis.usage is not None:
                    assert len(data.diagnosis.usage._to_dict()) > 0
                if data.diagnosis.modifiers is not None:
                    assert len(data.diagnosis.modifiers._to_dict()) > 0
            if data.procedure is not None:
                assert len(data.procedure._to_dict()) > 0
                if data.procedure.usage is not None:
                    assert len(data.procedure.usage._to_dict()) > 0
                if data.procedure.task is not None:
                    assert len(data.procedure.task._to_dict()) > 0
                if data.procedure.type is not None:
                    assert len(data.procedure.type._to_dict()) > 0
                if data.procedure.modifiers is not None:
                    assert len(data.procedure.modifiers._to_dict()) > 0
            if data.medication is not None:
                assert len(data.medication._to_dict()) > 0
                if data.medication.usage is not None:
                    assert len(data.medication.usage._to_dict()) > 0
                if data.medication.started is not None:
                    assert len(data.medication.started._to_dict()) > 0
                if data.medication.stopped is not None:
                    assert len(data.medication.stopped._to_dict()) > 0
                if data.medication.dose_changed is not None:
                    assert len(data.medication.dose_changed._to_dict()) > 0
                if data.medication.adverse is not None:
                    assert len(data.medication.adverse._to_dict()) > 0
            if data.normality is not None:
                assert len(data.normality._to_dict()) > 0
                if data.normality.usage is not None:
                    assert len(data.normality.usage._to_dict()) > 0
                if data.normality.evidence is not None:
                    for entry in data.normality.evidence:
                        assert entry is not None
