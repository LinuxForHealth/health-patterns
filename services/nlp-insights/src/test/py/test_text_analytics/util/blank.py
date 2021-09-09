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


# The ACD output can get very long and is a pain to put into the GT output.
# Testcases should call this to remove the ACD output from the built FHIR JSON, allowing the ACD field to be blank in the GT JSON.
# Parameters:
#   fhir_resource_dict - dictionary containing a FHIR resource (eg Condition)
def blank_acd_evidence_detail_in_resource(fhir_resource_dict):
    del fhir_resource_dict

# This no longer works with the change to use the CDM IG.  If we need this once we move ACD output to MinIO it will need to be reworked.
    # next = fhir_resource_dict['meta']
    # next = next['extension']
    # next = next[0]
    # next = next['extension']   # insight/result
    # for item in next:
    #     for key in item:
    #         if key == 'extension':
    #             next = item
    #             next = next['extension']   # insight-entry
    #             next = next[1]             # evidence-detail
    #             next = next['valueAttachment']
    #             blank_dict = {}
    #             next['data'] = json.dumps(blank_dict).encode('utf-8')


# The ACD output can get very long and is a pain to put into the GT output.
# Testcases should call this to remove the ACD output from the built FHIR JSON, allowing the ACD field to be blank in the GT JSON.
# Parameters:
#   fhir_resource_dict - dictionary containing a FHIR Bundle
def blank_acd_evidence_detail_in_bundle(fhir_bundle_dict):
    entries = fhir_bundle_dict['entry']
    for entry in entries:
        nextEntry = entry['resource']
        blank_acd_evidence_detail_in_resource(nextEntry)
