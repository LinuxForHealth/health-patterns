# coding: utf-8

# (C) Copyright IBM Corp. 2020.
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
Natural Language Processing (NLP) service featuring a set of medical domain annotators for
use in detecting entities and medical concepts from unstructured data. Multiple annotators
may be invoked from a single request.
"""

from enum import Enum
from typing import BinaryIO, Dict, List, TextIO, Union
import json

from ibm_cloud_sdk_core import BaseService, DetailedResponse, ApiException
from ibm_cloud_sdk_core.authenticators.authenticator import Authenticator
from ibm_cloud_sdk_core.get_authenticator import get_authenticator_from_environment
from ibm_cloud_sdk_core.utils import convert_model
from ibm_whcs_sdk.common import get_sdk_headers

##############################################################################
# Exception Handling
##############################################################################
class ACDException(ApiException):
    """
    Custom exception class for errors returned from ACD APIs.
    :param int code: The HTTP status code returned.
    :param str message: A message describing the error.
    :param str correlationId: A code to associate to the ACD error
    """

    def __init__(self, code, message=None, correlation_id=None):
        self.message = message
        self.code = code
        self.correlation_id = correlation_id

    def __str__(self):
        msg = ('Error: ' + str(self.message) + ', Code: ' + str(self.code)
               + ', CorrelationId: ' + str(self.correlation_id))
        return msg

##############################################################################
# Service
##############################################################################

class AnnotatorForClinicalDataV1(BaseService):
    """The Annotator for Clinical Data (ACD) V1 service."""

    DEFAULT_SERVICE_URL = 'https://annotator-for-clinical-data-acd.cloud.ibm.com/services/clinical_data_annotator/api'
    DEFAULT_SERVICE_NAME = 'annotator_for_clinical_data_acd'

    @classmethod
    def new_instance(cls,
                     version: str,
                     service_name: str = DEFAULT_SERVICE_NAME,
                    ) -> 'AnnotatorForClinicalDataAcdV1':
        """
        Return a new client for the Annotator for Clinical Data (ACD) service using
               the specified parameters and external configuration.

        :param str version: The release date of the version of the API you want to
               use. Specify dates in YYYY-MM-DD format.
        """
        if version is None:
            raise ValueError('version must be provided')

        authenticator = get_authenticator_from_environment(service_name)
        service = cls(
            version,
            authenticator
            )
        service.configure_service(service_name)
        return service

    def __init__(self,
                 version: str,
                 authenticator: Authenticator = None,
                ) -> None:
        """
        Construct a new client for the Annotator for Clinical Data (ACD) service.

        :param str version: The release date of the version of the API you want to
               use. Specify dates in YYYY-MM-DD format.

        :param Authenticator authenticator: The authenticator specifies the authentication mechanism.
               Get up to date information from https://github.com/IBM/python-sdk-core/blob/master/README.md
               about initializing the authenticator of your choice.
        """
        if version is None:
            raise ValueError('version must be provided')

        BaseService.__init__(self,
                             service_url=self.DEFAULT_SERVICE_URL,
                             authenticator=authenticator)
        self.version = version


    #########################
    # Request ACD
    #########################

    def request_acd(self, request=None):
        """
        Build the request in preparation for invoking ACD.
        """

        try:
            response = self.send(request)
            if 200 <= response.status_code <= 299:
                return response
        except ApiException as api_except:
            final = api_except._get_error_message
            if api_except.message is not None:
                error_message = api_except.message
            else:
                error_message = "No error message available"
            if api_except.code is not None:
                status_code = api_except.code
            if (
                api_except.http_response is not None
                and api_except.http_response.headers is not None
                and api_except.http_response.headers.get('x-correlation-id') is not None
                ):
                correlation_id = api_except.http_response.headers.get('x-correlation-id')
            else:
                correlation_id = "None"
            raise ACDException(status_code, error_message, correlation_id)

        return final

    #########################
    # Profiles
    #########################


    def get_profiles(self, **kwargs) -> DetailedResponse:
        """
        Get list of available persisted profiles.

        Returns a summary including ID and description of the available persisted
        profiles.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ListStringWrapper` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_profiles')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/profiles'
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def create_profile(self, *, new_id: str = None, new_name: str = None, new_description: str = None, new_published_date: str = None, new_publish: bool = None, new_version: str = None, new_cartridge_id: str = None, new_annotators: List['Annotator'] = None, **kwargs) -> DetailedResponse:
        """
        Persist a new profile.

        This API persists a new profile.  A profile is identified by an ID.  This ID can
        optionally be specified as part of the request body when invoking <b>POST
        /v1/analyze</b> API.  A profile contains annotator configuration information that
        will be applied to the annotators specified in the annotator flow.<p>If a caller
        would choose to have the ID of the new profile generated on their behalf, then in
        the request body the "id" field of the profile definition should be an empty
        string ("").  The auto-generated ID would be a normalized form of the "name" field
        from the profile definition.<p><b>Sample Profile #1</b><br>A profile definition
        that configures the 'concept_detection' annotator to use the UMLS umls.latest
        library.<br><pre>{<br>  "id": "acd_profile_cd_umls_latest",<br>  "name": "Profile
        for the latest Concept Detection UMLS Library",<br>  "description": "Provides
        configurations for running Concept Detection with the latest UMLS library",<br>
        "annotators": [<br>    {<br>      "name": "concept_detection",<br>
        "parameters": {<br>         "libraries": ["umls.latest"]<br>       }<br>    }<br>
        ]<br>}</pre><p><b>Sample Profile #2</b><br>A profile definition that configures
        the 'concept_detection' annotator to exclude any annotations where the semantic
        type does not equal 'neop'.<br><pre>{<br>  "id": "acd_profile_cd_neop_only",<br>
        "name": "Profile for Concept Detection neop Semantic Type",<br>  "description":
        "Concept Detection configuration fitler to exclude annotations where semantic type
        does not equal 'neop'.",<br>  "annotators": [<br>    {<br>       "name":
        "concept_detection",<br>       "configurations": [<br>         {<br>
        "filter": {<br>             "target": "unstructured.data.concepts",<br>
         "condition": {<br>                "type": "match",<br>                "field":
        "semanticType",<br>                "values": [<br>                   "neop"<br>
                     ],<br>                "not": false,<br>
        "caseInsensitive": false,<br>                "operator": "equals"<br>
        }<br>            }<br>         }<br>       ]<br>    }<br>  ]<br>}</pre>.

        :param str new_id: (optional)
        :param str new_name: (optional)
        :param str new_description: (optional)
        :param str new_published_date: (optional)
        :param bool new_publish: (optional)
        :param str new_version: (optional)
        :param str new_cartridge_id: (optional)
        :param List[Annotator] new_annotators: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if new_annotators is not None:
            new_annotators = [ convert_model(x) for x in new_annotators ]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='create_profile')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'id': new_id,
            'name': new_name,
            'description': new_description,
            'publishedDate': new_published_date,
            'publish': new_publish,
            'version': new_version,
            'cartridgeId': new_cartridge_id,
            'annotators': new_annotators
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/profiles'
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_acd(request)
        return response


    def get_profile(self, id: str, **kwargs) -> DetailedResponse:
        """
        Get details of a specific profile.

        Using the specified profile ID, retrieves the profile definition.

        :param str id: Profile ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `AcdProfile` object
        """

        if id is None:
            raise ValueError('id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_profile')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/profiles/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def update_profile(self, id: str, *, new_id: str = None, new_name: str = None, new_description: str = None, new_published_date: str = None, new_publish: bool = None, new_version: str = None, new_cartridge_id: str = None, new_annotators: List['Annotator'] = None, **kwargs) -> DetailedResponse:
        """
        Update a persisted profile definition.

        Using the specified Profile ID, updates the profile definition.  This is a
        complete replacement of the existing profile definition using the JSON object
        provided in the request body.

        :param str id: Profile ID.
        :param str new_id: (optional)
        :param str new_name: (optional)
        :param str new_description: (optional)
        :param str new_published_date: (optional)
        :param bool new_publish: (optional)
        :param str new_version: (optional)
        :param str new_cartridge_id: (optional)
        :param List[Annotator] new_annotators: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if id is None:
            raise ValueError('id must be provided')
        if new_annotators is not None:
            new_annotators = [ convert_model(x) for x in new_annotators ]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='update_profile')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'id': new_id,
            'name': new_name,
            'description': new_description,
            'publishedDate': new_published_date,
            'publish': new_publish,
            'version': new_version,
            'cartridgeId': new_cartridge_id,
            'annotators': new_annotators
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/profiles/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='PUT',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_acd(request)
        return response


    def delete_profile(self, id: str, **kwargs) -> DetailedResponse:
        """
        Delete a persisted profile.

        Using the specified profile ID, deletes the profile from the list of persisted
        profiles.

        :param str id: Profile ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if id is None:
            raise ValueError('id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='delete_profile')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/profiles/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response

    #########################
    # Flows
    #########################


    def get_flows(self, **kwargs) -> DetailedResponse:
        """
        Get list of available persisted flows.

        Returns a summary including ID and description of the available persisted flows.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ListStringWrapper` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_flows')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/flows'
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def create_flows(self, *, new_id: str = None, new_name: str = None, new_description: str = None, new_published_date: str = None, new_publish: bool = None, new_version: str = None, new_cartridge_id: str = None, new_annotator_flows: List['AnnotatorFlow'] = None, **kwargs) -> DetailedResponse:
        """
        Persist a new flow definition.

        This API persists a new flow.  A flow is identified by an ID.  This ID can
        optionally be specified as part of the request body when invoking <b>POST
        /v1/analyze</b> API.  A flow definition contains a list one or more annotators,
        and optionally can include annotator configuration, a flow ID, and/or flow
        sequence.<p>If a caller would choose to have the ID of the new flow generated on
        their behalf, then in the request body the "id" field of the flow definition
        should be an empty string ("").  The auto-generated ID would be a normalized form
        of the "name" field from the flow definition.<p><p><b>Sample Flow #1</b><br>A flow
        definition that includes two annotators.<br><pre>{<br>  "id": "flow_simple",<br>
        "name": "flow simple",<br>  "description": "A simple flow with two
        annotators",<br>  "annotatorFlows": [<br>      {<br>       "flow": {<br>
        "elements": [<br>             {<br>               "annotator": {<br>
            "name": "concept_detection"<br>                }<br>             },<br>
             {<br>               "annotator": {<br>                   "name":
        "symptom_disease"<br>                }<br>             }<br>           ],<br>
         "async": false<br>        }<br>      }<br>   ]<br>}</pre><p><b>Sample Flow
        #2</b><br>A flow definition that includes the 'concept_detection' annotator and
        configuration details for the 'concept_detection' annotator.<br><pre>{<br>  "id":
        "flow_concept_detection_exclude_non_neop",<br>  "name": "flow concept detection
        exclude non neop",<br>  "description": "A flow excluding detected concepts that do
        not have 'neop' semantic type",<br>  "annotatorFlows": [<br>      {<br>
        "flow": {<br>          "elements": [<br>             {<br>
        "annotator": {<br>                   "name": "concept_detection",<br>
             "configurations": [<br>                      {<br>
        "filter": {<br>                           "target":
        "unstructured.data.concepts",<br>                           "condition": {<br>
                                 "type": "match",<br>
        "field": "semanticType",<br>                              "values": [<br>
                               "neop"<br>                                ],<br>
                          "not": false,<br>
        "caseInsensitive": false,<br>                              "operator":
        "equals"<br>                            }<br>                         }<br>
                      }<br>                    ]<br>                 }<br>
        }<br>         ],<br>       "async": false<br>        }<br>      }<br>
        ]<br>}</pre>.

        :param str new_id: (optional)
        :param str new_name: (optional)
        :param str new_description: (optional)
        :param str new_published_date: (optional)
        :param bool new_publish: (optional)
        :param str new_version: (optional)
        :param str new_cartridge_id: (optional)
        :param List[AnnotatorFlow] new_annotator_flows: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if new_annotator_flows is not None:
            new_annotator_flows = [ convert_model(x) for x in new_annotator_flows ]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='create_flows')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'id': new_id,
            'name': new_name,
            'description': new_description,
            'publishedDate': new_published_date,
            'publish': new_publish,
            'version': new_version,
            'cartridgeId': new_cartridge_id,
            'annotatorFlows': new_annotator_flows
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data, cls=AnnotatorEncoder)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/flows'
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_acd(request)
        return response


    def get_flows_by_id(self, id: str, **kwargs) -> DetailedResponse:
        """
        Get details of a specific flow.

        Using the specified Flow ID, retrieves the flow definition.

        :param str id: Flow ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `AcdFlow` object
        """

        if id is None:
            raise ValueError('id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_flows_by_id')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/flows/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def update_flows(self, id: str, *, new_id: str = None, new_name: str = None, new_description: str = None, new_published_date: str = None, new_publish: bool = None, new_version: str = None, new_cartridge_id: str = None, new_annotator_flows: List['AnnotatorFlow'] = None, **kwargs) -> DetailedResponse:
        """
        Update a persisted flow definition.

        Using the specified Flow ID, updates the persisted flow definition.  This is a
        complete replacement of the existing flow definition using the JSON object
        provided in the request body.

        :param str id: Flow ID.
        :param str new_id: (optional)
        :param str new_name: (optional)
        :param str new_description: (optional)
        :param str new_published_date: (optional)
        :param bool new_publish: (optional)
        :param str new_version: (optional)
        :param str new_cartridge_id: (optional)
        :param List[AnnotatorFlow] new_annotator_flows: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if id is None:
            raise ValueError('id must be provided')
        if new_annotator_flows is not None:
            new_annotator_flows = [ convert_model(x) for x in new_annotator_flows ]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='update_flows')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        data = {
            'id': new_id,
            'name': new_name,
            'description': new_description,
            'publishedDate': new_published_date,
            'publish': new_publish,
            'version': new_version,
            'cartridgeId': new_cartridge_id,
            'annotatorFlows': new_annotator_flows
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data, cls=AnnotatorEncoder)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/flows/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='PUT',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_acd(request)
        return response


    def delete_flows(self, id: str, **kwargs) -> DetailedResponse:
        """
        Delete a persisted flow.

        Using the specified Flow ID, deletes the flow from the list of persisted flows.

        :param str id: Flow ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if id is None:
            raise ValueError('id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='delete_flows')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/flows/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response

    #########################
    # ACD
    #########################


    def run_pipeline(self, *, unstructured: List['UnstructuredContainer'] = None, annotator_flows: List['AnnotatorFlow'] = None, debug_text_restore: bool = None, return_analyzed_text: bool = None, **kwargs) -> DetailedResponse:
        """
        Detect entities & relations from unstructured data.

        <p>This API accepts a JSON request model featuring both the unstructured data to
        be analyzed as well as the desired annotator flow.<p/><p><b>Annotator
        Chaining</b><br/>Sample request invoking both the concept_detection and
        symptom_disease annotators asynchronously. This sample request references
        configurations via a profile id. Profiles define configurations that can be
        referenced within a request. Profile is optional. A default profile is used if no
        profile id is available in the annotator flow. The default profile contains the
        parameters for the concept detection and the attribute detection. An empty profile
        can be used if absolutely no parameters are attached to any annotators. See <a
        href=".." target="_blank">documentation</a> for more information. </p><pre>{<br/>
        "annotatorFlows": [<br/>    {<br/>      "profile" : "default_profile_v1.0", <br/>
            "flow": {<br/>        "elements": [<br/>          {<br/>
        "annotator": {<br/>              "name": "concept_detection"<br/>
        }<br/>          },<br/>          {<br/>            "annotator": {<br/>
         "name": "symptom_disease"<br/>             }<br/>          }<br/>        ],<br/>
              "async": false<br/>      }<br/>    }<br/>  ],<br/>  "unstructured": [<br/>
         {<br/>      "text": "Patient has lung cancer, but did not smoke. She may consider
        chemotherapy as part of a treatment plan."<br/>    }<br/>
        ]<br/>}<br/></pre><p><b>Annotation Filtering</b><br/>Sample request invoking
        concept_detection with a filter defined to exclude any annotations detected from
        concept_detection where the semanticType field does not equal
        "neop".</p><pre>{<br/>  "annotatorFlows": [<br/>    {<br/>      "flow": {<br/>
           "elements": [<br/>          {<br/>            "annotator": {<br/>
        "name": "concept_detection",<br/>              "configurations": [<br/>
            {<br/>                  "filter": {<br/>                     "target":
        "unstructured.data.concepts",<br/>                     "condition": {<br/>
                       "type": "match",<br/>                        "field":
        "semanticType",<br/>                        "values": [<br/>
            "neop"<br/>                         ],<br/>                        "not":
        false,<br/>                        "caseInsensitive": false,<br/>
              "operator": "equals"<br/>                     }<br/>                  }<br/>
                       }<br/>              ]<br/>            }<br/>          }<br/>
        ],<br/>       "async": false<br/>      }<br/>    }<br/>  ],<br/>  "unstructured":
        [<br/>    {<br/>      "text": "Patient has lung cancer, but did not smoke. She may
        consider chemotherapy as part of a treatment plan."<br/>    }<br/>
        ]<br/>}<br/></pre><p><b>Annotators that support annotation filtering:</b> allergy,
        bathing_assistance, cancer, concept_detection, dressing_assistance,
        eating_assistance, ejection_fraction, lab_value, medication, named_entities,
        procedure, seeing_assistance, smoking, symptom_disease, toileting_assistance,
        walking_assistance.</p><hr/><p><b>Annotation Augmentation</b><br/>Sample request
        invoking the cancer annotator and providing a whitelist entry for a new custom
        surface form: "lungcancer".</p><pre>{<br/> "annotatorFlows": [<br/>    {<br/>
        "flow": {<br/>       "elements": [<br/>          {<br/>           "annotator":
        {<br/>             "name": "cancer",<br/>             "configurations": [<br/>
                   {<br/>                 "whitelist": {<br/>                   "name":
        "cancer",<br/>                   "entries": [<br/>                      {<br/>
                     "surfaceForms": [<br/>                   "lungcancer"<br/>
            ],<br/>               "features": {<br/>                   "normalizedName":
        "lung cancer",<br/>                   "hccCode": "9",<br/>
        "icd10Code": "C34.9",<br/>                   "ccsCode": "19",<br/>
          "icd9Code": "162.9",<br/>                   "conceptId": "93880001"<br/>
               }<br/>                      }<br/>                    ]<br/>
          }<br/>                }<br/>              ]<br/>            }<br/>
        }<br/>        ],<br/>       "async": false<br/>      }<br/>    }<br/>  ],<br/>
        "unstructured": [<br/>    {<br/>     "text": "The patient was diagnosed with
        lungcancer, on Dec 23, 2011."<br/>    }<br/>  ]<br/>}<br/></pre><b>Annotators that
        support annotation augmentation:</b> allergy, bathing_assistance, cancer,
        dressing_assistance, eating_assistance, ejection_fraction, lab_value, medication,
        named_entities, procedure, seeing_assistance, smoking, symptom_disease,
        toileting_assistance, walking_assistance.<br/>.

        :param List[UnstructuredContainer] unstructured: (optional)
        :param List[AnnotatorFlow] annotator_flows: (optional)
        :param bool debug_text_restore: (optional) If true, any ReplaceTextChange
               annotations will be left in the container and the modified text before
               restoring to original form will stored in the metadata that is returned.
               Otherwise, these annotations and modified text will be removed from the
               container.
        :param bool return_analyzed_text: (optional) Set this to true to show the
               analyzed text in the response.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if unstructured is not None:
            unstructured = [ convert_model(x) for x in unstructured ]
        if annotator_flows is not None:
            annotator_flows = [ convert_model(x) for x in annotator_flows ]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='run_pipeline')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'debug_text_restore': debug_text_restore,
            'return_analyzed_text': return_analyzed_text
        }

        data = {
            'unstructured': unstructured,
            'annotatorFlows': annotator_flows
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/analyze'
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_acd(request)
        return response


    def analyze_org(self, unstructured=None, annotator_flows=None, **kwargs):
        """
        Detect entities & relations from unstructured data and return as 'dict'.
        <p>This API accepts a JSON request model featuring both the unstructured data to be analyzed as well as
        the desired annotator flow.<p/><p><b>Annotator Chaining</b><br/>Sample request invoking both the
        concept_detection and symptom_disease annotators asynchronously.</p><pre>{<br/>  \"annotatorFlows\":
        [<br/>    {<br/>      \"flow\": {<br/>        \"elements\": [<br/>          {<br/>
        \"annotator\": {<br/>              \"name\": \"concept_detection\"<br/>            }<br/>          },
        <br/>          {<br/>            \"annotator\": {<br/>              \"name\": \"symptom_disease\"<br/>
                    }<br/>          }<br/>        ],<br/>        \"async\": true<br/>      }<br/>    }<br/>  ],
                    <br/>  \"unstructured\": [<br/>    {<br/>      \"text\": \"Patient has lung cancer,
                    but did not smoke. She may consider chemotherapy as part of a treatment plan.\"<br/>    }
                    <br/>  ]<br/>}<br/></pre><p><b>Annotation Filtering</b><br/>
                    Sample request invoking concept_detection with a filter defined to exclude any annotations
                    derived from concept_detection where the semanticType field does not equal \"neop\".
                    </p><pre>{<br/>  \"annotatorFlows\": [<br/>    {<br/>      \"flow\": {<br/>
                    \"elements\": [<br/>          {<br/>            \"annotator\": {<br/>
                    \"name\": \"concept_detection\",<br/>              \"configurations\": [<br/>
                    {<br/>                  \"filter\": {<br/>
                    \"target\": \"unstructured.data.concepts\",<br/>                     \"condition\": {<br/>
                    \"type\": \"match\",<br/>  \"field\": \"semanticType\",<br/>
                    \"values\": [<br/>                           \"neop\"<br/>                         ],
                    <br/>                        \"not\": false,<br/>
                    \"caseInsensitive\": false,<br/>                        \"operator\": \"equals\"
                    <br/>                     }<br/>                  }<br/>                }<br/>
                    ]<br/>            }<br/>          }<br/>        ],<br/>       \"async\": false<br/>
                    }<br/>    }<br/>  ],<br/>  \"unstructured\": [<br/>    {<br/>
                    \"text\": \"Patient has lung cancer, but did not smoke. She may consider chemotherapy as
                    part of a treatment plan.\"<br/>    }<br/>  ]<br/>}<br/></pre><p><b>Annotators that support
                    annotation filtering:</b> allergy, bathing_assistance, cancer, concept_detection,
                    dressing_assistance, eating_assistance, ejection_fraction, lab_value, medication, named_entities,
                    procedure, seeing_assistance, smoking, symptom_disease, toileting_assistance, walking_assistance.
                    </p><hr/><p><b>Annotation Augmentation</b><br/>Sample request invoking the cancer annotator and
                    providing a whitelist entry for a new custom surface form: \"lungcancer\".</p><pre>{<br/>
                    \"annotatorFlows\": [<br/>    {<br/>     \"flow\": {<br/>       \"elements\": [<br/>
                    {<br/>           \"annotator\": {<br/>             \"name\": \"cancer\",<br/>
                    \"configurations\": [<br/>                {<br/>                 \"whitelist\": {<br/>
                    \"name\": \"cancer\",<br/>                   \"entries\": [<br/>
                    {<br/>                  \"surfaceForms\": [<br/>                   \"lungcancer\"<br/>
                    ],<br/>               \"features\": {<br/>                   \"normalizedName\":
                    \"lung cancer\",<br/>                   \"hccCode\": \"9\",<br/>
                    \"icd10Code\": \"C34.9\",<br/>                   \"ccsCode\": \"19\",<br/>
                    \"icd9Code\": \"162.9\",<br/>                   \"conceptId\": \"93880001\"<br/>
                    }<br/>                      }<br/>                    ]<br/>                  }<br/>
                    }<br/>              ]<br/>            }<br/>          }<br/>        ],<br/>
                    \"async\": false<br/>      }<br/>    }<br/>  ],<br/> \"unstructured\": [<br/>    {<br/>
                    \"text\": \"The patient was diagnosed with lungcancer, on Dec 23, 2011.\"<br/>    }<br/>
                    ]<br/>}<br/></pre><b>Annotators that support annotation augmentation:</b> allergy,
                    bathing_assistance, cancer, dressing_assistance, eating_assistance, ejection_fraction,
                    lab_value, medication, named_entities, procedure, seeing_assistance, smoking, symptom_disease,
                    toileting_assistance, walking_assistance.<br/>.
        :param list[UnstructuredContainer] unstructured:
        :param list[AnnotatorFlow] annotator_flows:
        :return: A `DetailedResponse` containing the result, headers and HTTP status code
        :rtype: DetailedResponse
        """
        if unstructured is not None:
            unstructured = [x._to_dict() if hasattr(x, "_to_dict") else x for x in unstructured]
        if annotator_flows is not None:
            annotator_flows = [x._to_dict() if hasattr(x, "_to_dict") else x for x in annotator_flows]

        headers = {'content-type': 'application/json'}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V2', operation_id='analyze_org')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        params = {
            'version': self.version
        }
        data = {
            'unstructured': unstructured,
            'annotatorFlows': annotator_flows
        }
        url = '/v1/analyze'
        data = json.dumps(data, cls=AnnotatorEncoder)
        request = self.prepare_request(method='POST', url=url, headers=headers, params=params, data=data)
        response = self.request_acd(request)

        return response

    # Manually added method.
    def analyze(self, text, flow, **kwargs):
        """
        Detect entities & relations from unstructured data and return as 'ContainerGroup'.
        :param str or list[str] text: Text to be analyzed.
        :param Flow flow: The annotator flow definition.
        :return: A 'ContainerGroup' object
        :rtype: watson_health_cognitive_services.annotator_for_clinical_data_v1.ContainerAnnotation for single text
                or watson_health_cognitive_services.annotator_for_clincial_data_v1.ContainerGroup for test array
        """

        annotator_flow = AnnotatorFlow(flow=flow)
        list_annotator_flow = [annotator_flow]
        list_unstructure_container = []
        if isinstance(text, list):
            for item in text:
                unstructured_container = UnstructuredContainer(text=item)
                list_unstructure_container.append(unstructured_container)
            result = (ContainerGroup._from_dict(self.analyze_org(list_unstructure_container,
                                                                 list_annotator_flow, **kwargs).get_result()))
        else:
            unstructured_container = UnstructuredContainer(text=text)
            list_unstructure_container = [unstructured_container]
            result = (ContainerGroup._from_dict(self.analyze_org(list_unstructure_container,
                                                                 list_annotator_flow, **kwargs).get_result()).unstructured[0].data)

        return result


    def run_pipeline_with_flow(self, flow_id: str, return_analyzed_text: bool, analytic_flow_bean_input: Union['AnalyticFlowBeanInput', str, TextIO], *, content_type: str = None, debug_text_restore: bool = None, **kwargs) -> DetailedResponse:
        """
        analyze with a pre-specified flow.

        <p>This API accepts a flow identifier as well as a <emph>TEXT</emph> or a
        <emph>JSON</emph> request model featuring the unstructured text to be analyzed.
        <p/><p><b>JSON request model with unstructured text </b></p><pre>{<br/>
        "unstructured": [<br/>    {<br/>      "text": "Patient has lung cancer, but did
        not smoke. She may consider chemotherapy as part of a treatment plan."<br/>
        }<br/>  ]<br/>}<br/></pre><p><b>JSON request model with existing annotations
        </b><br/></p><pre>{<br> "unstructured": [<br>    {<br>      "text": "Patient will
        not start on cisplatin 80mg on 1/1/2018. Patient is also diabetic.",<br>
        "data": {<br>        "concepts": [<br>          {<br>            "cui":
        "C0030705",<br>            "preferredName": "Patients",<br>
        "semanticType": "podg",<br>            "source": "umls",<br>
        "sourceVersion": "2017AA",<br>            "type":
        "umls.PatientOrDisabledGroup",<br>            "begin": 0,<br>            "end":
        7,<br>            "coveredText": "Patient"<br>          }<br> ]<br>      }  <br>
         } <br> ]<br>}<br></pre>.

        :param str flow_id: flow identifier .
        :param bool return_analyzed_text: Set this to true to show the analyzed
               text in the response.
        :param AnalyticFlowBeanInput analytic_flow_bean_input: Input request data
               in TEXT or JSON format .
        :param str content_type: (optional) The type of the input. A character
               encoding can be specified by including a `charset` parameter. For example,
               'text/plain;charset=utf-8'.
        :param bool debug_text_restore: (optional) If true, any ReplaceTextChange
               annotations will be left in the container and the modified text before
               restoring to original form will be returned in the metadata.  Otherwise,
               these annotations and modified text will be removed from the container.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if flow_id is None:
            raise ValueError('flow_id must be provided')
        if return_analyzed_text is None:
            raise ValueError('return_analyzed_text must be provided')
        if analytic_flow_bean_input is None:
            raise ValueError('analytic_flow_bean_input must be provided')
        if isinstance(analytic_flow_bean_input, AnalyticFlowBeanInput):
            analytic_flow_bean_input = convert_model(analytic_flow_bean_input)
            content_type = content_type or 'application/json'
        headers = {
            'Content-Type': content_type
        }
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='run_pipeline_with_flow')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'return_analyzed_text': return_analyzed_text,
            'debug_text_restore': debug_text_restore
        }

        if isinstance(analytic_flow_bean_input, dict):
            data = json.dumps(analytic_flow_bean_input)
            if content_type is None:
                headers['content-type'] = 'application/json'
        else:
            data = analytic_flow_bean_input

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/analyze/{0}'.format(*self.encode_path_vars(flow_id))
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.request_acd(request)
        return response


    def analyze_with_flow_org(self, flow_id, request, content_type='text/plain', **kwargs):
        """
        Analyze with a persisted flow and return as a 'dict'.
        <p>This API accepts a flow identifier as well as a <emph>TEXT</emph> or a <emph>JSON</emph> request model
        featuring the unstructured text to be analyzed. <p/><p><b>JSON request model with unstructured text
        </b></p><pre>{<br/>  \"unstructured\": [<br/>    {<br/>      \"text\": \"Patient has lung cancer,
        but did not smoke. She may consider chemotherapy as part of a treatment plan.\"<br/>    }<br/>  ]
        <br/>}<br/></pre><p><b>JSON request model with existing annotations </b><br/></p><pre>{<br> \"unstructured\":
        [<br>    {<br>      \"text\": \"Patient will not start on cisplatin 80mg on 1/1/2018. Patient is also
        diabetic.\",<br>      \"data\": {<br>        \"concepts\": [<br>          {<br>            \"cui\":
        \"C0030705\",<br>            \"preferredName\": \"Patients\",<br>            \"semanticType\": \"podg\",
        <br>            \"source\": \"umls\",<br>            \"sourceVersion\": \"2017AA\",<br>            \"type\":
        \"umls.PatientOrDisabledGroup\",<br>            \"begin\": 0,<br>            \"end\": 7,<br>
        \"coveredText\": \"Patient\"<br>          }<br> ]<br>      }  <br>    } <br> ]<br>}<br></pre>.
        :param str flow_id: flow identifier .
        :param RequestContainer request: Input request data in TEXT or JSON format .
        :param str content_type: The type of the input: text/plain or application/json. A character encoding can be
        specified by including a `charset` parameter. For example, 'text/plain;charset=utf-8'.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code
        :rtype: Detailed Response
        """
        headers = {
            'content-type': content_type
        }

        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V2', operation_id='analyze_with_flow_org')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        params = {
            'version': self.version
        }
        if content_type == 'application/json' and isinstance(request, dict):
            data = json.dumps(request)
        else:
            data = request
        url = '/v1/analyze/{0}'.format(flow_id)
        request = self.prepare_request(method='POST', url=url, headers=headers, params=params, data=data)
        response = self.request_acd(request)

        return response

    # Manually added method.
    def analyze_with_flow(self, flow_id, text, **kwargs):
        """
        Analyze with a persisted flow and return as a 'ContainerGroup'.
        :param str flow_id: The ID of a persisted flow.
        :param str or UnstructuredContainer or list[UnstructuredContainer] text: Text to be analyzed.
        :return: A 'ContainerGroup' object
        :rtype: watson_health_cognitive_services.annotator_for_clinical_data_v1.ContainerAnnotation
        """

        if isinstance(text, list):

            request_container = RequestContainer(text)
            result = self.analyze_with_flow_org(flow_id, request_container._to_dict(), 'application/json', **kwargs)
            result = ContainerGroup._from_dict(result.get_result())
        elif isinstance(text, UnstructuredContainer):

            list_unstructured_container = [text]
            request_container = RequestContainer(list_unstructured_container)
            result = self.analyze_with_flow_org(flow_id, request_container._to_dict(), 'application/json', **kwargs)
            result = ContainerGroup._from_dict(result.get_result()).unstructured[0].data
        else:

            result = self.analyze_with_flow_org(flow_id, text)
            result = ContainerGroup._from_dict(result.get_result()).unstructured[0].data

        return result


    def get_annotators(self, **kwargs) -> DetailedResponse:
        """
        Get list of available annotators.

        Get list of available annotators that can be leveraged to detect information from
        unstructured data. One or more annnotators can be leveraged within a single
        request to the service.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_annotators')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/annotators'
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def get_annotators_by_id(self, id: str, **kwargs) -> DetailedResponse:
        """
        Get details of a specific annotator.

        Get details of an annotator that can be used to detect information from
        unstructured data.

        :param str id: The ID the Service API was registered under.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if id is None:
            raise ValueError('id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_annotators_by_id')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/annotators/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def delete_user_specific_artifacts(self, **kwargs) -> DetailedResponse:
        """
        Delete tenant specific artifacts.

        Delete tenant specific artifacts.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='delete_user_specific_artifacts')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/user_data'
        request = self.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response

    #########################
    # Cartridges
    #########################


    def cartridges_get(self, **kwargs) -> DetailedResponse:
        """
        Get list of available deployment status.

        Returns a summary including ID and status of the available deployments.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ListStringWrapper` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='cartridges_get')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/cartridges'
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def cartridges_post_multipart(self, *, archive_file: BinaryIO = None, archive_file_content_type: str = None, **kwargs) -> DetailedResponse:
        """
        Create a cartridge deployment.

        Create a cartridge deployment from a cartridge archive file.

        :param BinaryIO archive_file: (optional) Cartridge archive file.
        :param str archive_file_content_type: (optional) The content type of
               archive_file.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `DeployCartridgeResponse` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='cartridges_post_multipart')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        form_data = []
        if archive_file:
            form_data.append(('archive_file', (None, archive_file, archive_file_content_type or 'application/octet-stream')))

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/cartridges'
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       files=form_data)

        response = self.request_acd(request)
        return response


    def cartridges_put_multipart(self, *, archive_file: BinaryIO = None, archive_file_content_type: str = None, **kwargs) -> DetailedResponse:
        """
        Create a cartridge deployment.

        Update a cartridge deployment from a cartridge archive file.

        :param BinaryIO archive_file: (optional) Cartridge archive file.
        :param str archive_file_content_type: (optional) The content type of
               archive_file.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `DeployCartridgeResponse` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='cartridges_put_multipart')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        form_data = []
        if archive_file:
            form_data.append(('archive_file', (None, archive_file, archive_file_content_type or 'application/octet-stream')))

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/cartridges'
        request = self.prepare_request(method='PUT',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       files=form_data)

        response = self.request_acd(request)
        return response


    def cartridges_get_id(self, id: str, **kwargs) -> DetailedResponse:
        """
        Get details of a specific deployment.

        Using the specified Catridge ID, retrieves the deployment status.

        :param str id: Cartridge ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `AcdCartridges` object
        """

        if id is None:
            raise ValueError('id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='cartridges_get_id')
        headers.update(sdk_headers)

        params = {
            'version': self.version
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/cartridges/{0}'.format(*self.encode_path_vars(id))
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


    def deploy_cartridge(self, *, archive_file: BinaryIO = None, archive_file_content_type: str = None, update: bool = None, **kwargs) -> DetailedResponse:
        """
        Deploy a cartridge.

        Deploy a cartridge from a cartridge archive file.

        :param BinaryIO archive_file: (optional) Cartridge archive file.
        :param str archive_file_content_type: (optional) The content type of
               archive_file.
        :param bool update: (optional) Update resources if they already exist.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `DeployCartridgeResponse` object
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='deploy_cartridge')
        headers.update(sdk_headers)

        params = {
            'version': self.version,
            'update': update
        }

        form_data = []
        if archive_file:
            form_data.append(('archive_file', (None, archive_file, archive_file_content_type or 'application/octet-stream')))

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/deploy'
        request = self.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       files=form_data)

        response = self.request_acd(request)
        return response

    #########################
    # status
    #########################


    def get_health_check_status(self, *, accept: str = None, format: str = None, **kwargs) -> DetailedResponse:
        """
        Determine if service is running correctly.

        This resource differs from /status in that it will will always return a 500 error
        if the service state is not OK.  This makes it simpler for service front ends
        (such as Datapower) to detect a failed service.

        :param str accept: (optional) The type of the response: application/json or
               application/xml.
        :param str format: (optional) Override response format.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `dict` result representing a `ServiceStatus` object
        """

        headers = {
            'Accept': accept
        }
        sdk_headers = get_sdk_headers(service_name=self.DEFAULT_SERVICE_NAME, service_version='V1', operation_id='get_health_check_status')
        headers.update(sdk_headers)

        params = {
            'format': format
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v1/status/health_check'
        request = self.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.request_acd(request)
        return response


class RunPipelineWithFlowEnums:
    """
    Enums for run_pipeline_with_flow parameters.
    """

    class ContentType(Enum):
        """
        The type of the input. A character encoding can be specified by including a
        `charset` parameter. For example, 'text/plain;charset=utf-8'.
        """
        APPLICATION_JSON = 'application/json'
        TEXT_PLAIN = 'text/plain'


class GetServiceStatusEnums:
    """
    Enums for get_service_status parameters.
    """

    class Accept(Enum):
        """
        The type of the response: application/json or application/xml.
        """
        APPLICATION_JSON = 'application/json'
        APPLICATION_XML = 'application/xml'
    class Format(Enum):
        """
        Override response format.
        """
        JSON = 'json'
        XML = 'xml'
    class LivenessCheck(Enum):
        """
        Perform a shallow liveness check.
        """
        TRUE = 'true'
        FALSE = 'false'


class GetHealthCheckStatusEnums:
    """
    Enums for get_health_check_status parameters.
    """

    class Accept(Enum):
        """
        The type of the response: application/json or application/xml.
        """
        APPLICATION_JSON = 'application/json'
        APPLICATION_XML = 'application/xml'
    class Format(Enum):
        """
        Override response format.
        """
        JSON = 'json'
        XML = 'xml'


##############################################################################
# Models
##############################################################################


class AcdCartridges():
    """
    AcdCartridges.

    :attr str id: (optional)
    :attr str name: (optional)
    :attr str status: (optional)
    :attr int status_code: (optional)
    :attr str status_location: (optional)
    :attr str start_time: (optional)
    :attr str end_time: (optional)
    :attr str duration: (optional)
    :attr str correlation_id: (optional)
    :attr int artifact_response_code: (optional)
    :attr List[ServiceError] artifact_response: (optional)
    """

    def __init__(self, *, id: str = None, name: str = None, status: str = None, status_code: int = None, status_location: str = None, start_time: str = None, end_time: str = None, duration: str = None, correlation_id: str = None, artifact_response_code: int = None, artifact_response: List['ServiceError'] = None) -> None:
        """
        Initialize a AcdCartridges object.

        :param str id: (optional)
        :param str name: (optional)
        :param str status: (optional)
        :param int status_code: (optional)
        :param str status_location: (optional)
        :param str start_time: (optional)
        :param str end_time: (optional)
        :param str duration: (optional)
        :param str correlation_id: (optional)
        :param int artifact_response_code: (optional)
        :param List[ServiceError] artifact_response: (optional)
        """
        self.id = id
        self.name = name
        self.status = status
        self.status_code = status_code
        self.status_location = status_location
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.correlation_id = correlation_id
        self.artifact_response_code = artifact_response_code
        self.artifact_response = artifact_response

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AcdCartridges':
        """Initialize a AcdCartridges object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'status' in _dict:
            args['status'] = _dict.get('status')
        if 'statusCode' in _dict:
            args['status_code'] = _dict.get('statusCode')
        if 'statusLocation' in _dict:
            args['status_location'] = _dict.get('statusLocation')
        if 'startTime' in _dict:
            args['start_time'] = _dict.get('startTime')
        if 'endTime' in _dict:
            args['end_time'] = _dict.get('endTime')
        if 'duration' in _dict:
            args['duration'] = _dict.get('duration')
        if 'correlationId' in _dict:
            args['correlation_id'] = _dict.get('correlationId')
        if 'artifactResponseCode' in _dict:
            args['artifact_response_code'] = _dict.get('artifactResponseCode')
        if 'artifactResponse' in _dict:
            args['artifact_response'] = [ServiceError.from_dict(x) for x in _dict.get('artifactResponse')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AcdCartridges object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status
        if hasattr(self, 'status_code') and self.status_code is not None:
            _dict['statusCode'] = self.status_code
        if hasattr(self, 'status_location') and self.status_location is not None:
            _dict['statusLocation'] = self.status_location
        if hasattr(self, 'start_time') and self.start_time is not None:
            _dict['startTime'] = self.start_time
        if hasattr(self, 'end_time') and self.end_time is not None:
            _dict['endTime'] = self.end_time
        if hasattr(self, 'duration') and self.duration is not None:
            _dict['duration'] = self.duration
        if hasattr(self, 'correlation_id') and self.correlation_id is not None:
            _dict['correlationId'] = self.correlation_id
        if hasattr(self, 'artifact_response_code') and self.artifact_response_code is not None:
            _dict['artifactResponseCode'] = self.artifact_response_code
        if hasattr(self, 'artifact_response') and self.artifact_response is not None:
            _dict['artifactResponse'] = [x.to_dict() for x in self.artifact_response]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AcdCartridges object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AcdCartridges') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AcdCartridges') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class AcdFlow():
    """
    AcdFlow.

    :attr str id: (optional)
    :attr str name: (optional)
    :attr str description: (optional)
    :attr str published_date: (optional)
    :attr bool publish: (optional)
    :attr str version: (optional)
    :attr str cartridge_id: (optional)
    :attr List[AnnotatorFlow] annotator_flows: (optional)
    """

    def __init__(self, *, id: str = None, name: str = None, description: str = None, published_date: str = None, publish: bool = None, version: str = None, cartridge_id: str = None, annotator_flows: List['AnnotatorFlow'] = None) -> None:
        """
        Initialize a AcdFlow object.

        :param str id: (optional)
        :param str name: (optional)
        :param str description: (optional)
        :param str published_date: (optional)
        :param bool publish: (optional)
        :param str version: (optional)
        :param str cartridge_id: (optional)
        :param List[AnnotatorFlow] annotator_flows: (optional)
        """
        self.id = id
        self.name = name
        self.description = description
        self.published_date = published_date
        self.publish = publish
        self.version = version
        self.cartridge_id = cartridge_id
        self.annotator_flows = annotator_flows

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AcdFlow':
        """Initialize a AcdFlow object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'publishedDate' in _dict:
            args['published_date'] = _dict.get('publishedDate')
        if 'publish' in _dict:
            args['publish'] = _dict.get('publish')
        if 'version' in _dict:
            args['version'] = _dict.get('version')
        if 'cartridgeId' in _dict:
            args['cartridge_id'] = _dict.get('cartridgeId')
        if 'annotatorFlows' in _dict:
            args['annotator_flows'] = [AnnotatorFlow.from_dict(x) for x in _dict.get('annotatorFlows')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AcdFlow object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'published_date') and self.published_date is not None:
            _dict['publishedDate'] = self.published_date
        if hasattr(self, 'publish') and self.publish is not None:
            _dict['publish'] = self.publish
        if hasattr(self, 'version') and self.version is not None:
            _dict['version'] = self.version
        if hasattr(self, 'cartridge_id') and self.cartridge_id is not None:
            _dict['cartridgeId'] = self.cartridge_id
        if hasattr(self, 'annotator_flows') and self.annotator_flows is not None:
            _dict['annotatorFlows'] = [x.to_dict() for x in self.annotator_flows]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AcdFlow object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AcdFlow') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AcdFlow') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class AcdProfile():
    """
    AcdProfile.

    :attr str id: (optional)
    :attr str name: (optional)
    :attr str description: (optional)
    :attr str published_date: (optional)
    :attr bool publish: (optional)
    :attr str version: (optional)
    :attr str cartridge_id: (optional)
    :attr List[Annotator] annotators: (optional)
    """

    def __init__(self, *, id: str = None, name: str = None, description: str = None, published_date: str = None, publish: bool = None, version: str = None, cartridge_id: str = None, annotators: List['Annotator'] = None) -> None:
        """
        Initialize a AcdProfile object.

        :param str id: (optional)
        :param str name: (optional)
        :param str description: (optional)
        :param str published_date: (optional)
        :param bool publish: (optional)
        :param str version: (optional)
        :param str cartridge_id: (optional)
        :param List[Annotator] annotators: (optional)
        """
        self.id = id
        self.name = name
        self.description = description
        self.published_date = published_date
        self.publish = publish
        self.version = version
        self.cartridge_id = cartridge_id
        self.annotators = annotators

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AcdProfile':
        """Initialize a AcdProfile object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'publishedDate' in _dict:
            args['published_date'] = _dict.get('publishedDate')
        if 'publish' in _dict:
            args['publish'] = _dict.get('publish')
        if 'version' in _dict:
            args['version'] = _dict.get('version')
        if 'cartridgeId' in _dict:
            args['cartridge_id'] = _dict.get('cartridgeId')
        if 'annotators' in _dict:
            args['annotators'] = [Annotator.from_dict(x) for x in _dict.get('annotators')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AcdProfile object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'published_date') and self.published_date is not None:
            _dict['publishedDate'] = self.published_date
        if hasattr(self, 'publish') and self.publish is not None:
            _dict['publish'] = self.publish
        if hasattr(self, 'version') and self.version is not None:
            _dict['version'] = self.version
        if hasattr(self, 'cartridge_id') and self.cartridge_id is not None:
            _dict['cartridgeId'] = self.cartridge_id
        if hasattr(self, 'annotators') and self.annotators is not None:
            _dict['annotators'] = [x.to_dict() for x in self.annotators]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AcdProfile object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AcdProfile') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AcdProfile') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class AllergyMedication(object):
    """
    AllergyMedication.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    :attr MedicationAnnotation medication: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, section_normalized_name=None, section_surface_form=None, medication=None,
                 **kwargs):
        """
        Initialize a AllergyMedication object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param MedicationAnnotation medication: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        self.medication = medication
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a AllergyMedication object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'medication' in _dict:
            args['medication'] = [MedicationAnnotation._from_dict(v) for v in _dict['medication']]
            del xtra['medication']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AllergyMedication object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'medication') and self.medication is not None:
            _dict['medication'] = [v._to_dict() for v in self.medication]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical',
                       'section_normalized_name', 'section_surface_form', 'medication'})
        if not hasattr(self, '_additionalProperties'):
            super(AllergyMedication, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(AllergyMedication, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this AllergyMedication object."""
        return json.dumps(self._to_dict(), indent=2)


class Annotation(object):
    """
    Annotation.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, section_normalized_name=None, section_surface_form=None, **kwargs):
        """
        Initialize a Annotation object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Annotation object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Annotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical',
                       'section_normalized_name', 'section_surface_form'})
        if not hasattr(self, '_additionalProperties'):
            super(Annotation, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Annotation, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Annotation object."""
        return json.dumps(self._to_dict(), indent=2)

class AnalyticFlowBeanInput():
    """
    AnalyticFlowBeanInput.

    :attr List[UnstructuredContainer] unstructured: (optional)
    :attr List[AnnotatorFlow] annotator_flows: (optional)
    """

    def __init__(self, *, unstructured: List['UnstructuredContainer'] = None, annotator_flows: List['AnnotatorFlow'] = None) -> None:
        """
        Initialize a AnalyticFlowBeanInput object.

        :param List[UnstructuredContainer] unstructured: (optional)
        :param List[AnnotatorFlow] annotator_flows: (optional)
        """
        self.unstructured = unstructured
        self.annotator_flows = annotator_flows

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AnalyticFlowBeanInput':
        """Initialize a AnalyticFlowBeanInput object from a json dictionary."""
        args = {}
        if 'unstructured' in _dict:
            args['unstructured'] = [UnstructuredContainer.from_dict(x) for x in _dict.get('unstructured')]
        if 'annotatorFlows' in _dict:
            args['annotator_flows'] = [AnnotatorFlow.from_dict(x) for x in _dict.get('annotatorFlows')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AnalyticFlowBeanInput object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'unstructured') and self.unstructured is not None:
            _dict['unstructured'] = [x.to_dict() for x in self.unstructured]
        if hasattr(self, 'annotator_flows') and self.annotator_flows is not None:
            _dict['annotatorFlows'] = [x.to_dict() for x in self.annotator_flows]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AnalyticFlowBeanInput object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AnalyticFlowBeanInput') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AnalyticFlowBeanInput') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Annotator():
    """
    Annotator.

    :attr str name:
    :attr dict parameters: (optional)
    :attr List[ConfigurationEntity] configurations: (optional)
    """

    def __init__(self, name: str, *, parameters: dict = None, configurations: List['ConfigurationEntity'] = None) -> None:
        """
        Initialize a Annotator object.

        :param str name:
        :param dict parameters: (optional)
        :param List[ConfigurationEntity] configurations: (optional)
        """
        self.name = name
        self.parameters = parameters
        self.configurations = configurations

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Annotator':
        """Initialize a Annotator object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in Annotator JSON')
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        if 'configurations' in _dict:
            args['configurations'] = [ConfigurationEntity.from_dict(x) for x in _dict.get('configurations')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Annotator object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        if hasattr(self, 'configurations') and self.configurations is not None:
            _dict['configurations'] = [x.to_dict() for x in self.configurations]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Annotator object."""
        return json.dumps(self.to_dict(), indent=2, cls=AnnotatorEncoder)

    def __eq__(self, other: 'Annotator') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Annotator') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class AnnotatorEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

class AnnotatorFlow():
    """
    AnnotatorFlow.

    :attr str profile: (optional)
    :attr Flow flow:
    :attr str id: (optional)
    :attr str type: (optional)
    :attr dict data: (optional)
    :attr dict metadata: (optional)
    :attr List[ConfigurationEntity] global_configurations: (optional)
    :attr int uid: (optional)
    """

    def __init__(self, flow: 'Flow', *, profile: str = None, id: str = None, type: str = None, data: dict = None, metadata: dict = None, global_configurations: List['ConfigurationEntity'] = None, uid: int = None) -> None:
        """
        Initialize a AnnotatorFlow object.

        :param Flow flow:
        :param str profile: (optional)
        :param str id: (optional)
        :param str type: (optional)
        :param dict data: (optional)
        :param dict metadata: (optional)
        :param List[ConfigurationEntity] global_configurations: (optional)
        :param int uid: (optional)
        """
        self.profile = profile
        self.flow = flow
        self.id = id
        self.type = type
        self.data = data
        self.metadata = metadata
        self.global_configurations = global_configurations
        self.uid = uid

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AnnotatorFlow':
        """Initialize a AnnotatorFlow object from a json dictionary."""
        args = {}
        if 'profile' in _dict:
            args['profile'] = _dict.get('profile')
        if 'flow' in _dict:
            args['flow'] = Flow.from_dict(_dict.get('flow'))
        else:
            raise ValueError('Required property \'flow\' not present in AnnotatorFlow JSON')
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'data' in _dict:
            args['data'] = _dict.get('data')
        if 'metadata' in _dict:
            args['metadata'] = _dict.get('metadata')
        if 'globalConfigurations' in _dict:
            args['global_configurations'] = [ConfigurationEntity.from_dict(x) for x in _dict.get('globalConfigurations')]
        if 'uid' in _dict:
            args['uid'] = _dict.get('uid')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AnnotatorFlow object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'profile') and self.profile is not None:
            _dict['profile'] = self.profile
        if hasattr(self, 'flow') and self.flow is not None:
            _dict['flow'] = self.flow.to_dict()
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'data') and self.data is not None:
            _dict['data'] = self.data
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata
        if hasattr(self, 'global_configurations') and self.global_configurations is not None:
            _dict['globalConfigurations'] = [x.to_dict() for x in self.global_configurations]
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AnnotatorFlow object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AnnotatorFlow') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AnnotatorFlow') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Name(object):
    # allergy.
    ALLERGY = "allergy"
    # attribute_detection.
    ATTRIBUTE_DETECTION = "attribute_detection"
    # bathing_assistance.
    BATHING_ASSISTANCE = "bathing_assistance"
    # cancer.
    CANCER = "cancer"
    # concept_detection.
    CONCEPT_DETECTION = "concept_detection"
    # concept_value.
    CONCEPT_VALUE = "concept_value"
    # disambiguation.
    DISAMBIGUATION = "disambiguation"
    # dressing_assistance.
    DRESSING_ASSISTANCE = "dressing_assistance"
    # eating_assistance.
    EATING_ASSISTANCE = "eating_assistance"
    # ejection_fraction.
    EJECTION_FRACTION = "ejection_fraction"
    # hypothetical.
    HYPOTHETICAL = "hypothetical"
    # lab_value.
    LAB_VALUE = "lab_value"
    # medication.
    MEDICATION = "medication"
    # named_entities.
    NAMED_ENTITIES = "named_entities"
    # negation.
    NEGATION = "negation"
    # procedure.
    PROCEDURE = "procedure"
    # relation.
    RELATION = "relation"
    # seeing_assistance.
    SEEING_ASSISTANCE = "seeing_assistance"
    # smoking.
    SMOKING = "smoking"
    # spell checker
    SPELL_CHECKER = "spell_checker"
    # symptom_disease.
    SYMPTOM_DISEASE = "symptom_disease"
    # toileting_assistance.
    TOILETING_ASSISTANCE = "toileting_assistance"
    # walking_assistance.
    WALKING_ASSISTANCE = "walking_assistance"
    # section.
    SECTION = "section"
    # nlu.
    NLU = "nlu"
    #model_broker
    MODEL_BROKER = "model_broker"


class AssistanceAnnotation(object):
    """
    AssistanceAnnotation.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str primary_action_normalized_name: (optional)
    :attr str modality: (optional)
    :attr str primary_action_surface_form: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, primary_action_normalized_name=None, modality=None,
                 primary_action_surface_form=None, section_normalized_name=None, section_surface_form=None,
                 **kwargs):
        """
        Initialize a AssistanceAnnotation object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str primary_action_normalized_name: (optional)
        :param str modality: (optional)
        :param str primary_action_surface_form: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.primary_action_normalized_name = primary_action_normalized_name
        self.modality = modality
        self.primary_action_surface_form = primary_action_surface_form
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a AssistanceAnnotation object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'primaryActionNormalizedName' in _dict:
            args['primary_action_normalized_name'] = _dict['primaryActionNormalizedName']
            del xtra['primaryActionNormalizedName']
        if 'modality' in _dict:
            args['modality'] = _dict['modality']
            del xtra['modality']
        if 'primaryActionSurfaceForm' in _dict:
            args['primary_action_surface_form'] = _dict['primaryActionSurfaceForm']
            del xtra['primaryActionSurfaceForm']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AssistanceAnnotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'primary_action_normalized_name') and self.primary_action_normalized_name is not None:
            _dict['primaryActionNormalizedName'] = self.primary_action_normalized_name
        if hasattr(self, 'modality') and self.modality is not None:
            _dict['modality'] = self.modality
        if hasattr(self, 'primary_action_surface_form') and self.primary_action_surface_form is not None:
            _dict['primaryActionSurfaceForm'] = self.primary_action_surface_form
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical',
                       'primary_action_normalized_name', 'modality', 'primary_action_surface_form',
                       'section_normalized_name', 'section_surface_form'})
        if not hasattr(self, '_additionalProperties'):
            super(AssistanceAnnotation, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(AssistanceAnnotation, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this AssistanceAnnotation object."""
        return json.dumps(self._to_dict(), indent=2)

class AttributeValueEntry(object):
    """
    AttributeValueEntry.
    :attr str value: (optional)
    :attr str unit: (optional)
    :attr str frequency: (optional)
    :attr str duration: (optional)
    :attr str dimension: (optional)
    """

    def __init__(self, value=None, unit=None, frequency=None, duration=None, dimension=None, **kwargs):
        """
        Initialize a AttributeValueEntry object.
        :param str value: (optional)
        :param str unit: (optional)
        :param str frequency: (optional)
        :param str duration: (optional)
        :param str dimension: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.value = value
        self.unit = unit
        self.frequency = frequency
        self.duration = duration
        self.dimension = dimension
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    def __getitem__(self, key):
        """This class was originally exposed to users as a dict, so to preserve backwards compatibility,
            we'll make this class function as a dict as well as a class.
        """
        return self.__dict__[key]

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a AttributeValueEntry object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'value' in _dict:
            args['value'] = _dict['value']
            del xtra['value']
        if 'unit' in _dict:
            args['unit'] = _dict['unit']
            del xtra['unit']
        if 'frequency' in _dict:
            args['frequency'] = _dict['frequency']
            del xtra['frequency']
        if 'duration' in _dict:
            args['duration'] = _dict['duration']
            del xtra['duration']
        if 'dimension' in _dict:
            args['dimension'] = _dict['dimension']
            del xtra['dimension']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AttributeValueEntry object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'unit') and self.unit is not None:
            _dict['unit'] = self.unit
        if hasattr(self, 'frequency') and self.frequency is not None:
            _dict['frequency'] = self.frequency
        if hasattr(self, 'duration') and self.duration is not None:
            _dict['duration'] = self.duration
        if hasattr(self, 'dimension') and self.dimension is not None:
            _dict['dimension'] = self.dimension
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'value', 'unit', 'frequency', 'duration', 'dimension'}
        if not hasattr(self, '_additionalProperties'):
            super(AttributeValueEntry, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(AttributeValueEntry, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this AttributeValueEntry object."""
        return json.dumps(self._to_dict(), indent=2)

class AttributeValueAnnotation(object):
    """
    AttributeValueAnnotation.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str preferred_name: (optional)
    :attr list[object] values: (optional)
    :attr str source: (optional)
    :attr str source_version: (optional)
    :attr Concept concept: (optional)
    :attr str name: (optional)
    :attr str icd9_code: (optional)
    :attr str icd10_code: (optional)
    :attr str nci_code: (optional)
    :attr str snomed_concept_id: (optional)
    :attr str mesh_id: (optional)
    :attr str rx_norm_id: (optional)
    :attr str loinc_id: (optional)
    :attr str vocabs: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    :attr str cpt_code: (optional)
    :attr Disambiguation disambiguation_data: (optional)
    :attr InsightModelData insight_model_data: (optional)
    :attr str ccs_code: (optional)
    :attr str hcc_code: (optional)
    :attr str rule_id: (optional)
    :attr list[Concept] derived_from: (optional)
    :attr list[Temporal] temporal: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, preferred_name=None, values=None, source=None, source_version=None,
                 concept=None, name=None, icd9_code=None, icd10_code=None, nci_code=None, snomed_concept_id=None,
                 mesh_id=None, rx_norm_id=None, loinc_id=None, vocabs=None, section_normalized_name=None,
                 section_surface_form=None, cpt_code=None, disambiguation_data=None, insight_model_data=None,
                 ccs_code=None, hcc_code=None, rule_id=None, derived_from=None, temporal=None, **kwargs):
        """
        Initialize a AttributeValueAnnotation object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str preferred_name: (optional)
        :param list[object] values: (optional)
        :param str source: (optional)
        :param str source_version: (optional)
        :param Concept concept: (optional)
        :param str name: (optional)
        :param str icd9_code: (optional)
        :param str icd10_code: (optional)
        :param str nci_code: (optional)
        :param str snomed_concept_id: (optional)
        :param str mesh_id: (optional)
        :param str rx_norm_id: (optional)
        :param str loinc_id: (optional)
        :param str vocabs: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param str cpt_code: (optional)
        :param Disambiguation disambiguation_data: (optional)
        :param InsightModelData insight_model_data: (optional)
        :param str ccs_code: (optional)
        :param str hcc_code: (optional)
        :param str rule_id: (optional)
        :param list[Concept] derived_from: (optional)
        :param list[Temporal] temporal: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.preferred_name = preferred_name
        self.values = values
        self.source = source
        self.source_version = source_version
        self.concept = concept
        self.name = name
        self.icd9_code = icd9_code
        self.icd10_code = icd10_code
        self.nci_code = nci_code
        self.snomed_concept_id = snomed_concept_id
        self.mesh_id = mesh_id
        self.rx_norm_id = rx_norm_id
        self.loinc_id = loinc_id
        self.vocabs = vocabs
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        self.cpt_code = cpt_code
        self.disambiguation_data = disambiguation_data
        self.insight_model_data = insight_model_data
        self.ccs_code = ccs_code
        self.hcc_code = hcc_code
        self.rule_id = rule_id
        self.derived_from = derived_from
        self.temporal = temporal
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a AttributeValueAnnotation object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict['preferredName']
            del xtra['preferredName']
        if 'values' in _dict:
            args['values'] = [AttributeValueEntry._from_dict(entry) for entry in _dict['values']]
            del xtra['values']
        if 'source' in _dict:
            args['source'] = _dict['source']
            del xtra['source']
        if 'sourceVersion' in _dict:
            args['source_version'] = _dict['sourceVersion']
            del xtra['sourceVersion']
        if 'concept' in _dict:
            args['concept'] = Concept._from_dict(_dict['concept'])
            del xtra['concept']
        if 'name' in _dict:
            args['name'] = _dict['name']
            del xtra['name']
        if 'icd9Code' in _dict:
            args['icd9_code'] = _dict['icd9Code']
            del xtra['icd9Code']
        if 'icd10Code' in _dict:
            args['icd10_code'] = _dict['icd10Code']
            del xtra['icd10Code']
        if 'nciCode' in _dict:
            args['nci_code'] = _dict['nciCode']
            del xtra['nciCode']
        if 'snomedConceptId' in _dict:
            args['snomed_concept_id'] = _dict['snomedConceptId']
            del xtra['snomedConceptId']
        if 'meshId' in _dict:
            args['mesh_id'] = _dict['meshId']
            del xtra['meshId']
        if 'rxNormId' in _dict:
            args['rx_norm_id'] = _dict['rxNormId']
            del xtra['rxNormId']
        # Normalize alternative capitalization (rxNormID)
        if 'rxNormID' in _dict:
            args['rx_norm_id'] = _dict['rxNormID']
            del xtra['rxNormID']
        if 'loincId' in _dict:
            args['loinc_id'] = _dict['loincId']
            del xtra['loincId']
        if 'vocabs' in _dict:
            args['vocabs'] = _dict['vocabs']
            del xtra['vocabs']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'cptCode' in _dict:
            args['cpt_code'] = _dict['cptCode']
            del xtra['cptCode']
        if 'disambiguationData' in _dict:
            args['disambiguation_data'] = Disambiguation._from_dict(_dict['disambiguationData'])
            del xtra['disambiguationData']
        if 'insightModelData' in _dict:
            args['insight_model_data'] = InsightModelData._from_dict(_dict['insightModelData'])
            del xtra['insightModelData']
        if 'ccsCode' in _dict:
            args['ccs_code'] = _dict['ccsCode']
            del xtra['ccsCode']
        if 'hccCode' in _dict:
            args['hcc_code'] = _dict['hccCode']
            del xtra['hccCode']
        if 'ruleId' in _dict:
            args['rule_id'] = _dict['ruleId']
            del xtra['ruleId']
        if 'derivedFrom' in _dict:
            args['derived_from'] = [Concept._from_dict(entry) for entry in _dict['derivedFrom']]
            del xtra['derivedFrom']
        if 'temporal' in _dict:
            args['temporal'] = [Temporal._from_dict(entry) for entry in _dict['temporal']]
            del xtra['temporal']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AttributeValueAnnotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = [entry._to_dict() for entry in self.values]
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'source_version') and self.source_version is not None:
            _dict['sourceVersion'] = self.source_version
        if hasattr(self, 'concept') and self.concept is not None:
            _dict['concept'] = self.concept._to_dict()
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'icd9_code') and self.icd9_code is not None:
            _dict['icd9Code'] = self.icd9_code
        if hasattr(self, 'icd10_code') and self.icd10_code is not None:
            _dict['icd10Code'] = self.icd10_code
        if hasattr(self, 'nci_code') and self.nci_code is not None:
            _dict['nciCode'] = self.nci_code
        if hasattr(self, 'snomed_concept_id') and self.snomed_concept_id is not None:
            _dict['snomedConceptId'] = self.snomed_concept_id
        if hasattr(self, 'mesh_id') and self.mesh_id is not None:
            _dict['meshId'] = self.mesh_id
        if hasattr(self, 'rx_norm_id') and self.rx_norm_id is not None:
            _dict['rxNormId'] = self.rx_norm_id
        if hasattr(self, 'loinc_id') and self.loinc_id is not None:
            _dict['loincId'] = self.loinc_id
        if hasattr(self, 'vocabs') and self.vocabs is not None:
            _dict['vocabs'] = self.vocabs
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'cpt_code') and self.cpt_code is not None:
            _dict['cptCode'] = self.cpt_code
        if hasattr(self, 'disambiguation_data') and self.disambiguation_data is not None:
            _dict['disambiguationData'] = self.disambiguation_data._to_dict()
        if hasattr(self, 'insight_model_data') and self.insight_model_data is not None:
            _dict['insightModelData'] = self.insight_model_data._to_dict()
        if hasattr(self, 'ccs_code') and self.ccs_code is not None:
            _dict['ccsCode'] = self.ccs_code
        if hasattr(self, 'hcc_code') and self.hcc_code is not None:
            _dict['hccCode'] = self.hcc_code
        if hasattr(self, 'rule_id') and self.rule_id is not None:
            _dict['ruleId'] = self.rule_id
        if hasattr(self, 'derived_from') and self.derived_from is not None:
            _dict['derivedFrom'] = [entry._to_dict() for entry in self.derived_from]
        if hasattr(self, 'temporal') and self.temporal is not None:
            _dict['temporal'] = [entry._to_dict() for entry in self.temporal]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'preferred_name',
                       'values', 'source', 'source_version', 'concept', 'name', 'icd9_code', 'icd10_code', 'nci_code',
                       'snomed_concept_id', 'mesh_id', 'rx_norm_id', 'loinc_id', 'vocabs', 'section_normalized_name',
                       'section_surface_form', 'cpt_code', 'disambiguation_data', 'insight_model_data', 'ccs_code',
                       'hcc_code', 'rule_id', 'derived_from', 'temporal'})
        if not hasattr(self, '_additionalProperties'):
            super(AttributeValueAnnotation, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(AttributeValueAnnotation, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this AttributeValueAnnotation object."""
        return json.dumps(self._to_dict(), indent=2)


class CancerDiagnosis(object):
    """
    CancerDiagnosis.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr int cui: (optional)
    :attr str section_normalized_name: (optional)
    :attr str modality: (optional)
    :attr str section_surface_form: (optional)
    :attr Disambiguation disambiguation_data: (optional)
    :attr list[object] cancer: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, cui=None, section_normalized_name=None, modality=None,
                 section_surface_form=None, disambiguation_data=None, cancer=None, **kwargs):
        """
        Initialize a CancerDiagnosis object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param int cui: (optional)
        :param str section_normalized_name: (optional)
        :param str modality: (optional)
        :param str section_surface_form: (optional)
        :param Disambiguation disambiguation_data: (optional)
        :param list[object] cancer: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.cui = cui
        self.section_normalized_name = section_normalized_name
        self.modality = modality
        self.section_surface_form = section_surface_form
        self.disambiguation_data = disambiguation_data
        self.cancer = cancer
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a CancerDiagnosis object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'cui' in _dict:
            args['cui'] = _dict['cui']
            del xtra['cui']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'modality' in _dict:
            args['modality'] = _dict['modality']
            del xtra['modality']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'disambiguationData' in _dict:
            args['disambiguation_data'] = Disambiguation._from_dict(_dict['disambiguationData'])
            del xtra['disambiguationData']
        if 'cancer' in _dict:
            args['cancer'] = _dict['cancer']
            del xtra['cancer']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CancerDiagnosis object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'modality') and self.modality is not None:
            _dict['modality'] = self.modality
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'disambiguation_data') and self.disambiguation_data is not None:
            _dict['disambiguationData'] = self.disambiguation_data._to_dict()
        if hasattr(self, 'cancer') and self.cancer is not None:
            _dict['cancer'] = self.cancer
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'cui',
                       'section_normalized_name', 'modality', 'section_surface_form', 'disambiguation_data', 'cancer'})
        if not hasattr(self, '_additionalProperties'):
            super(CancerDiagnosis, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(CancerDiagnosis, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this CancerDiagnosis object."""
        return json.dumps(self._to_dict(), indent=2)


class Concept(object):
    """
    Concept.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr int cui: (optional)
    :attr str preferred_name: (optional)
    :attr str semantic_type: (optional)
    :attr str source: (optional)
    :attr str source_version: (optional)
    :attr Disambiguation disambiguation_data: (optional)
    :attr str icd9_code: (optional)
    :attr str icd10_code: (optional)
    :attr str nci_code: (optional)
    :attr str snomed_concept_id: (optional)
    :attr str mesh_id: (optional)
    :attr str rx_norm_id: (optional)
    :attr str loinc_id: (optional)
    :attr str vocabs: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    :attr str cpt_code: (optional)
    :attr InsightModelData insight_model_data: (optional)
    :attr str rule_id: (optional)
    :attr list[Concept] derived_from: (optional)
    :attr list[Temporal] temporal: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, cui=None, preferred_name=None, semantic_type=None, source=None,
                 source_version=None, disambiguation_data=None, icd9_code=None, icd10_code=None, nci_code=None,
                 snomed_concept_id=None, mesh_id=None, rx_norm_id=None, loinc_id=None, vocabs=None,
                 section_normalized_name=None, section_surface_form=None, cpt_code=None, insight_model_data=None,
                 rule_id=None, derived_from=None, temporal=None, **kwargs):
        """
        Initialize a Concept object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param int cui: (optional)
        :param str preferred_name: (optional)
        :param str semantic_type: (optional)
        :param str source: (optional)
        :param str source_version: (optional)
        :param Disambiguation disambiguation_data: (optional)
        :param str icd9_code: (optional)
        :param str icd10_code: (optional)
        :param str nci_code: (optional)
        :param str snomed_concept_id: (optional)
        :param str mesh_id: (optional)
        :param str rx_norm_id: (optional)
        :param str loinc_id: (optional)
        :param str vocabs: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param str cpt_code: (optional)
        :param InsightModelData insight_model_data: (optional)
        :param str rule_id: (optional)
        :param list[Concept] derived_from: (optional)
        :param list[Temporal] temporal: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.cui = cui
        self.preferred_name = preferred_name
        self.semantic_type = semantic_type
        self.source = source
        self.source_version = source_version
        self.disambiguation_data = disambiguation_data
        self.icd9_code = icd9_code
        self.icd10_code = icd10_code
        self.nci_code = nci_code
        self.snomed_concept_id = snomed_concept_id
        self.mesh_id = mesh_id
        self.rx_norm_id = rx_norm_id
        self.loinc_id = loinc_id
        self.vocabs = vocabs
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        self.cpt_code = cpt_code
        self.insight_model_data = insight_model_data
        self.rule_id = rule_id
        self.derived_from = derived_from
        self.temporal = temporal
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Concept object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'cui' in _dict:
            args['cui'] = _dict['cui']
            del xtra['cui']
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict['preferredName']
            del xtra['preferredName']
        if 'semanticType' in _dict:
            args['semantic_type'] = _dict['semanticType']
            del xtra['semanticType']
        if 'source' in _dict:
            args['source'] = _dict['source']
            del xtra['source']
        if 'sourceVersion' in _dict:
            args['source_version'] = _dict['sourceVersion']
            del xtra['sourceVersion']
        if 'disambiguationData' in _dict:
            args['disambiguation_data'] = Disambiguation._from_dict(_dict['disambiguationData'])
            del xtra['disambiguationData']
        if 'icd9Code' in _dict:
            args['icd9_code'] = _dict['icd9Code']
            del xtra['icd9Code']
        if 'icd10Code' in _dict:
            args['icd10_code'] = _dict['icd10Code']
            del xtra['icd10Code']
        if 'nciCode' in _dict:
            args['nci_code'] = _dict['nciCode']
            del xtra['nciCode']
        if 'snomedConceptId' in _dict:
            args['snomed_concept_id'] = _dict['snomedConceptId']
            del xtra['snomedConceptId']
        if 'meshId' in _dict:
            args['mesh_id'] = _dict['meshId']
            del xtra['meshId']
        if 'rxNormId' in _dict:
            args['rx_norm_id'] = _dict['rxNormId']
            del xtra['rxNormId']
        # Normalize alternative capitalization (rxNormID)
        if 'rxNormID' in _dict:
            args['rx_norm_id'] = _dict['rxNormID']
            del xtra['rxNormID']
        if 'loincId' in _dict:
            args['loinc_id'] = _dict['loincId']
            del xtra['loincId']
        if 'vocabs' in _dict:
            args['vocabs'] = _dict['vocabs']
            del xtra['vocabs']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'cptCode' in _dict:
            args['cpt_code'] = _dict['cptCode']
            del xtra['cptCode']
        if 'insightModelData' in _dict:
            args['insight_model_data'] = InsightModelData._from_dict(_dict['insightModelData'])
            del xtra['insightModelData']
        if 'ruleId' in _dict:
            args['rule_id'] = _dict['ruleId']
            del xtra['ruleId']
        if 'derivedFrom' in _dict:
            args['derived_from'] = [Concept._from_dict(entry) for entry in _dict['derivedFrom']]
            del xtra['derivedFrom']
        if 'temporal' in _dict:
            args['temporal'] = [Temporal._from_dict(entry) for entry in _dict['temporal']]
            del xtra['temporal']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Concept object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'semantic_type') and self.semantic_type is not None:
            _dict['semanticType'] = self.semantic_type
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'source_version') and self.source_version is not None:
            _dict['sourceVersion'] = self.source_version
        if hasattr(self, 'disambiguation_data') and self.disambiguation_data is not None:
            _dict['disambiguationData'] = self.disambiguation_data._to_dict()
        if hasattr(self, 'icd9_code') and self.icd9_code is not None:
            _dict['icd9Code'] = self.icd9_code
        if hasattr(self, 'icd10_code') and self.icd10_code is not None:
            _dict['icd10Code'] = self.icd10_code
        if hasattr(self, 'nci_code') and self.nci_code is not None:
            _dict['nciCode'] = self.nci_code
        if hasattr(self, 'snomed_concept_id') and self.snomed_concept_id is not None:
            _dict['snomedConceptId'] = self.snomed_concept_id
        if hasattr(self, 'mesh_id') and self.mesh_id is not None:
            _dict['meshId'] = self.mesh_id
        if hasattr(self, 'rx_norm_id') and self.rx_norm_id is not None:
            _dict['rxNormId'] = self.rx_norm_id
        if hasattr(self, 'loinc_id') and self.loinc_id is not None:
            _dict['loincId'] = self.loinc_id
        if hasattr(self, 'vocabs') and self.vocabs is not None:
            _dict['vocabs'] = self.vocabs
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'cpt_code') and self.cpt_code is not None:
            _dict['cptCode'] = self.cpt_code
        if hasattr(self, 'insight_model_data') and self.insight_model_data is not None:
            _dict['insightModelData'] = self.insight_model_data._to_dict()
        if hasattr(self, 'rule_id') and self.rule_id is not None:
            _dict['ruleId'] = self.rule_id
        if hasattr(self, 'derived_from') and self.derived_from is not None:
            _dict['derivedFrom'] = [entry._to_dict() for entry in self.derived_from]
        if hasattr(self, 'temporal') and self.temporal is not None:
            _dict['temporal'] = [entry._to_dict() for entry in self.temporal]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'cui',
                       'preferred_name', 'semantic_type', 'source', 'source_version', 'disambiguation_data',
                       'icd9_code', 'icd10_code', 'nci_code', 'snomed_concept_id', 'mesh_id', 'rx_norm_id',
                       'loinc_id', 'vocabs', 'section_normalized_name', 'section_surface_form', 'cpt_code',
                       'insight_model_data', 'rule_id', 'derived_from', 'temporal'})
        if not hasattr(self, '_additionalProperties'):
            super(Concept, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Concept, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Concept object."""
        return json.dumps(self._to_dict(), indent=2)


class ConceptValue(object):
    """
    ConceptValue.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str cui: (optional)
    :attr str dimension: (optional)
    :attr str preferred_name: (optional)
    :attr str trigger: (optional)
    :attr str source: (optional)
    :attr str value: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    :attr str rule_id: (optional)
    :attr list[Concept] derived_from: (optional)
    :attr str unit: (optional)
    :attr list[object] values: (optional)
    :attr str range_begin: (optional)
    :attr str range_end: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, cui=None, dimension=None, preferred_name=None, trigger=None, source=None,
                 value=None, section_normalized_name=None, section_surface_form=None, rule_id=None,
                 derived_from=None, unit=None, values=None, range_begin=None, range_end=None, **kwargs):
        """
        Initialize a ConceptValue object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str cui: (optional)
        :param str dimension: (optional)
        :param str preferred_name: (optional)
        :param str trigger: (optional)
        :param str source: (optional)
        :param str value: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param str rule_id: (optional)
        :param list[Concept] derived_from: (optional)
        :param str unit: (optional)
        :param list[object] values: (optional)
        :param str range_begin: (optional)
        :param str range_end: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.cui = cui
        self.dimension = dimension
        self.preferred_name = preferred_name
        self.trigger = trigger
        self.source = source
        self.value = value
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        self.rule_id = rule_id
        self.derived_from = derived_from
        self.unit = unit
        self.values = values
        self.range_begin = range_begin
        self.range_end = range_end
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a ConceptValue object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'cui' in _dict:
            args['cui'] = _dict['cui']
            del xtra['cui']
        if 'dimension' in _dict:
            args['dimension'] = _dict['dimension']
            del xtra['dimension']
        if 'preferredName' in _dict:
            args['preferred_name'] = _dict['preferredName']
            del xtra['preferredName']
        if 'trigger' in _dict:
            args['trigger'] = _dict['trigger']
            del xtra['trigger']
        if 'source' in _dict:
            args['source'] = _dict['source']
            del xtra['source']
        if 'value' in _dict:
            args['value'] = _dict['value']
            del xtra['value']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'ruleId' in _dict:
            args['rule_id'] = _dict['ruleId']
            del xtra['ruleId']
        if 'derivedFrom' in _dict:
            args['derived_from'] = [Concept._from_dict(entry) for entry in _dict['derivedFrom']]
            del xtra['derivedFrom']
        if 'unit' in _dict:
            args['unit'] = _dict['unit']
            del xtra['unit']
        if 'values' in _dict:
            args['values'] = _dict['values']
            del xtra['values']
        if 'rangeBegin' in _dict:
            args['range_begin'] = _dict['rangeBegin']
            del xtra['rangeBegin']
        if 'rangeEnd' in _dict:
            args['range_end'] = _dict['rangeEnd']
            del xtra['rangeEnd']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ConceptValue object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'dimension') and self.dimension is not None:
            _dict['dimension'] = self.dimension
        if hasattr(self, 'preferred_name') and self.preferred_name is not None:
            _dict['preferredName'] = self.preferred_name
        if hasattr(self, 'trigger') and self.trigger is not None:
            _dict['trigger'] = self.trigger
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'rule_id') and self.rule_id is not None:
            _dict['ruleId'] = self.rule_id
        if hasattr(self, 'derived_from') and self.derived_from is not None:
            _dict['derivedFrom'] = [entry._to_dict() for entry in self.derived_from]
        if hasattr(self, 'unit') and self.unit is not None:
            _dict['unit'] = self.unit
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values
        if hasattr(self, 'range_begin') and self.range_begin is not None:
            _dict['rangeBegin'] = self.range_begin
        if hasattr(self, 'range_end') and self.range_end is not None:
            _dict['rangeEnd'] = self.range_end
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'cui',
                       'dimension', 'preferred_name', 'trigger', 'source', 'value', 'section_normalized_name',
                       'section_surface_form', 'rule_id', 'derived_from', 'unit', 'values', 'range_begin', 'range_end'})
        if not hasattr(self, '_additionalProperties'):
            super(ConceptValue, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(ConceptValue, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this ConceptValue object."""
        return json.dumps(self._to_dict(), indent=2)


class ConfigurationEntity():
    """
    ConfigurationEntity.

    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int mergeid: (optional)
    """

    def __init__(self, *, id: str = None, type: str = None, uid: int = None, mergeid: int = None) -> None:
        """
        Initialize a ConfigurationEntity object.

        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int mergeid: (optional)
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.mergeid = mergeid

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ConfigurationEntity':
        """Initialize a ConfigurationEntity object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'uid' in _dict:
            args['uid'] = _dict.get('uid')
        if 'mergeid' in _dict:
            args['mergeid'] = _dict.get('mergeid')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ConfigurationEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'mergeid') and self.mergeid is not None:
            _dict['mergeid'] = self.mergeid
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ConfigurationEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ConfigurationEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ConfigurationEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ContainerAnnotation(object):
    """
    ContainerAnnotation.
    :attr list[Annotation] allergy_ind: (optional)
    :attr list[Annotation] allergy_medication_ind: (optional)
    :attr list[AttributeValueAnnotation] attribute_values: (optional)
    :attr list[AssistanceAnnotation] bathing_assistance_ind: (optional)
    :attr list[CancerDiagnosis] ica_cancer_diagnosis_ind: (optional)
    :attr list[Concept] concepts: (optional)
    :attr list[ConceptValue] concept_values: (optional)
    :attr list[AssistanceAnnotation] dressing_assistance_ind: (optional)
    :attr list[AssistanceAnnotation] eating_assistance_ind: (optional)
    :attr list[EjectionFractionAnnotation] ejection_fraction_ind: (optional)
    :attr list[Annotation] hypothetical_spans: (optional)
    :attr list[LabValueAnnotation] lab_value_ind: (optional)
    :attr list[MedicationAnnotation] medication_ind: (optional)
    :attr list[Annotation] email_address_ind: (optional)
    :attr list[Annotation] location_ind: (optional)
    :attr list[Annotation] person_ind: (optional)
    :attr list[Annotation] u_s_phone_number_ind: (optional)
    :attr list[Annotation] medical_institution_ind: (optional)
    :attr list[Annotation] organization_ind: (optional)
    :attr list[NegatedSpan] negated_spans: (optional)
    :attr list[Procedure] procedure_ind: (optional)
    :attr list[AssistanceAnnotation] seeing_assistance_ind: (optional)
    :attr list[Smoking] smoking_ind: (optional)
    :attr list[SymptomDisease] symptom_disease_ind: (optional)
    :attr list[AssistanceAnnotation] toileting_assistance_ind: (optional)
    :attr list[AssistanceAnnotation] walking_assistance_ind: (optional)
    :attr list[Section] sections: (optional)
    :attr list[NluEntities] nlu_entities: (optional)
    :attr list[Relations] relations: (optional)
    :attr list[SpellingCorrection]: (optional)
    :attr list[SpellCorrectedText] spell_corrected_text: (optional)
    :attr list[Temporal] temporal_spans: (optional)
    """

    def __init__(self, allergy_ind=None, allergy_medication_ind=None, attribute_values=None,
                 bathing_assistance_ind=None, ica_cancer_diagnosis_ind=None, concepts=None,
                 concept_values=None, dressing_assistance_ind=None, eating_assistance_ind=None,
                 ejection_fraction_ind=None, hypothetical_spans=None, lab_value_ind=None, medication_ind=None,
                 email_address_ind=None, location_ind=None, person_ind=None, u_s_phone_number_ind=None,
                 medical_institution_ind=None, organization_ind=None, negated_spans=None, procedure_ind=None,
                 seeing_assistance_ind=None, smoking_ind=None, symptom_disease_ind=None, toileting_assistance_ind=None,
                 walking_assistance_ind=None, sections=None, nlu_entities=None, relations=None,
                 spelling_corrections=None, spell_corrected_text=None, temporal_spans=None):
        """
        Initialize a ContainerAnnotation object.
        :param list[Annotation] allergy_ind: (optional)
        :param list[Annotation] allergy_medication_ind: (optional)
        :param list[AttributeValueAnnotation] attribute_values: (optional)
        :param list[AssistanceAnnotation] bathing_assistance_ind: (optional)
        :param list[CancerDiagnosis] ica_cancer_diagnosis_ind: (optional)
        :param list[Concept] concepts: (optional)
        :param list[ConceptValue] concept_values: (optional)
        :param list[AssistanceAnnotation] dressing_assistance_ind: (optional)
        :param list[AssistanceAnnotation] eating_assistance_ind: (optional)
        :param list[EjectionFractionAnnotation] ejection_fraction_ind: (optional)
        :param list[Annotation] hypothetical_spans: (optional)
        :param list[LabValueAnnotation] lab_value_ind: (optional)
        :param list[MedicationAnnotation] medication_ind: (optional)
        :param list[Annotation] email_address_ind: (optional)
        :param list[Annotation] location_ind: (optional)
        :param list[Annotation] person_ind: (optional)
        :param list[Annotation] u_s_phone_number_ind: (optional)
        :param list[Annotation] medical_institution_ind: (optional)
        :param list[Annotation] organization_ind: (optional)
        :param list[NegatedSpan] negated_spans: (optional)
        :param list[Procedure] procedure_ind: (optional)
        :param list[AssistanceAnnotation] seeing_assistance_ind: (optional)
        :param list[Smoking] smoking_ind: (optional)
        :param list[SymptomDisease] symptom_disease_ind: (optional)
        :param list[AssistanceAnnotation] toileting_assistance_ind: (optional)
        :param list[AssistanceAnnotation] walking_assistance_ind: (optional)
        :param list[Section] sections: (optional)
        :param list[NluEntities] nlu_entities: (optional)
        :param list[Relations] relations: (optional)
        :param list[SpellingCorrection] spelling_correction: (optional)
        :param list[SpellCorrectedText] spell_corrected_text: (optional)
        :param list[Temporal] temporal_spans: (optional)
        """
        self.allergy_ind = allergy_ind
        self.allergy_medication_ind = allergy_medication_ind
        self.attribute_values = attribute_values
        self.bathing_assistance_ind = bathing_assistance_ind
        self.ica_cancer_diagnosis_ind = ica_cancer_diagnosis_ind
        self.concepts = concepts
        self.concept_values = concept_values
        self.dressing_assistance_ind = dressing_assistance_ind
        self.eating_assistance_ind = eating_assistance_ind
        self.ejection_fraction_ind = ejection_fraction_ind
        self.hypothetical_spans = hypothetical_spans
        self.lab_value_ind = lab_value_ind
        self.medication_ind = medication_ind
        self.email_address_ind = email_address_ind
        self.location_ind = location_ind
        self.person_ind = person_ind
        self.u_s_phone_number_ind = u_s_phone_number_ind
        self.medical_institution_ind = medical_institution_ind
        self.organization_ind = organization_ind
        self.negated_spans = negated_spans
        self.procedure_ind = procedure_ind
        self.seeing_assistance_ind = seeing_assistance_ind
        self.smoking_ind = smoking_ind
        self.symptom_disease_ind = symptom_disease_ind
        self.toileting_assistance_ind = toileting_assistance_ind
        self.walking_assistance_ind = walking_assistance_ind
        self.sections = sections
        self.nlu_entities = nlu_entities
        self.relations = relations
        self.spelling_corrections = spelling_corrections
        self.spell_corrected_text = spell_corrected_text
        self.temporal_spans = temporal_spans

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a ContainerAnnotation object from a json dictionary."""
        args = {}
        if 'AllergyMedicationInd' in _dict:
            args['allergy_medication_ind'] = [Annotation._from_dict(x) for x in _dict['AllergyMedicationInd']]
        if 'AllergyInd' in _dict:
            args['allergy_ind'] = [Annotation._from_dict(x) for x in _dict['AllergyInd']]
        if 'attributeValues' in _dict:
            args['attribute_values'] = [AttributeValueAnnotation._from_dict(x) for x in _dict['attributeValues']]
        if 'BathingAssistanceInd' in _dict:
            args['bathing_assistance_ind'] = ([AssistanceAnnotation._from_dict(x)
                                               for x in _dict['BathingAssistanceInd']])
        if 'IcaCancerDiagnosisInd' in _dict:
            args['ica_cancer_diagnosis_ind'] = [CancerDiagnosis._from_dict(x) for x in _dict['IcaCancerDiagnosisInd']]
        if 'concepts' in _dict:
            args['concepts'] = [Concept._from_dict(x) for x in _dict['concepts']]
        if 'conceptValues' in _dict:
            args['concept_values'] = [ConceptValue._from_dict(x) for x in _dict['conceptValues']]
        if 'DressingAssistanceInd' in _dict:
            args['dressing_assistance_ind'] = ([AssistanceAnnotation._from_dict(x)
                                                for x in _dict['DressingAssistanceInd']])
        if 'EatingAssistanceInd' in _dict:
            args['eating_assistance_ind'] = [AssistanceAnnotation._from_dict(x) for x in _dict['EatingAssistanceInd']]
        if 'EjectionFractionInd' in _dict:
            args['ejection_fraction_ind'] = ([EjectionFractionAnnotation._from_dict(x)
                                              for x in _dict['EjectionFractionInd']])
        if 'hypotheticalSpans' in _dict:
            args['hypothetical_spans'] = [Annotation._from_dict(x) for x in _dict['hypotheticalSpans']]
        if 'LabValueInd' in _dict:
            args['lab_value_ind'] = [LabValueAnnotation._from_dict(x) for x in _dict['LabValueInd']]
        if 'MedicationInd' in _dict:
            args['medication_ind'] = [MedicationAnnotation._from_dict(x) for x in _dict['MedicationInd']]
        if 'EmailAddressInd' in _dict:
            args['email_address_ind'] = [Annotation._from_dict(x) for x in _dict['EmailAddressInd']]
        if 'LocationInd' in _dict:
            args['location_ind'] = [Annotation._from_dict(x) for x in _dict['LocationInd']]
        if 'PersonInd' in _dict:
            args['person_ind'] = [Annotation._from_dict(x) for x in _dict['PersonInd']]
        if 'US_PhoneNumberInd' in _dict:
            args['u_s_phone_number_ind'] = [Annotation._from_dict(x) for x in _dict['US_PhoneNumberInd']]
        if 'MedicalInstitutionInd' in _dict:
            args['medical_institution_ind'] = [Annotation._from_dict(x) for x in _dict['MedicalInstitutionInd']]
        if 'OrganizationInd' in _dict:
            args['organization_ind'] = [Annotation._from_dict(x) for x in _dict['OrganizationInd']]
        if 'negatedSpans' in _dict:
            args['negated_spans'] = [NegatedSpan._from_dict(x) for x in _dict['negatedSpans']]
        if 'ProcedureInd' in _dict:
            args['procedure_ind'] = [Procedure._from_dict(x) for x in _dict['ProcedureInd']]
        if 'SeeingAssistanceInd' in _dict:
            args['seeing_assistance_ind'] = [AssistanceAnnotation._from_dict(x) for x in _dict['SeeingAssistanceInd']]
        if 'SmokingInd' in _dict:
            args['smoking_ind'] = [Smoking._from_dict(x) for x in _dict['SmokingInd']]
        if 'SymptomDiseaseInd' in _dict:
            args['symptom_disease_ind'] = [SymptomDisease._from_dict(x) for x in _dict['SymptomDiseaseInd']]
        if 'ToiletingAssistanceInd' in _dict:
            args['toileting_assistance_ind'] = ([AssistanceAnnotation._from_dict(x)
                                                 for x in _dict['ToiletingAssistanceInd']])
        if 'WalkingAssistanceInd' in _dict:
            args['walking_assistance_ind'] = ([AssistanceAnnotation._from_dict(x)
                                               for x in _dict['WalkingAssistanceInd']])
        if 'sections' in _dict:
            args['sections'] = [Section._from_dict(x) for x in _dict['sections']]
        if 'nluEntities' in _dict:
            args['nlu_entities'] = [NluEntities._from_dict(x) for x in _dict['nluEntities']]
        if 'relations' in _dict:
            args['relations'] = [Relations._from_dict(x) for x in _dict['relations']]
        if 'spellingCorrections' in _dict:
            args['spelling_corrections'] = [SpellingCorrection._from_dict(x) for x in _dict['spellingCorrections']]
        if 'spellCorrectedText' in _dict:
            args['spell_corrected_text'] = [SpellCorrectedText._from_dict(x) for x in _dict['spellCorrectedText']]
        if 'temporalSpans' in _dict:
            args['temporal_spans'] = [Temporal._from_dict(x) for x in _dict['temporalSpans']]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ContainerAnnotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'allergy_medication_ind') and self.allergy_medication_ind is not None:
            _dict['AllergyMedicationInd'] = [x._to_dict() for x in self.allergy_medication_ind]
        if hasattr(self, 'allergy_ind') and self.allergy_ind is not None:
            _dict['AllergyInd'] = [x._to_dict() for x in self.allergy_ind]
        if hasattr(self, 'attribute_values') and self.attribute_values is not None:
            _dict['attributeValues'] = [x._to_dict() for x in self.attribute_values]
        if hasattr(self, 'bathing_assistance_ind') and self.bathing_assistance_ind is not None:
            _dict['BathingAssistanceInd'] = [x._to_dict() for x in self.bathing_assistance_ind]
        if hasattr(self, 'ica_cancer_diagnosis_ind') and self.ica_cancer_diagnosis_ind is not None:
            _dict['IcaCancerDiagnosisInd'] = [x._to_dict() for x in self.ica_cancer_diagnosis_ind]
        if hasattr(self, 'concepts') and self.concepts is not None:
            _dict['concepts'] = [x._to_dict() for x in self.concepts]
        if hasattr(self, 'concept_values') and self.concept_values is not None:
            _dict['conceptValues'] = [x._to_dict() for x in self.concept_values]
        if hasattr(self, 'dressing_assistance_ind') and self.dressing_assistance_ind is not None:
            _dict['DressingAssistanceInd'] = [x._to_dict() for x in self.dressing_assistance_ind]
        if hasattr(self, 'eating_assistance_ind') and self.eating_assistance_ind is not None:
            _dict['EatingAssistanceInd'] = [x._to_dict() for x in self.eating_assistance_ind]
        if hasattr(self, 'ejection_fraction_ind') and self.ejection_fraction_ind is not None:
            _dict['EjectionFractionInd'] = [x._to_dict() for x in self.ejection_fraction_ind]
        if hasattr(self, 'hypothetical_spans') and self.hypothetical_spans is not None:
            _dict['hypotheticalSpans'] = [x._to_dict() for x in self.hypothetical_spans]
        if hasattr(self, 'lab_value_ind') and self.lab_value_ind is not None:
            _dict['LabValueInd'] = [x._to_dict() for x in self.lab_value_ind]
        if hasattr(self, 'medication_ind') and self.medication_ind is not None:
            _dict['MedicationInd'] = [x._to_dict() for x in self.medication_ind]
        if hasattr(self, 'email_address_ind') and self.email_address_ind is not None:
            _dict['EmailAddressInd'] = [x._to_dict() for x in self.email_address_ind]
        if hasattr(self, 'location_ind') and self.location_ind is not None:
            _dict['LocationInd'] = [x._to_dict() for x in self.location_ind]
        if hasattr(self, 'person_ind') and self.person_ind is not None:
            _dict['PersonInd'] = [x._to_dict() for x in self.person_ind]
        if hasattr(self, 'u_s_phone_number_ind') and self.u_s_phone_number_ind is not None:
            _dict['US_PhoneNumberInd'] = [x._to_dict() for x in self.u_s_phone_number_ind]
        if hasattr(self, 'medical_institution_ind') and self.medical_institution_ind is not None:
            _dict['MedicalInstitutionInd'] = [x._to_dict() for x in self.medical_institution_ind]
        if hasattr(self, 'organization_ind') and self.organization_ind is not None:
            _dict['OrganizationInd'] = [x._to_dict() for x in self.organization_ind]
        if hasattr(self, 'negated_spans') and self.negated_spans is not None:
            _dict['negatedSpans'] = [x._to_dict() for x in self.negated_spans]
        if hasattr(self, 'procedure_ind') and self.procedure_ind is not None:
            _dict['ProcedureInd'] = [x._to_dict() for x in self.procedure_ind]
        if hasattr(self, 'seeing_assistance_ind') and self.seeing_assistance_ind is not None:
            _dict['SeeingAssistanceInd'] = [x._to_dict() for x in self.seeing_assistance_ind]
        if hasattr(self, 'smoking_ind') and self.smoking_ind is not None:
            _dict['SmokingInd'] = [x._to_dict() for x in self.smoking_ind]
        if hasattr(self, 'symptom_disease_ind') and self.symptom_disease_ind is not None:
            _dict['SymptomDiseaseInd'] = [x._to_dict() for x in self.symptom_disease_ind]
        if hasattr(self, 'toileting_assistance_ind') and self.toileting_assistance_ind is not None:
            _dict['ToiletingAssistanceInd'] = [x._to_dict() for x in self.toileting_assistance_ind]
        if hasattr(self, 'walking_assistance_ind') and self.walking_assistance_ind is not None:
            _dict['WalkingAssistanceInd'] = [x._to_dict() for x in self.walking_assistance_ind]
        if hasattr(self, 'sections') and self.sections is not None:
            _dict['sections'] = [x._to_dict() for x in self.sections]
        if hasattr(self, 'nlu_entities') and self.nlu_entities is not None:
            _dict['nluEntities'] = [x._to_dict() for x in self.nlu_entities]
        if hasattr(self, 'relations') and self.relations is not None:
            _dict['relations'] = [x._to_dict() for x in self.relations]
        if hasattr(self, 'spelling_corrections') and self.spelling_corrections is not None:
            _dict['spellingCorrections'] = [x._to_dict() for x in self.spelling_corrections]
        if hasattr(self, 'spell_corrected_text') and self.spell_corrected_text is not None:
            _dict['spellCorrectedText'] = [x._to_dict() for x in self.spell_corrected_text]
        if hasattr(self, 'temporal_spans') and self.temporal_spans is not None:
            _dict['temporalSpans'] = [x._to_dict() for x in self.temporal_spans]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this ContainerAnnotation object."""
        return json.dumps(self._to_dict(), indent=2)

class ContainerGroup(object):
    """
    ContainerGroup.
    :attr list[UnstructuredContainer] unstructured: (optional)
    :attr list[AnnotatorFlow] annotator_flows: (optional)
    """

    def __init__(self, unstructured=None, annotator_flows=None):
        """
        Initialize a ContainerGroup object.
        :param list[UnstructuredContainer] unstructured: (optional)
        :param list[AnnotatorFlow] annotator_flows: (optional)
        """
        self.unstructured = unstructured
        self.annotator_flows = annotator_flows


    @classmethod
    def from_dict(cls, _dict):
        """Initialize a ContainerGroup object from a json dictionary."""
        args = {}
        if 'unstructured' in _dict:
            args['unstructured'] = [UnstructuredContainer._from_dict(x) for x in _dict['unstructured']]
        if 'annotatorFlows' in _dict:
            args['annotator_flows'] = [AnnotatorFlow._from_dict(x) for x in _dict['annotatorFlows']]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ContainerGroup object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'unstructured') and self.unstructured is not None:
            _dict['unstructured'] = [x._to_dict() for x in self.unstructured]
        if hasattr(self, 'annotator_flows') and self.annotator_flows is not None:
            _dict['annotatorFlows'] = [x._to_dict() for x in self.annotator_flows]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()


class Disambiguation(object):
    """
    Disambiguation.
    :attr str validity: (optional)
    """

    def __init__(self, validity=None):
        """
        Initialize a Disambiguation object.
        :param str validity: (optional)
        """
        self.validity = validity

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Disambiguation object from a json dictionary."""
        args = {}
        if 'validity' in _dict:
            args['validity'] = _dict['validity']
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Disambiguation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'validity') and self.validity is not None:
            _dict['validity'] = self.validity
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this Disambiguation object."""
        return json.dumps(self._to_dict(), indent=2)

class DeployCartridgeResponse():
    """
    DeployCartridgeResponse.

    :attr int code: (optional)
    :attr List[ServiceError] artifact_response: (optional)
    """

    def __init__(self, *, code: int = None, artifact_response: List['ServiceError'] = None) -> None:
        """
        Initialize a DeployCartridgeResponse object.

        :param int code: (optional)
        :param List[ServiceError] artifact_response: (optional)
        """
        self.code = code
        self.artifact_response = artifact_response

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DeployCartridgeResponse':
        """Initialize a DeployCartridgeResponse object from a json dictionary."""
        args = {}
        if 'code' in _dict:
            args['code'] = _dict.get('code')
        if 'artifactResponse' in _dict:
            args['artifact_response'] = [ServiceError.from_dict(x) for x in _dict.get('artifactResponse')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DeployCartridgeResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'code') and self.code is not None:
            _dict['code'] = self.code
        if hasattr(self, 'artifact_response') and self.artifact_response is not None:
            _dict['artifactResponse'] = [x.to_dict() for x in self.artifact_response]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DeployCartridgeResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DeployCartridgeResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DeployCartridgeResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class EjectionFractionAnnotation(object):
    """
    EjectionFractionAnnotation.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str first_value: (optional)
    :attr str ef_alphabetic_value_surface_form: (optional)
    :attr str second_value: (optional)
    :attr str ef_term_surface_form: (optional)
    :attr str ef_suffix_surface_form: (optional)
    :attr str ef_suffix_normalized_name: (optional)
    :attr str ef_alphabetic_value_normalized_name: (optional)
    :attr str ef_term_normalized_name: (optional)
    :attr str is_range: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, first_value=None, ef_alphabetic_value_surface_form=None, second_value=None,
                 ef_term_surface_form=None, ef_suffix_surface_form=None, ef_suffix_normalized_name=None,
                 ef_alphabetic_value_normalized_name=None, ef_term_normalized_name=None, is_range=None,
                 section_normalized_name=None, section_surface_form=None, **kwargs):
        """
        Initialize a EjectionFractionAnnotation object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str first_value: (optional)
        :param str ef_alphabetic_value_surface_form: (optional)
        :param str second_value: (optional)
        :param str ef_term_surface_form: (optional)
        :param str ef_suffix_surface_form: (optional)
        :param str ef_suffix_normalized_name: (optional)
        :param str ef_alphabetic_value_normalized_name: (optional)
        :param str ef_term_normalized_name: (optional)
        :param str is_range: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.first_value = first_value
        self.ef_alphabetic_value_surface_form = ef_alphabetic_value_surface_form
        self.second_value = second_value
        self.ef_term_surface_form = ef_term_surface_form
        self.ef_suffix_surface_form = ef_suffix_surface_form
        self.ef_suffix_normalized_name = ef_suffix_normalized_name
        self.ef_alphabetic_value_normalized_name = ef_alphabetic_value_normalized_name
        self.ef_term_normalized_name = ef_term_normalized_name
        self.is_range = is_range
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a EjectionFractionAnnotation object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'firstValue' in _dict:
            args['first_value'] = _dict['firstValue']
            del xtra['firstValue']
        if 'efAlphabeticValueSurfaceForm' in _dict:
            args['ef_alphabetic_value_surface_form'] = _dict['efAlphabeticValueSurfaceForm']
            del xtra['efAlphabeticValueSurfaceForm']
        if 'secondValue' in _dict:
            args['second_value'] = _dict['secondValue']
            del xtra['secondValue']
        if 'efTermSurfaceForm' in _dict:
            args['ef_term_surface_form'] = _dict['efTermSurfaceForm']
            del xtra['efTermSurfaceForm']
        if 'efSuffixSurfaceForm' in _dict:
            args['ef_suffix_surface_form'] = _dict['efSuffixSurfaceForm']
            del xtra['efSuffixSurfaceForm']
        if 'efSuffixNormalizedName' in _dict:
            args['ef_suffix_normalized_name'] = _dict['efSuffixNormalizedName']
            del xtra['efSuffixNormalizedName']
        if 'efAlphabeticValueNormalizedName' in _dict:
            args['ef_alphabetic_value_normalized_name'] = _dict['efAlphabeticValueNormalizedName']
            del xtra['efAlphabeticValueNormalizedName']
        if 'efTermNormalizedName' in _dict:
            args['ef_term_normalized_name'] = _dict['efTermNormalizedName']
            del xtra['efTermNormalizedName']
        if 'isRange' in _dict:
            args['is_range'] = _dict['isRange']
            del xtra['isRange']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a EjectionFractionAnnotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'first_value') and self.first_value is not None:
            _dict['firstValue'] = self.first_value
        if hasattr(self, 'ef_alphabetic_value_surface_form') and self.ef_alphabetic_value_surface_form is not None:
            _dict['efAlphabeticValueSurfaceForm'] = self.ef_alphabetic_value_surface_form
        if hasattr(self, 'second_value') and self.second_value is not None:
            _dict['secondValue'] = self.second_value
        if hasattr(self, 'ef_term_surface_form') and self.ef_term_surface_form is not None:
            _dict['efTermSurfaceForm'] = self.ef_term_surface_form
        if hasattr(self, 'ef_suffix_surface_form') and self.ef_suffix_surface_form is not None:
            _dict['efSuffixSurfaceForm'] = self.ef_suffix_surface_form
        if hasattr(self, 'ef_suffix_normalized_name') and self.ef_suffix_normalized_name is not None:
            _dict['efSuffixNormalizedName'] = self.ef_suffix_normalized_name
        if hasattr(self, 'ef_alphabetic_value_normalized_name') and self.ef_alphabetic_value_normalized_name is not None:
            _dict['efAlphabeticValueNormalizedName'] = self.ef_alphabetic_value_normalized_name
        if hasattr(self, 'ef_term_normalized_name') and self.ef_term_normalized_name is not None:
            _dict['efTermNormalizedName'] = self.ef_term_normalized_name
        if hasattr(self, 'is_range') and self.is_range is not None:
            _dict['isRange'] = self.is_range
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'first_value',
                       'ef_alphabetic_value_surface_form', 'second_value', 'ef_term_surface_form',
                       'ef_suffix_surface_form', 'ef_suffix_normalized_name', 'ef_alphabetic_value_normalized_name',
                       'ef_term_normalized_name', 'is_range', 'section_normalized_name', 'section_surface_form'})
        if not hasattr(self, '_additionalProperties'):
            super(EjectionFractionAnnotation, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(EjectionFractionAnnotation, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this EjectionFractionAnnotation object."""
        return json.dumps(self._to_dict(), indent=2)


class Entity():
    """
    Entity.

    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int mergeid: (optional)
    """

    def __init__(self, *, id: str = None, type: str = None, uid: int = None, mergeid: int = None) -> None:
        """
        Initialize a Entity object.

        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int mergeid: (optional)
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.mergeid = mergeid

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Entity':
        """Initialize a Entity object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'uid' in _dict:
            args['uid'] = _dict.get('uid')
        if 'mergeid' in _dict:
            args['mergeid'] = _dict.get('mergeid')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Entity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'mergeid') and self.mergeid is not None:
            _dict['mergeid'] = self.mergeid
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Entity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Entity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Entity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Flow():
    """
    Flow.

    :attr List[FlowEntry] elements: (optional)
    :attr bool async_: (optional)
    """

    def __init__(self, *, elements: List['FlowEntry'] = None, async_: bool = None) -> None:
        """
        Initialize a Flow object.

        :param List[FlowEntry] elements: (optional)
        :param bool async_: (optional)
        """
        self.elements = elements
        self.async_ = async_

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Flow':
        """Initialize a Flow object from a json dictionary."""
        args = {}
        if 'elements' in _dict:
            args['elements'] = [FlowEntry.from_dict(x) for x in _dict.get('elements')]
        if 'async' in _dict:
            args['async_'] = _dict.get('async')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Flow object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'elements') and self.elements is not None:
            _dict['elements'] = [x.to_dict() for x in self.elements]
        if hasattr(self, 'async_') and self.async_ is not None:
            _dict['async'] = self.async_
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Flow object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Flow') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Flow') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class FlowEntry():
    """
    FlowEntry.
    :attr Annotator annotator: (optional)
    """

    def __init__(self, annotator=None) -> None:
        """
        Initialize a FlowEntry object.
        :param Annotator annotator: (optional)
        """
        self.annotator = annotator

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'FlowEntry':
        """Initialize a FlowEntry object from a json dictionary."""
        args = {}
        if 'annoator' in _dict:
            args['annotator'] = _dict['annotator']
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FlowEntry object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'annotator') and self.annotator is not None:
            _dict['annotator'] = self.annotator
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FlowEntry object."""
        return json.dumps(self.to_dict(), indent=2, cls=AnnotatorEncoder)

    def __eq__(self, other: 'FlowEntry') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'FlowEntry') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class InsightModelDataUsage(object):
    """
    InsightModelData Usage.
    :attr float taken_score: (optional)
    :attr float explicit_score: (optional)
    :attr float implicit_score: (optional)
    :attr float considering_score: (optional)
    :attr float patient_reported_score: (optional)
    :attr float discussed_score: (optional)
    :attr float lab_measurement_score: (optional)
    :attr float pending_score: (optional)
    """

    def __init__(self, taken_score=None, explicit_score=None, implicit_score=None, considering_score=None,
                 patient_reported_score=None, discussed_score=None, lab_measurement_score=None, 
                 pending_score=None, **kwargs):
        """
        Initialize an InsightModelData Usage object.
        :param float taken_score: (optional)
        :param float explicit_score: (optional)
        :param float implicit_score: (optional)
        :param float considering_score: (optional)
        :param float patient_reported_score: (optional)
        :param float discussed_score: (optional)
        :param float lab_measurement_score: (optional)
        :param float pending_score: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.taken_score = taken_score
        self.explicit_score = explicit_score
        self.implicit_score = implicit_score
        self.considering_score = considering_score
        self.patient_reported_score = patient_reported_score
        self.discussed_score = discussed_score
        self.lab_measurement_score = lab_measurement_score
        self.pending_score = pending_score
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Usage object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'takenScore' in _dict:
            args['taken_score'] = _dict['takenScore']
            del xtra['takenScore']
        if 'explicitScore' in _dict:
            args['explicit_score'] = _dict['explicitScore']
            del xtra['explicitScore']
        if 'implicitScore' in _dict:
            args['implicit_score'] = _dict['implicitScore']
            del xtra['implicitScore']
        if 'consideringScore' in _dict:
            args['considering_score'] = _dict['consideringScore']
            del xtra['consideringScore']
        if 'patientReportedScore' in _dict:
            args['patient_reported_score'] = _dict['patientReportedScore']
            del xtra['patientReportedScore']
        if 'discussedScore' in _dict:
            args['discussed_score'] = _dict['discussedScore']
            del xtra['discussedScore']
        if 'labMeasurementScore' in _dict:
            args['lab_measurement_score'] = _dict['labMeasurementScore']
            del xtra['labMeasurementScore']
        if 'pendingScore' in _dict:
            args['pending_score'] = _dict['pendingScore']
            del xtra['pendingScore']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Usage object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'taken_score') and self.taken_score is not None:
            _dict['takenScore'] = self.taken_score
        if hasattr(self, 'explicit_score') and self.explicit_score is not None:
            _dict['explicitScore'] = self.explicit_score
        if hasattr(self, 'implicit_score') and self.implicit_score is not None:
            _dict['implicitScore'] = self.implicit_score
        if hasattr(self, 'considering_score') and self.considering_score is not None:
            _dict['consideringScore'] = self.considering_score
        if hasattr(self, 'patient_reported_score') and self.patient_reported_score is not None:
            _dict['patientReportedScore'] = self.patient_reported_score
        if hasattr(self, 'discussed_score') and self.discussed_score is not None:
            _dict['discussedScore'] = self.discussed_score
        if hasattr(self, 'lab_measurement_score') and self.lab_measurement_score is not None:
            _dict['labMeasurementScore'] = self.lab_measurement_score
        if hasattr(self, 'pending_score') and self.pending_score is not None:
            _dict['pendingScore'] = self.pending_score
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'taken_score', 'explicit_score', 'implicit_score', 'considering_score', 'patient_reported_score', 'discussed_score', 'lab_measurement_score', 'pending_score'})
        if not hasattr(self, '_additionalProperties'):
            super(InsightModelDataUsage, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InsightModelDataUsage, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Usage object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataTask(object):
    """
    InsightModelData Task.
    :attr float therapeutic_score: (optional)
    :attr float diagnostic_score: (optional)
    :attr float lab_test_score: (optional)
    :attr float surgical_task_score: (optional)
    :attr float clinical_assessment_score: (optional)
    """

    def __init__(self, therapeutic_score=None, diagnostic_score=None, lab_test_score=None, surgical_task_score=None, clinical_assessment_score=None, **kwargs):
        """
        Initialize an InsightModelData Task object.
        :param float therapeutic_score: (optional)
        :param float diagnostic_score: (optional)
        :param float lab_test_score: (optional)
        :param float surgical_task_score: (optional)
        :param float clinical_assessment_score: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.therapeutic_score = therapeutic_score
        self.diagnostic_score = diagnostic_score
        self.lab_test_score = lab_test_score
        self.surgical_task_score = surgical_task_score
        self.clinical_assessment_score = clinical_assessment_score
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Task object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'therapeuticScore' in _dict:
            args['therapeutic_score'] = _dict['therapeuticScore']
            del xtra['therapeuticScore']
        if 'diagnosticScore' in _dict:
            args['diagnostic_score'] = _dict['diagnosticScore']
            del xtra['diagnosticScore']
        if 'labTestScore' in _dict:
            args['lab_test_score'] = _dict['labTestScore']
            del xtra['labTestScore']
        if 'surgicalTaskScore' in _dict:
            args['surgical_task_score'] = _dict['surgicalTaskScore']
            del xtra['surgicalTaskScore']
        if 'clinicalAssessmentScore' in _dict:
            args['clinical_assessment_score'] = _dict['clinicalAssessmentScore']
            del xtra['clinicalAssessmentScore']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Task object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'therapeutic_score') and self.therapeutic_score is not None:
            _dict['therapeuticScore'] = self.therapeutic_score
        if hasattr(self, 'diagnostic_score') and self.diagnostic_score is not None:
            _dict['diagnosticScore'] = self.diagnostic_score
        if hasattr(self, 'lab_test_score') and self.lab_test_score is not None:
            _dict['labTestScore'] = self.lab_test_score
        if hasattr(self, 'surgical_task_score') and self.surgical_task_score is not None:
            _dict['surgicalTaskScore'] = self.surgical_task_score
        if hasattr(self, 'clinical_assessment_score') and self.clinical_assessment_score is not None:
            _dict['clinicalAssessmentScore'] = self.clinical_assessment_score
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'therapeutic_score', 'diagnostic_score', 'lab_test_score', 'surgical_task_score', 'clinical_assessment_score'})
        if not hasattr(self, '_additionalProperties'):
            super(InsightModelDataTask, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InsightModelDataTask, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Task object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataType(object):
    """
    InsightModelData Type.
    :attr float device_score: (optional)
    :attr float material_score: (optional)
    :attr float medication_score: (optional)
    :attr float procedure_score: (optional)
    :attr float condition_management_score: (optional)
    """

    def __init__(self, device_score=None, material_score=None, medication_score=None, procedure_score=None, condition_management_score=None, **kwargs):
        """
        Initialize an InsightModelData Type object.
        :param float device_score: (optional)
        :param float material_score: (optional)
        :param float medication_score: (optional)
        :param float procedure_score: (optional)
        :param float condition_management_score: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.device_score = device_score
        self.material_score = material_score
        self.medication_score = medication_score
        self.procedure_score = procedure_score
        self.condition_management_score = condition_management_score
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Type object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'deviceScore' in _dict:
            args['device_score'] = _dict['deviceScore']
            del xtra['deviceScore']
        if 'materialScore' in _dict:
            args['material_score'] = _dict['materialScore']
            del xtra['materialScore']
        if 'medicationScore' in _dict:
            args['medication_score'] = _dict['medicationScore']
            del xtra['medicationScore']
        if 'procedureScore' in _dict:
            args['procedure_score'] = _dict['procedureScore']
            del xtra['procedureScore']
        if 'conditionManagementScore' in _dict:
            args['condition_management_score'] = _dict['conditionManagementScore']
            del xtra['conditionManagementScore']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Type object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'device_score') and self.device_score is not None:
            _dict['deviceScore'] = self.device_score
        if hasattr(self, 'material_score') and self.material_score is not None:
            _dict['materialScore'] = self.material_score
        if hasattr(self, 'medication_score') and self.medication_score is not None:
            _dict['medicationScore'] = self.medication_score
        if hasattr(self, 'procedure_score') and self.procedure_score is not None:
            _dict['procedureScore'] = self.procedure_score
        if hasattr(self, 'condition_management_score') and self.condition_management_score is not None:
            _dict['conditionManagementScore'] = self.condition_management_score
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'device_score', 'material_score', 'medication_score', 'procedure_score', 'condition_management_score'})
        if not hasattr(self, '_additionalProperties'):
            super(InsightModelDataType, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InsightModelDataType, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Type object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataEvent(object):
    """
    InsightModelData Event.
    :attr float score: (optional)
    :attr float allergy_score: (optional)
    :attr InsightModelDataUsage usage: (optional)
    """

    def __init__(self, score=None, allergy_score=None, usage=None, **kwargs):
        """
        Initialize an InsightModelData Event object.
        :param float score: (optional)
        "param float allergy_score: (optional)
        :param InsightModelDataUsage usage: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.score = score
        self.allergy_score = allergy_score
        self.usage = usage
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Event object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'score' in _dict:
            args['score'] = _dict['score']
            del xtra['score']
        if 'allergyScore' in _dict:
            args['allergy_score'] = _dict['allergyScore']
            del xtra['allergyScore']
        if 'usage' in _dict:
            args['usage'] = InsightModelDataUsage._from_dict(_dict['usage'])
            del xtra['usage']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Event object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'score') and self.score is not None:
            _dict['score'] = self.score
        if hasattr(self, 'allergy_score') and self.allergy_score is not None:
            _dict['allergyScore'] = self.allergy_score
        if hasattr(self, 'usage') and self.usage is not None:
            _dict['usage'] = self.usage._to_dict()
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'score', 'allergy_score', 'usage'})
        if not hasattr(self, '_additionalProperties'):
            super(InsightModelDataEvent, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InsightModelDataEvent, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Event object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataNormalityUsage(object):
    """
    InsightModelData Normality Usage.
    :attr float normal_score: (optional)
    :attr float abnormal_score: (optional)
    :attr float unknown_score: (optional)
    :attr float non_finding_score: (optional)
    """

    def __init__(self, normal_score=None, abnormal_score=None, unknown_score=None, non_finding_score=None, **kwargs):
        """
        Initialize an InsightModelData Normality Usage object.
        :param float normal_score: (optional)
        :param float abnormal_score: (optional)
        :param float unknown_score: (optional)
        :param float non_finding_score: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.normal_score = normal_score
        self.abnormal_score = abnormal_score
        self.unknown_score = unknown_score
        self.non_finding_score = non_finding_score
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Normality Usage object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'normalScore' in _dict:
            args['normal_score'] = _dict['normalScore']
            del xtra['normalScore']
        if 'abnormalScore' in _dict:
            args['abnormal_score'] = _dict['abnormalScore']
            del xtra['abnormalScore']
        if 'unknownScore' in _dict:
            args['unknown_score'] = _dict['unknownScore']
            del xtra['unknownScore']
        if 'nonFindingScore' in _dict:
            args['non_finding_score'] = _dict['nonFindingScore']
            del xtra['nonFindingScore']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Normality Usage object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'normal_score') and self.normal_score is not None:
            _dict['normalScore'] = self.normal_score
        if hasattr(self, 'abnormal_score') and self.abnormal_score is not None:
            _dict['abnormalScore'] = self.abnormal_score
        if hasattr(self, 'unknown_score') and self.unknown_score is not None:
            _dict['unknownScore'] = self.unknown_score
        if hasattr(self, 'non_finding_score') and self.non_finding_score is not None:
            _dict['nonFindingScore'] = self.non_finding_score
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'normal_score', 'abnormal_score', 'unknown_score', 'non_finding_score'})
        if not hasattr(self, '_additionalProperties'):
            super(InsightModelDataNormalityUsage, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InsightModelDataNormalityUsage, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Normality Usage object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataEvidence(object):
    """
    InsightModelData Evidence.
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    """ 
        
    def __init__(self, begin=None, end=None, covered_text=None, **kwargs):
        """
        Initialize an InsightModelData Evidence object.
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)
    
    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Evidence object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText'] 
        args.update(xtra)
        return cls(**args)
    
    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Evidence object from a json dictionary."""
        return cls.from_dict(_dict)
        
    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict
        
    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()
        
    def __setattr__(self, name, value):
        properties = ({'begin', 'end', 'covered_text'})
        if not hasattr(self, '_additionalProperties'):
            super(InsightModelDataEvidence, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InsightModelDataEvidence, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Evidence object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataMedication(object):
    """
    InsightModelData Medication.
    :attr InsightModelDataUsage usage: (optional)
    :attr InsightModelDataEvent started: (optional)
    :attr InsightModelDataEvent stopped: (optional)
    :attr InsightModelDataEvent dose_changed: (optional)
    :attr InsightModelDataEvent adverse: (optional)
    """

    def __init__(self, usage=None, started=None, stopped=None, dose_changed=None, adverse=None, **kwargs):
        """
        Initialize an InsightModelData Medication object.
        :param InsightModelDataUsage usage: (optional)
        :param InsightModelDataEvent started: (optional)
        :param InsightModelDataEvent stopped: (optional)
        :param InsightModelDataEvent dose_changed: (optional)
        :param InsightModelDataEvent adverse: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.usage = usage
        self.started = started
        self.stopped = stopped
        self.dose_changed = dose_changed
        self.adverse = adverse
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Medication object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'usage' in _dict:
            args['usage'] = InsightModelDataUsage._from_dict(_dict['usage'])
            del xtra['usage']
        if 'started' in _dict:
            args['started'] = InsightModelDataEvent._from_dict(_dict['started'])
            del xtra['started']
        if 'stopped' in _dict:
            args['stopped'] = InsightModelDataEvent._from_dict(_dict['stopped'])
            del xtra['stopped']
        if 'doseChanged' in _dict:
            args['dose_changed'] = InsightModelDataEvent._from_dict(_dict['doseChanged'])
            del xtra['doseChanged']
        if 'adverse' in _dict:
            args['adverse'] = InsightModelDataEvent._from_dict(_dict['adverse'])
            del xtra['adverse']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Medication object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'usage') and self.usage is not None:
            _dict['usage'] = self.usage._to_dict()
        if hasattr(self, 'started') and self.started is not None:
            _dict['started'] = self.started._to_dict()
        if hasattr(self, 'stopped') and self.stopped is not None:
            _dict['stopped'] = self.stopped._to_dict()
        if hasattr(self, 'dose_changed') and self.dose_changed is not None:
            _dict['doseChanged'] = self.dose_changed._to_dict()
        if hasattr(self, 'adverse') and self.adverse is not None:
            _dict['adverse'] = self.adverse._to_dict()
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
            properties = ({'usage', 'started', 'stopped', 'dose_changed', 'adverse'})
            if not hasattr(self, '_additionalProperties'):
                super(InsightModelDataMedication, self).__setattr__('_additionalProperties', set())
            if name not in properties:
                self._additionalProperties.add(name)
            super(InsightModelDataMedication, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Medication object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataProcedure(object):
    """
    InsightModelData Procedure.
    :attr InsightModelDataUsage usage: (optional)
    :attr InsightModelDataTask task: (optional)
    :attr InsightModelDataType type: (optional)
    :attr InsightModelDataProcedureModifier modifiers: (optional)
    """

    def __init__(self, usage=None, task=None, type=None, modifiers=None, **kwargs):
        """
        Initialize an InsightModelData Procedure object.
        :param InsightModelDataUsage usage: (optional)
        :param InsightModelDataTask task: (optional)
        :param InsightModelDataType type: (optional)
        :param InsightModelDataProcedureModifier modifiers: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.usage = usage
        self.task = task
        self.type = type
        self.modifiers = modifiers
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Procedure object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'usage' in _dict:
            args['usage'] = InsightModelDataUsage._from_dict(_dict['usage'])
            del xtra['usage']
        if 'task' in _dict:
            args['task'] = InsightModelDataTask._from_dict(_dict['task'])
            del xtra['task']
        if 'type' in _dict:
            args['type'] = InsightModelDataType._from_dict(_dict['type'])
            del xtra['type']
        if 'modifiers' in _dict:
            args['modifiers'] = InsightModelDataProcedureModifier._from_dict(_dict['modifiers'])
            del xtra['modifiers']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Procedure object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'usage') and self.usage is not None:
            _dict['usage'] = self.usage._to_dict()
        if hasattr(self, 'task') and self.task is not None:
            _dict['task'] = self.task._to_dict()
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type._to_dict()
        if hasattr(self, 'modifiers') and self.modifiers is not None:
            _dict['modifiers'] = self.modifiers._to_dict()
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
            properties = ({'usage', 'task', 'type', 'modifiers'})
            if not hasattr(self, '_additionalProperties'):
                super(InsightModelDataProcedure, self).__setattr__('_additionalProperties', set())
            if name not in properties:
                self._additionalProperties.add(name)
            super(InsightModelDataProcedure, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Procedure object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataProcedureModifier(object):
    """
    InsightModelData Procedure Modifier.
    :attr list[InsightModelDataEvidence] associated_diagnosis: (optional)
    :attr list[InsightModelDataSite] sites: (optional)
    """

    def __init__(self, associated_diagnosis=None, sites=None, **kwargs):
        """
        Initialize an InsightModelData Procedure Modifier object.
        :param list[InsightModelDataEvidence] associated_diagnosis: (optional)
        :param list[InsightModelDataSite] sites: (optional)
        """
        self.associated_diagnosis = associated_diagnosis
        self.sites = sites
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Procedure Modifier object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'associatedDiagnosis' in _dict:
            args['associated_diagnosis'] = [InsightModelDataEvidence._from_dict(entry) for entry in _dict['associatedDiagnosis']]
            del xtra['associatedDiagnosis']
        if 'sites' in _dict:
            args['sites'] = [InsightModelDataSite._from_dict(entry) for entry in _dict['sites']]
            del xtra['sites']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Procedure Modifier object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'associated_diagnosis') and self.associated_diagnosis is not None:
            _dict['associatedDiagnosis'] = [entry._to_dict() for entry in self.associated_diagnosis]
        if hasattr(self, 'sites') and self.sites is not None:
            _dict['sites'] = [entry._to_dict() for entry in self.sites]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
            properties = ({'associated_diagnosis', 'sites'})
            if not hasattr(self, '_additionalProperties'):
                super(InsightModelDataProcedureModifier, self).__setattr__('_additionalProperties', set())
            if name not in properties:
                self._additionalProperties.add(name)
            super(InsightModelDataProcedureModifier, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Procedure Modifier object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataSite(object):
    """
    InsightModelData Site.
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr str type: (optional)
    """

    def __init__(self, begin=None, end=None, covered_text=None, type=None, **kwargs):
        """
        Initialize an InsightModelData Site object.
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param str type: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.type = type
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)
   
    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Site object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Site object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()


class InsightModelDataDiagnosis(object):
    """
    InsightModelData Diagnosis.
    :attr InsightModelDataUsage usage: (optional)
    :attr float suspected_score: (optional)
    :attr float symptom_score: (optional)
    :attr float trauma_score: (optional)
    :attr float family_history_score: (optional)
    :attr InsightModelDataDiagnosisModifier modifiers: (optional)
    """

    def __init__(self, usage=None, suspected_score=None, symptom_score=None, trauma_score=None, family_history_score=None, modifiers=None, **kwargs):
        """
        Initialize an InsightModelData Diagnosis object.
        :param InsightModelDataUsage usage: (optional)
        :param float suspected_score: (optional)
        :param float symptom_score: (optional)
        :param float trauma_score: (optional)
        :param float family_history_score: (optional)
        :param InsightModelDataDiagnosisModifier modifiers: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.usage = usage
        self.suspected_score = suspected_score
        self.symptom_score = symptom_score
        self.trauma_score = trauma_score
        self.family_history_score = family_history_score
        self.modifiers = modifiers
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Diagnosis object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'usage' in _dict:
            args['usage'] = InsightModelDataUsage._from_dict(_dict['usage'])
            del xtra['usage']
        if 'suspectedScore' in _dict:
            args['suspected_score'] = _dict['suspectedScore']
            del xtra['suspectedScore']
        if 'symptomScore' in _dict:
            args['symptom_score'] = _dict['symptomScore']
            del xtra['symptomScore']
        if 'traumaScore' in _dict:
            args['trauma_score'] = _dict['traumaScore']
            del xtra['traumaScore']
        if 'familyHistoryScore' in _dict:
            args['family_history_score'] = _dict['familyHistoryScore']
            del xtra['familyHistoryScore']
        if 'modifiers' in _dict:
            args['modifiers'] = InsightModelDataDiagnosisModifier._from_dict(_dict['modifiers'])
            del xtra['modifiers']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Diagnosis object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'usage') and self.usage is not None:
            _dict['usage'] = self.usage._to_dict()
        if hasattr(self, 'suspected_score') and self.suspected_score is not None:
            _dict['suspectedScore'] = self.suspected_score
        if hasattr(self, 'symptom_score') and self.symptom_score is not None:
            _dict['symptomScore'] = self.symptom_score
        if hasattr(self, 'trauma_score') and self.trauma_score is not None:
            _dict['traumaScore'] = self.trauma_score
        if hasattr(self, 'family_history_score') and self.family_history_score is not None:
            _dict['familyHistoryScore'] = self.family_history_score
        if hasattr(self, 'modifiers') and self.modifiers is not None:
            _dict['modifiers'] = self.modifiers._to_dict()
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
            properties = ({'usage', 'suspected_score', 'symptom_score', 'trauma_score', 'family_history_score', 'modifiers'})
            if not hasattr(self, '_additionalProperties'):
                super(InsightModelDataDiagnosis, self).__setattr__('_additionalProperties', set())
            if name not in properties:
                self._additionalProperties.add(name)
            super(InsightModelDataDiagnosis, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Diagnosis object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataDiagnosisModifier(object):
    """
    InsightModelData Diagnosis Modifier.
    :attr list[InsightModelDataEvidence] associated_procedures: (optional)
    :attr list[InsightModelDataSite] sites: (optional)
    """

    def __init__(self, associated_procedures=None, sites=None, **kwargs):
        """
        Initialize an InsightModelData Diagnosis Modifier object.
        :param list[InsightModelDataEvidence] associated_procedures: (optional)
        :param list[InsightModelDataSite] sites: (optional)
        """
        self.associated_procedures = associated_procedures
        self.sites = sites
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Diagnosis Modifier object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'associatedProcedures' in _dict:
            args['associated_procedures'] = [InsightModelDataEvidence._from_dict(entry) for entry in _dict['associatedProcedures']]
            del xtra['associatedProcedures']
        if 'sites' in _dict:
            args['sites'] = [InsightModelDataSite._from_dict(entry) for entry in _dict['sites']]
            del xtra['sites']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Diagnosis Modifier object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'associated_procedures') and self.associated_procedures is not None:
            _dict['associatedProcedures'] = [entry._to_dict() for entry in self.associated_procedures]
        if hasattr(self, 'sites') and self.sites is not None:
            _dict['sites'] = [entry._to_dict() for entry in self.sites]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
            properties = ({'associated_procedures', 'sites'})
            if not hasattr(self, '_additionalProperties'):
                super(InsightModelDataDiagnosisModifier, self).__setattr__('_additionalProperties', set())
            if name not in properties:
                self._additionalProperties.add(name)
            super(InsightModelDataDiagnosisModifier, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Diagnosis Modifier object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelDataNormality(object):
    """
    InsightModelData Normality.
    :attr InsightModelDataNormalityUsage usage: (optional)
    :attr list[InsightModelDataEvidence] evidence: (optional)
    :attr float directly_affected_score: (optional)
    """

    def __init__(self, usage=None, evidence=None, directly_affected_score=None, **kwargs):
        """
        Initialize an InsightModelData Normality object.
        :param InsightModelDataNormalityUsage usage: (optional)
        :param list[InsightModelDataEvidence] evidence: (optional)
        :param float directly_affected_score: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.usage = usage
        self.evidence = evidence
        self.directly_affected_score = directly_affected_score
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData Normality object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'usage' in _dict:
            args['usage'] = InsightModelDataNormalityUsage._from_dict(_dict['usage'])
            del xtra['usage']
        if 'evidence' in _dict:
            args['evidence'] = [InsightModelDataEvidence._from_dict(entry) for entry in _dict['evidence']]
            del xtra['evidence']
        if 'directlyAffectedScore' in _dict:
            args['directly_affected_score'] = _dict['directlyAffectedScore']
            del xtra['directlyAffectedScore']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InsightModelData Normality object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'usage') and self.usage is not None:
            _dict['usage'] = self.usage._to_dict()
        if hasattr(self, 'evidence') and self.evidence is not None:
            _dict['evidence'] = [entry._to_dict() for entry in self.evidence]
        if hasattr(self, 'directly_affected_score') and self.directly_affected_score is not None:
            _dict['directlyAffectedScore'] = self.directly_affected_score
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
            properties = ({'usage', 'evidence', 'directly_affected_score'})
            if not hasattr(self, '_additionalProperties'):
                super(InsightModelDataNormality, self).__setattr__('_additionalProperties', set())
            if name not in properties:
                self._additionalProperties.add(name)
            super(InsightModelDataNormality, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData Normality object."""
        return json.dumps(self._to_dict(), indent=2)

class InsightModelData(object):
    """
    InsightModelData.
    :attr InsightModelDataMedication medication: (optional)
    :attr InsightModelDataProcedure procedure: (optional)
    :attr InsightModelDataDiagnosis diagnosis: (optional)
    :attr InsightModelDataNormality normality: (optional)
    """

    def __init__(self, medication=None, procedure=None, diagnosis=None, normality=None, **kwargs):
        """
        Initialize an InsightModelData object.
        :param InsightModelDataMedication medication: (optional)
        :param InsightModelDataProcedure procedure: (optional)
        :param InsightModelDataDiagnosis diagnosis: (optional)
        :param InsightModelDataNormality normality: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.medication = medication
        self.procedure = procedure
        self.diagnosis = diagnosis
        self.normality = normality
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an InsightModelData object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'medication' in _dict:
            args['medication'] = InsightModelDataMedication._from_dict(_dict['medication'])
            del xtra['medication']
        if 'procedure' in _dict:
            args['procedure'] = InsightModelDataProcedure._from_dict(_dict['procedure'])
            del xtra['procedure']
        if 'diagnosis' in _dict:
            args['diagnosis'] = InsightModelDataDiagnosis._from_dict(_dict['diagnosis'])
            del xtra['diagnosis']
        if 'normality' in _dict:
            args['normality'] = InsightModelDataNormality._from_dict(_dict['normality'])
            del xtra['normality']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize an InsightModelData object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'medication') and self.medication is not None:
            _dict['medication'] = self.medication._to_dict()
        if hasattr(self, 'procedure') and self.procedure is not None:
            _dict['procedure'] = self.procedure._to_dict()
        if hasattr(self, 'diagnosis') and self.diagnosis is not None:
            _dict['diagnosis'] = self.diagnosis._to_dict()
        if hasattr(self, 'normality') and self.normality is not None:
            _dict['normality'] = self.normality._to_dict()
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'medication', 'procedure', 'diagnosis', 'normality'})
        if not hasattr(self, '_additionalProperties'):
            super(InsightModelData, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InsightModelData, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InsightModelData object."""
        return json.dumps(self._to_dict(), indent=2)

class LabValueAnnotation(object):
    """
    LabValueAnnotation.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str loinc_id: (optional)
    :attr str low_value: (optional)
    :attr str date_in_milliseconds: (optional)
    :attr str lab_type_surface_form: (optional)
    :attr str lab_type_normalized_name: (optional)
    :attr str lab_value: (optional)
    :attr str section_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, loinc_id=None, low_value=None, date_in_milliseconds=None,
                 lab_type_surface_form=None, lab_type_normalized_name=None, lab_value=None,
                 section_normalized_name=None, section_surface_form=None, **kwargs):
        """
        Initialize a LabValueAnnotation object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str loinc_id: (optional)
        :param str low_value: (optional)
        :param str date_in_milliseconds: (optional)
        :param str lab_type_surface_form: (optional)
        :param str lab_type_normalized_name: (optional)
        :param str lab_value: (optional)
        :param str section_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.loinc_id = loinc_id
        self.low_value = low_value
        self.date_in_milliseconds = date_in_milliseconds
        self.lab_type_surface_form = lab_type_surface_form
        self.lab_type_normalized_name = lab_type_normalized_name
        self.lab_value = lab_value
        self.section_normalized_name = section_normalized_name
        self.section_surface_form = section_surface_form
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a LabValueAnnotation object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'loincId' in _dict:
            args['loinc_id'] = _dict['loincId']
            del xtra['loincId']
        if 'lowValue' in _dict:
            args['low_value'] = _dict['lowValue']
            del xtra['lowValue']
        if 'dateInMilliseconds' in _dict:
            args['date_in_milliseconds'] = _dict['dateInMilliseconds']
            del xtra['dateInMilliseconds']
        if 'labTypeSurfaceForm' in _dict:
            args['lab_type_surface_form'] = _dict['labTypeSurfaceForm']
            del xtra['labTypeSurfaceForm']
        if 'labTypeNormalizedName' in _dict:
            args['lab_type_normalized_name'] = _dict['labTypeNormalizedName']
            del xtra['labTypeNormalizedName']
        if 'labValue' in _dict:
            args['lab_value'] = _dict['labValue']
            del xtra['labValue']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a LabValueAnnotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'loinc_id') and self.loinc_id is not None:
            _dict['loincId'] = self.loinc_id
        if hasattr(self, 'low_value') and self.low_value is not None:
            _dict['lowValue'] = self.low_value
        if hasattr(self, 'date_in_milliseconds') and self.date_in_milliseconds is not None:
            _dict['dateInMilliseconds'] = self.date_in_milliseconds
        if hasattr(self, 'lab_type_surface_form') and self.lab_type_surface_form is not None:
            _dict['labTypeSurfaceForm'] = self.lab_type_surface_form
        if hasattr(self, 'lab_type_normalized_name') and self.lab_type_normalized_name is not None:
            _dict['labTypeNormalizedName'] = self.lab_type_normalized_name
        if hasattr(self, 'lab_value') and self.lab_value is not None:
            _dict['labValue'] = self.lab_value
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical',
                       'loinc_id', 'low_value', 'date_in_milliseconds', 'lab_type_surface_form',
                       'lab_type_normalized_name', 'lab_value', 'section_normalized_name', 'section_surface_form'})
        if not hasattr(self, '_additionalProperties'):
            super(LabValueAnnotation, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(LabValueAnnotation, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this LabValueAnnotation object."""
        return json.dumps(self._to_dict(), indent=2)


class ListStringWrapper():
    """
    ListStringWrapper.

    :attr List[str] data: (optional)
    """

    def __init__(self, *, data: List[str] = None) -> None:
        """
        Initialize a ListStringWrapper object.

        :param List[str] data: (optional)
        """
        self.data = data

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ListStringWrapper':
        """Initialize a ListStringWrapper object from a json dictionary."""
        args = {}
        if 'data' in _dict:
            args['data'] = _dict.get('data')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ListStringWrapper object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data') and self.data is not None:
            _dict['data'] = self.data
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ListStringWrapper object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ListStringWrapper') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ListStringWrapper') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class MedicationAnnotation(object):
    """
    MedicationAnnotation.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str section_normalized_name: (optional)
    :attr str cui: (optional)
    :attr list[object] drug: (optional)
    :attr str section_surface_form: (optional)
    :attr InsightModelData insight_model_data: (optional)
    :attr list[Temporal] temporal: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, section_normalized_name=None, cui=None, drug=None, section_surface_form=None,
                 insight_model_data=None, temporal=None, **kwargs):
        """
        Initialize a MedicationAnnotation object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str section_normalized_name: (optional)
        :param str cui: (optional)
        :param list[object] drug: (optional)
        :param str section_surface_form: (optional)
        :param InsightModelData insight_model_data: (optional)
        :param list[Temporal] temporal: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.section_normalized_name = section_normalized_name
        self.cui = cui
        self.drug = drug
        self.section_surface_form = section_surface_form
        self.insight_model_data = insight_model_data
        self.temporal = temporal
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a MedicationAnnotation object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'cui' in _dict:
            args['cui'] = _dict['cui']
            del xtra['cui']
        if 'drug' in _dict:
            args['drug'] = _dict['drug']
            del xtra['drug']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'insightModelData' in _dict:
            args['insight_model_data'] = InsightModelData._from_dict(_dict['insightModelData'])
            del xtra['insightModelData']
        if 'temporal' in _dict:
            args['temporal'] = [Temporal._from_dict(entry) for entry in _dict['temporal']]
            del xtra['temporal']
        
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MedicationAnnotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'drug') and self.drug is not None:
            _dict['drug'] = self.drug
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'insight_model_data') and self.insight_model_data is not None:
            _dict['insightModelData'] = self.insight_model_data._to_dict()
        if hasattr(self, 'temporal') and self.temporal is not None:
            _dict['temporal'] = [entry._to_dict() for entry in self.temporal]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical',
                       'section_normalized_name', 'cui', 'drug', 'section_surface_form', 
                       'insight_model_data', 'temporal'})
        if not hasattr(self, '_additionalProperties'):
            super(MedicationAnnotation, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(MedicationAnnotation, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this MedicationAnnotation object."""
        return json.dumps(self._to_dict(), indent=2)


class NegatedSpan(object):
    """
    NegatedSpan.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr object trigger: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, trigger=None, **kwargs):
        """
        Initialize a NegatedSpan object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param object trigger: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.trigger = trigger
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a NegatedSpan object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'trigger' in _dict:
            args['trigger'] = _dict['trigger']
            del xtra['trigger']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a NegationAnnotation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'trigger') and self.trigger is not None:
            _dict['trigger'] = self.trigger
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'trigger'}
        if not hasattr(self, '_additionalProperties'):
            super(NegatedSpan, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(NegatedSpan, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this NegatedSpan object."""
        return json.dumps(self._to_dict(), indent=2)


class NluEntities(object):
    """
    NLU Entities.
    :attr int begin: (optional)
    :attr str covered_text: (optional)
    :attr int end: (optional)
    :attr str type: (optional)
    :attr str source: (optional)
    :attr float relevance: (optional)
    :attr int uid
    """

    def __init__(self, begin=None, covered_text=None, end=None, type=None, source=None, relevance=None,
                 uid=None, **kwargs):
        """
        Initialize an NLU Entities object.
        :param int begin: (optional)
        :param str covered_text: (optional)
        :param int end: (optional)
        :param str type: (optional)
        :param str source: (optional)
        :param float relevance: (optional)
        :param int uid: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.begin = begin
        self.covered_text = covered_text
        self.end = end
        self.type = type
        self.source = source
        self.relevance = relevance
        self.uid = uid
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an NLU Entities object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'source' in _dict:
            args['source'] = _dict['source']
            del xtra['source']
        if 'relevance' in _dict:
            args['relevance'] = _dict['relevance']
            del xtra['relevance']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a NluEntities object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'relevance') and self.relevance is not None:
            _dict['relevance'] = self.relevance
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'begin', 'covered_text', 'end', 'type', 'source', 'relevance', 'uid'}
        if not hasattr(self, '_additionalProperties'):
            super(NluEntities, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(NluEntities, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this NluEntities object."""
        return json.dumps(self._to_dict(), indent=2)

class NodeEntity(object):
    """
    NLU Relations Node Entity.
    :attr int uid: (optional)
    """

    def __init__(self, uid, **kwargs):
        """
        Initialize a NLU Relations Node Entity object.
        :param int uid: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.uid = uid
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an NLU Relations Node Entity object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a NodeEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'uid'}
        if not hasattr(self, '_additionalProperties'):
            super(Node, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Node, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this NLU Relations Node Entity object."""
        return json.dumps(self._to_dict(), indent=2)

class Node(object):
    """
    NLU Relations Node.
    :attr NodeEntity entity: (optional)
    """

    def __init__(self, entity, **kwargs):
        """
        Initialize a NLU Relations Node object.
        :param NodeEntity entity: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.entity = entity
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an NLU Relations Node  object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'entity' in _dict:
            args['entity'] = _dict['entity']
            del xtra['entity']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Node object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'entity'}
        if not hasattr(self, '_additionalProperties'):
            super(Node, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Node, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this NLU Relations Node object."""
        return json.dumps(self._to_dict(), indent=2)


class Procedure(object):
    """
    Procedure.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str cui: (optional)
    :attr str section_normalized_name: (optional)
    :attr str date_in_milliseconds: (optional)
    :attr str snomed_concept_id: (optional)
    :attr str procedure_surface_form: (optional)
    :attr str procedure_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    :attr Disambiguation disambiguation_data: (optional)
    :attr InsightModelData insight_model_data: (optional)
    :attr list[Temporal] temporal: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, cui=None, section_normalized_name=None, date_in_milliseconds=None,
                 snomed_concept_id=None, procedure_surface_form=None, procedure_normalized_name=None,
                 section_surface_form=None, disambiguation_data=None, insight_model_data=None, 
                 temporal=None, **kwargs):
        """
        Initialize a Procedure object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str cui: (optional)
        :param str section_normalized_name: (optional)
        :param str date_in_milliseconds: (optional)
        :param str snomed_concept_id: (optional)
        :param str procedure_surface_form: (optional)
        :param str procedure_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param Disambiguation disambiguation_data: (optional)
        :param InsightModelData insight_model_data: (optional)
        :param list[Temporal] temporal: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.cui = cui
        self.section_normalized_name = section_normalized_name
        self.date_in_milliseconds = date_in_milliseconds
        self.snomed_concept_id = snomed_concept_id
        self.procedure_surface_form = procedure_surface_form
        self.procedure_normalized_name = procedure_normalized_name
        self.section_surface_form = section_surface_form
        self.disambiguation_data = disambiguation_data
        self.insight_model_data = insight_model_data
        self.temporal = temporal
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Procedure object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'cui' in _dict:
            args['cui'] = _dict['cui']
            del xtra['cui']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'dateInMilliseconds' in _dict:
            args['date_in_milliseconds'] = _dict['dateInMilliseconds']
            del xtra['dateInMilliseconds']
        if 'snomedConceptId' in _dict:
            args['snomed_concept_id'] = _dict['snomedConceptId']
            del xtra['snomedConceptId']
        if 'procedureSurfaceForm' in _dict:
            args['procedure_surface_form'] = _dict['procedureSurfaceForm']
            del xtra['procedureSurfaceForm']
        if 'procedureNormalizedName' in _dict:
            args['procedure_normalized_name'] = _dict['procedureNormalizedName']
            del xtra['procedureNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'disambiguationData' in _dict:
            args['disambiguation_data'] = Disambiguation._from_dict(_dict['disambiguationData'])
            del xtra['disambiguationData']
        if 'insightModelData' in _dict:
            args['insight_model_data'] = InsightModelData._from_dict(_dict['insightModelData'])
            del xtra['insightModelData']
        if 'temporal' in _dict:
            args['temporal'] = [Temporal._from_dict(entry) for entry in _dict['temporal']]
            del xtra['temporal']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Procedure object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'date_in_milliseconds') and self.date_in_milliseconds is not None:
            _dict['dateInMilliseconds'] = self.date_in_milliseconds
        if hasattr(self, 'snomed_concept_id') and self.snomed_concept_id is not None:
            _dict['snomedConceptId'] = self.snomed_concept_id
        if hasattr(self, 'procedure_surface_form') and self.procedure_surface_form is not None:
            _dict['procedureSurfaceForm'] = self.procedure_surface_form
        if hasattr(self, 'procedure_normalized_name') and self.procedure_normalized_name is not None:
            _dict['procedureNormalizedName'] = self.procedure_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'disambiguation_data') and self.disambiguation_data is not None:
            _dict['disambiguationData'] = self.disambiguation_data._to_dict()
        if hasattr(self, 'insight_model_data') and self.insight_model_data is not None:
            _dict['insightModelData'] = self.insight_model_data._to_dict()
        if hasattr(self, 'temporal') and self.temporal is not None:
            _dict['temporal'] = [entry._to_dict() for entry in self.temporal]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'cui',
                       'section_normalized_name', 'date_in_milliseconds', 'snomed_concept_id', 'procedure_surface_form',
                       'procedure_normalized_name', 'section_surface_form', 'disambiguation_data', 'insight_model_data',
                       'temporal'})
        if not hasattr(self, '_additionalProperties'):
            super(Procedure, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Procedure, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Procedure object."""
        return json.dumps(self._to_dict(), indent=2)


class Relations(object):
    """
    NLU Relations.
    :attr str source: (optional)
    :attr float score: (optional)
    :attr list[Node] nodes: (optional)
    :attr str type: (optional)
    """

    def __init__(self, source=None, score=None, nodes=None, type=None, **kwargs):
        """
        Initialize an NLU Relations object.
        :param str source: (optional)
        :param float score: (optional)
        :param list[Node] nodes: (optional)
        :param str type: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.source = source
        self.score = score
        self.nodes = nodes
        self.type = type
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize an NLU Relations object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'source' in _dict:
            args['source'] = _dict['source']
            del xtra['source']
        if 'score' in _dict:
            args['score'] = _dict['score']
            del xtra['score']
        if 'nodes' in _dict:
            args['nodes'] = [Node._from_dict(entry) for entry in _dict['nodes']]
            del xtra['nodes']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Relations object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'score') and self.score is not None:
            _dict['score'] = self.score
        if hasattr(self, 'nodes') and self.nodes is not None:
            _dict['nodes'] = [entry._to_dict() for entry in self.nodes]
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'source', 'score', 'nodes', 'type'}
        if not hasattr(self, '_additionalProperties'):
            super(Relations, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Relations, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Relations object."""
        return json.dumps(self._to_dict(), indent=2)


class RequestContainer(object):
    """
    RequestContainer.
    :attr list[UnstructuredContainer] unstructured: (optional)
    :attr list[AnnotatorFlow] annotator_flows: (optional)
    """

    def __init__(self, unstructured=None, annotator_flows=None):
        """
        Initialize a RequestContainer object.
        :param list[UnstructuredContainer] unstructured: (optional)
        :param list[AnnotatorFlow] annotator_flows: (optional)
        """
        self.unstructured = unstructured
        self.annotator_flows = annotator_flows

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a RequestContainer object from a json dictionary."""
        args = {}
        if 'unstructured' in _dict:
            args['unstructured'] = [UnstructuredContainer._from_dict(x) for x in _dict['unstructured']]
        if 'annotatorFlows' in _dict:
            args['annotator_flows'] = [AnnotatorFlow._from_dict(x) for x in _dict['annotatorFlows']]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RequestContainer object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'unstructured') and self.unstructured is not None:
            _dict['unstructured'] = [x._to_dict() for x in self.unstructured]
        if hasattr(self, 'annotator_flows') and self.annotator_flows is not None:
            _dict['annotatorFlows'] = [x._to_dict() for x in self.annotator_flows]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this RequestContainer object."""
        return json.dumps(self._to_dict(), indent=2)


class SectionTrigger(object):
    """
    SectionTrigger.
    :attr int begin: (optional)
    :attr str covered_text: (optional)
    :attr int end: (optional)
    :attr str section_normalized_name: (optional)
    :attr str source: (optional)
    :attr str type: (optional)
    """

    def __init__(self, begin=None, covered_text=None, end=None, section_normalized_name=None, source=None,
                 type=None, **kwargs):
        """
        Initialize a SectionTrigger object.
        :param int begin: (optional)
        :param str covered_text: (optional)
        :param int end: (optional)
        :param str section_normalized_name: (optional)
        :param str source: (optional)
        :param str type: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.begin = begin
        self.covered_text = covered_text
        self.end = end
        self.section_normalized_name = section_normalized_name
        self.source = source
        self.type = type
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a SectionTrigger object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'source' in _dict:
            args['source'] = _dict['source']
            del xtra['source']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SectionTrigger object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'begin', 'covered_text', 'end', 'section_normalized_name', 'source', 'type'}
        if not hasattr(self, '_additionalProperties'):
            super(SectionTrigger, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(SectionTrigger, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this SectionTrigger object."""
        return json.dumps(self._to_dict(), indent=2)


class Section(object):
    """
    Section.
    :attr int begin: (optional)
    :attr str covered_text: (optional)
    :attr int end: (optional)
    :attr str type: (optional)
    :attr str section_type: (optional)
    :attr SectionTrigger trigger: (optional)
    """

    def __init__(self, begin=None, covered_text=None, end=None, type=None, section_type=None, trigger=None, **kwargs):
        """
        Initialize a Section object.
        :param int begin: (optional)
        :param str covered_text: (optional)
        :param int end: (optional)
        :param str type: (optional)
        :param str section_type: (optional)
        :param SectionTrigger trigger: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.begin = begin
        self.covered_text = covered_text
        self.end = end
        self.type = type
        self.section_type = section_type
        self.trigger = trigger
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Section object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'sectionType' in _dict:
            args['section_type'] = _dict['sectionType']
            del xtra['sectionType']
        if 'trigger' in _dict:
            args['trigger'] = SectionTrigger._from_dict(_dict['trigger'])
            del xtra['trigger']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Section object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'section_type') and self.section_type is not None:
            _dict['sectionType'] = self.section_type
        if hasattr(self, 'trigger') and self.trigger is not None:
            _dict['trigger'] = self.trigger._to_dict()
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'begin', 'covered_text', 'end', 'type', 'section_type', 'trigger'}
        if not hasattr(self, '_additionalProperties'):
            super(Section, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Section, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Section object."""
        return json.dumps(self._to_dict(), indent=2)


class ServiceError():
    """
    Object representing an HTTP response with an error.

    :attr int code: (optional) respone code.
    :attr str message: (optional) response error message.
    :attr str level: (optional) error severity level.
    :attr str description: (optional) error description.
    :attr str more_info: (optional) additional error information.
    :attr str correlation_id: (optional) error message correlation identifier.
    :attr str artifact: (optional)
    :attr str href: (optional)
    """

    def __init__(self, *, code: int = None, message: str = None, level: str = None, description: str = None, more_info: str = None, correlation_id: str = None, artifact: str = None, href: str = None) -> None:
        """
        Initialize a ServiceError object.

        :param int code: (optional) respone code.
        :param str message: (optional) response error message.
        :param str level: (optional) error severity level.
        :param str description: (optional) error description.
        :param str more_info: (optional) additional error information.
        :param str correlation_id: (optional) error message correlation identifier.
        :param str artifact: (optional)
        :param str href: (optional)
        """
        self.code = code
        self.message = message
        self.level = level
        self.description = description
        self.more_info = more_info
        self.correlation_id = correlation_id
        self.artifact = artifact
        self.href = href

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ServiceError':
        """Initialize a ServiceError object from a json dictionary."""
        args = {}
        if 'code' in _dict:
            args['code'] = _dict.get('code')
        if 'message' in _dict:
            args['message'] = _dict.get('message')
        if 'level' in _dict:
            args['level'] = _dict.get('level')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'moreInfo' in _dict:
            args['more_info'] = _dict.get('moreInfo')
        if 'correlationId' in _dict:
            args['correlation_id'] = _dict.get('correlationId')
        if 'artifact' in _dict:
            args['artifact'] = _dict.get('artifact')
        if 'href' in _dict:
            args['href'] = _dict.get('href')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ServiceError object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'code') and self.code is not None:
            _dict['code'] = self.code
        if hasattr(self, 'message') and self.message is not None:
            _dict['message'] = self.message
        if hasattr(self, 'level') and self.level is not None:
            _dict['level'] = self.level
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'more_info') and self.more_info is not None:
            _dict['moreInfo'] = self.more_info
        if hasattr(self, 'correlation_id') and self.correlation_id is not None:
            _dict['correlationId'] = self.correlation_id
        if hasattr(self, 'artifact') and self.artifact is not None:
            _dict['artifact'] = self.artifact
        if hasattr(self, 'href') and self.href is not None:
            _dict['href'] = self.href
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ServiceError object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ServiceError') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ServiceError') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


    class LevelEnum(Enum):
        """
        error severity level.
        """
        ERROR = "ERROR"
        WARNING = "WARNING"
        INFO = "INFO"


class ServiceStatus():
    """
    Object representing service runtime status.

    :attr str service_state: (optional) scurrent service state.
    :attr str state_details: (optional) service state details.
    """

    def __init__(self, *, service_state: str = None, state_details: str = None) -> None:
        """
        Initialize a ServiceStatus object.

        :param str service_state: (optional) scurrent service state.
        :param str state_details: (optional) service state details.
        """
        self.service_state = service_state
        self.state_details = state_details

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ServiceStatus':
        """Initialize a ServiceStatus object from a json dictionary."""
        args = {}
        if 'serviceState' in _dict:
            args['service_state'] = _dict.get('serviceState')
        if 'stateDetails' in _dict:
            args['state_details'] = _dict.get('stateDetails')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ServiceStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'service_state') and self.service_state is not None:
            _dict['serviceState'] = self.service_state
        if hasattr(self, 'state_details') and self.state_details is not None:
            _dict['stateDetails'] = self.state_details
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ServiceStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ServiceStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ServiceStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


    class ServiceStateEnum(Enum):
        """
        scurrent service state.
        """
        OK = "OK"
        WARNING = "WARNING"
        ERROR = "ERROR"


class Smoking(object):
    """
    Smoking.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str participation: (optional)
    :attr str section_normalized_name: (optional)
    :attr str modality: (optional)
    :attr str current: (optional)
    :attr str smoke_term_surface_form: (optional)
    :attr str smoke_term_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, participation=None, section_normalized_name=None, modality=None, current=None,
                 smoke_term_surface_form=None, smoke_term_normalized_name=None, section_surface_form=None, **kwargs):
        """
        Initialize a Smoking object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str participation: (optional)
        :param str section_normalized_name: (optional)
        :param str modality: (optional)
        :param str current: (optional)
        :param str smoke_term_surface_form: (optional)
        :param str smoke_term_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.participation = participation
        self.section_normalized_name = section_normalized_name
        self.modality = modality
        self.current = current
        self.smoke_term_surface_form = smoke_term_surface_form
        self.smoke_term_normalized_name = smoke_term_normalized_name
        self.section_surface_form = section_surface_form
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Smoking object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'participation' in _dict:
            args['participation'] = _dict['participation']
            del xtra['participation']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'modality' in _dict:
            args['modality'] = _dict['modality']
            del xtra['modality']
        if 'current' in _dict:
            args['current'] = _dict['current']
            del xtra['current']
        if 'smokeTermSurfaceForm' in _dict:
            args['smoke_term_surface_form'] = _dict['smokeTermSurfaceForm']
            del xtra['smokeTermSurfaceForm']
        if 'smokeTermNormalizedName' in _dict:
            args['smoke_term_normalized_name'] = _dict['smokeTermNormalizedName']
            del xtra['smokeTermNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Smoking object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'participation') and self.participation is not None:
            _dict['participation'] = self.participation
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'modality') and self.modality is not None:
            _dict['modality'] = self.modality
        if hasattr(self, 'current') and self.current is not None:
            _dict['current'] = self.current
        if hasattr(self, 'smoke_term_surface_form') and self.smoke_term_surface_form is not None:
            _dict['smokeTermSurfaceForm'] = self.smoke_term_surface_form
        if hasattr(self, 'smoke_term_normalized_name') and self.smoke_term_normalized_name is not None:
            _dict['smokeTermNormalizedName'] = self.smoke_term_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical',
                       'participation', 'section_normalized_name', 'modality', 'current',
                       'smoke_term_surface_form', 'smoke_term_normalized_name', 'section_surface_form'})
        if not hasattr(self, '_additionalProperties'):
            super(Smoking, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Smoking, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Smoking object."""
        return json.dumps(self._to_dict(), indent=2)


class SpellingCorrection(object):
    """
    Spelling Correction.
    :attr int begin:
    :attr int end:
    :attr str covered_text:
    :attr list[Suggestion] suggestions
    """
    def __init__(self, begin=None, end=None, covered_text=None, suggestions=None, **kwargs):
        """
        Initializes a spelling correction
        :param int begin:
        :param int end:
        :param str covered_text:
        :param list[Suggestion] suggestions:
        """
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.suggestions = suggestions
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a SpellingCorrection object from a json dictionary."""
        args = {}
        xtra = _dict.copy()

        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'suggestions' in _dict:
            args['suggestions'] = [Suggestion._from_dict(entry) for entry in _dict['suggestions']]
            del xtra['suggestions']

        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SpellingCorrection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this spelling correction model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'suggestions') and self.suggestions is not None:
            _dict['suggestions'] = [entry._to_dict() for entry in self.suggestions]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'begin', 'end', 'covered_text', 'suggestions'}
        if not hasattr(self, '_additionalProperties'):
            super(SpellingCorrection, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(SpellingCorrection, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Spelling Correction object."""
        return json.dumps(self._to_dict(), indent=2)


class SpellCorrectedText(object):
    """
    :attr str corrected_text
    :attr str debug_text: (optional)
    """
    def __init__(self, corrected_text=None, debug_text=None, **kwargs):
        """
        Initializes a Spell corrected text
        :param str corrected_text
        :param str debug_text: (optional)
        """
        self.corrected_text = corrected_text
        self.debug_text = debug_text
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a spelling corrected text object from a json dictionary."""
        args = {}
        xtra = _dict.copy()

        if 'correctedText' in _dict:
            args['corrected_text'] = _dict['correctedText']
            del xtra['correctedText']
        if 'debugText' in _dict:
            args['debug_text'] = _dict['debugText']
            del xtra['debugText']

        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SpellCorrectedText object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this spell corrected text"""
        _dict = {}
        if hasattr(self, 'corrected_text') and self.corrected_text is not None:
            _dict['correctedText'] = self.corrected_text
        if hasattr(self, 'debug_text') and self.debug_text is not None:
            _dict['debugText'] = self.debug_text

        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'corrected_text', 'debug_text'}
        if not hasattr(self, '_additionalProperties'):
            super(SpellCorrectedText, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(SpellCorrectedText, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this spelling suggestion object."""
        return json.dumps(self._to_dict(), indent=2)


class Suggestion(object):
    """
    :attr str text
    :attr float confidence
    :attr bool applied
    :attr list[str] semtypes: (optional)
    """

    def __init__(self, text=None, confidence=None, applied=None, semtypes=None, **kwargs):
        """
        Initializes a spelling suggestion
        :param str text
        :param float confidence
        :param bool applied
        :param list[str] semtypes: (optional)
        """
        self.text = text
        self.confidence = confidence
        self.applied = applied
        self.semtypes = semtypes
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a spelling suggestion object from a json dictionary."""
        args = {}
        xtra = _dict.copy()

        if 'text' in _dict:
            args['text'] = _dict['text']
            del xtra['text']
        if 'confidence' in _dict:
            args['confidence'] = _dict['confidence']
            del xtra['confidence']
        if 'applied' in _dict:
            args['applied'] = _dict['applied']
            del xtra['applied']
        if 'semtypes' in _dict:
            args['semtypes'] = _dict['semtypes']
            del xtra['semtypes']

        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Suggestion object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this spelling suggestion."""
        _dict = {}
        if hasattr(self, 'text') and self.text is not None:
            _dict['text'] = self.text
        if hasattr(self, 'confidence') and self.confidence is not None:
            _dict['confidence'] = self.confidence
        if hasattr(self, 'applied') and self.applied is not None:
            _dict['applied'] = self.applied
        if hasattr(self, 'semtypes') and self.semtypes is not None:
            _dict['semtypes'] = self.semtypes
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'text', 'confidence', 'applied', 'semtypes'}
        if not hasattr(self, '_additionalProperties'):
            super(Suggestion, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Suggestion, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this spelling suggestion object."""
        return json.dumps(self._to_dict(), indent=2)


class SymptomDisease(object):
    """
    SymptomDisease.
    :attr str id: (optional)
    :attr str type: (optional)
    :attr int uid: (optional)
    :attr int begin: (optional)
    :attr int end: (optional)
    :attr str covered_text: (optional)
    :attr bool negated: (optional)
    :attr bool hypothetical: (optional)
    :attr str cui: (optional)
    :attr str icd10_code: (optional)
    :attr str section_normalized_name: (optional)
    :attr str modality: (optional)
    :attr str symptom_disease_surface_form: (optional)
    :attr str date_in_milliseconds: (optional)
    :attr str snomed_concept_id: (optional)
    :attr str ccs_code: (optional)
    :attr str symptom_disease_normalized_name: (optional)
    :attr str section_surface_form: (optional)
    :attr str icd9_code: (optional)
    :attr str hcc_code: (optional)
    :attr Disambiguation disambiguation_data: (optional)
    :attr InsightModelData insight_model_data: (optional)
    :attr list[Temporal] temporal: (optional)
    """

    def __init__(self, id=None, type=None, uid=None, begin=None, end=None, covered_text=None, negated=None,
                 hypothetical=None, cui=None, icd10_code=None, section_normalized_name=None, modality=None,
                 symptom_disease_surface_form=None, date_in_milliseconds=None, snomed_concept_id=None, ccs_code=None,
                 symptom_disease_normalized_name=None, section_surface_form=None, icd9_code=None, hcc_code=None,
                 disambiguation_data=None, insight_model_data=None, temporal=None, **kwargs):
        """
        Initialize a SymptomDisease object.
        :param str id: (optional)
        :param str type: (optional)
        :param int uid: (optional)
        :param int begin: (optional)
        :param int end: (optional)
        :param str covered_text: (optional)
        :param bool negated: (optional)
        :param bool hypothetical: (optional)
        :param str cui: (optional)
        :param str icd10_code: (optional)
        :param str section_normalized_name: (optional)
        :param str modality: (optional)
        :param str symptom_disease_surface_form: (optional)
        :param str date_in_milliseconds: (optional)
        :param str snomed_concept_id: (optional)
        :param str ccs_code: (optional)
        :param str symptom_disease_normalized_name: (optional)
        :param str section_surface_form: (optional)
        :param str icd9_code: (optional)
        :param str hcc_code: (optional)
        :param Disambiguation disambiguation_data: (optional)
        :param InsightModelData insight_model_data: (optional)
        :param list[Temporal] temporal: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        self.id = id
        self.type = type
        self.uid = uid
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.negated = negated
        self.hypothetical = hypothetical
        self.cui = cui
        self.icd10_code = icd10_code
        self.section_normalized_name = section_normalized_name
        self.modality = modality
        self.symptom_disease_surface_form = symptom_disease_surface_form
        self.date_in_milliseconds = date_in_milliseconds
        self.snomed_concept_id = snomed_concept_id
        self.ccs_code = ccs_code
        self.symptom_disease_normalized_name = symptom_disease_normalized_name
        self.section_surface_form = section_surface_form
        self.icd9_code = icd9_code
        self.hcc_code = hcc_code
        self.disambiguation_data = disambiguation_data
        self.insight_model_data = insight_model_data
        self.temporal = temporal
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a SymptomDisease object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'id' in _dict:
            args['id'] = _dict['id']
            del xtra['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
            del xtra['type']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
            del xtra['uid']
        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'negated' in _dict:
            args['negated'] = _dict['negated']
            del xtra['negated']
        if 'hypothetical' in _dict:
            args['hypothetical'] = _dict['hypothetical']
            del xtra['hypothetical']
        if 'cui' in _dict:
            args['cui'] = _dict['cui']
            del xtra['cui']
        if 'icd10Code' in _dict:
            args['icd10_code'] = _dict['icd10Code']
            del xtra['icd10Code']
        if 'sectionNormalizedName' in _dict:
            args['section_normalized_name'] = _dict['sectionNormalizedName']
            del xtra['sectionNormalizedName']
        if 'modality' in _dict:
            args['modality'] = _dict['modality']
            del xtra['modality']
        if 'symptomDiseaseSurfaceForm' in _dict:
            args['symptom_disease_surface_form'] = _dict['symptomDiseaseSurfaceForm']
            del xtra['symptomDiseaseSurfaceForm']
        if 'dateInMilliseconds' in _dict:
            args['date_in_milliseconds'] = _dict['dateInMilliseconds']
            del xtra['dateInMilliseconds']
        if 'snomedConceptId' in _dict:
            args['snomed_concept_id'] = _dict['snomedConceptId']
            del xtra['snomedConceptId']
        if 'ccsCode' in _dict:
            args['ccs_code'] = _dict['ccsCode']
            del xtra['ccsCode']
        if 'symptomDiseaseNormalizedName' in _dict:
            args['symptom_disease_normalized_name'] = _dict['symptomDiseaseNormalizedName']
            del xtra['symptomDiseaseNormalizedName']
        if 'sectionSurfaceForm' in _dict:
            args['section_surface_form'] = _dict['sectionSurfaceForm']
            del xtra['sectionSurfaceForm']
        if 'icd9Code' in _dict:
            args['icd9_code'] = _dict['icd9Code']
            del xtra['icd9Code']
        if 'hccCode' in _dict:
            args['hcc_code'] = _dict['hccCode']
            del xtra['hccCode']
        if 'disambiguationData' in _dict:
            args['disambiguation_data'] = Disambiguation._from_dict(_dict['disambiguationData'])
            del xtra['disambiguationData']
        if 'insightModelData' in _dict:
            args['insight_model_data'] = InsightModelData._from_dict(_dict['insightModelData'])
            del xtra['insightModelData']
        if 'temporal' in _dict:
            args['temporal'] = [Temporal._from_dict(entry) for entry in _dict['temporal']]
            del xtra['temporal']
        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SymptomDisease object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'negated') and self.negated is not None:
            _dict['negated'] = self.negated
        if hasattr(self, 'hypothetical') and self.hypothetical is not None:
            _dict['hypothetical'] = self.hypothetical
        if hasattr(self, 'cui') and self.cui is not None:
            _dict['cui'] = self.cui
        if hasattr(self, 'icd10_code') and self.icd10_code is not None:
            _dict['icd10Code'] = self.icd10_code
        if hasattr(self, 'section_normalized_name') and self.section_normalized_name is not None:
            _dict['sectionNormalizedName'] = self.section_normalized_name
        if hasattr(self, 'modality') and self.modality is not None:
            _dict['modality'] = self.modality
        if hasattr(self, 'symptom_disease_surface_form') and self.symptom_disease_surface_form is not None:
            _dict['symptomDiseaseSurfaceForm'] = self.symptom_disease_surface_form
        if hasattr(self, 'date_in_milliseconds') and self.date_in_milliseconds is not None:
            _dict['dateInMilliseconds'] = self.date_in_milliseconds
        if hasattr(self, 'snomed_concept_id') and self.snomed_concept_id is not None:
            _dict['snomedConceptId'] = self.snomed_concept_id
        if hasattr(self, 'ccs_code') and self.ccs_code is not None:
            _dict['ccsCode'] = self.ccs_code
        if hasattr(self, 'symptom_disease_normalized_name') and self.symptom_disease_normalized_name is not None:
            _dict['symptomDiseaseNormalizedName'] = self.symptom_disease_normalized_name
        if hasattr(self, 'section_surface_form') and self.section_surface_form is not None:
            _dict['sectionSurfaceForm'] = self.section_surface_form
        if hasattr(self, 'icd9_code') and self.icd9_code is not None:
            _dict['icd9Code'] = self.icd9_code
        if hasattr(self, 'hcc_code') and self.hcc_code is not None:
            _dict['hccCode'] = self.hcc_code
        if hasattr(self, 'disambiguation_data') and self.disambiguation_data is not None:
            _dict['disambiguationData'] = self.disambiguation_data._to_dict()
        if hasattr(self, 'insight_model_data') and self.insight_model_data is not None:
            _dict['insightModelData'] = self.insight_model_data._to_dict()
        if hasattr(self, 'temporal') and self.temporal is not None:
            _dict['temporal'] = [entry._to_dict() for entry in self.temporal]
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = ({'id', 'type', 'uid', 'begin', 'end', 'covered_text', 'negated', 'hypothetical', 'cui',
                       'icd10_code', 'section_normalized_name', 'modality', 'symptom_disease_surface_form',
                       'date_in_milliseconds', 'snomed_concept_id', 'ccs_code', 'symptom_disease_normalized_name',
                       'section_surface_form', 'icd9_code', 'hcc_code', 'disambiguation_data', 'insight_model_data',
                       'temporal'})
        if not hasattr(self, '_additionalProperties'):
            super(SymptomDisease, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(SymptomDisease, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this SymptomDisease object."""
        return json.dumps(self._to_dict(), indent=2)


class Temporal(object):
    """
    Temporal.
    :attr int begin:
    :attr int end:
    :attr str covered_text:
    :attr object temporal_type: (optional)
    :attr object relation_types: (optional)
    """
    def __init__(self, begin=None, end=None, covered_text=None, temporal_type=None, relation_types=None, **kwargs):
        """
        Initializes a temporal
        :param int begin:
        :param int end:
        :param str covered_text:
        :param object temporal_type:
        :param object relation_types:
        :param **kwargs: (optional) Any additional properties.
        """
        self.begin = begin
        self.end = end
        self.covered_text = covered_text
        self.temporal_type = temporal_type
        self.relation_types = relation_types 
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a Temporal object from a json dictionary."""
        args = {}
        xtra = _dict.copy()

        if 'begin' in _dict:
            args['begin'] = _dict['begin']
            del xtra['begin']
        if 'end' in _dict:
            args['end'] = _dict['end']
            del xtra['end']
        if 'coveredText' in _dict:
            args['covered_text'] = _dict['coveredText']
            del xtra['coveredText']
        if 'temporalType' in _dict:
            args['temporal_type'] = _dict['temporalType']
            del xtra['temporalType']
        if 'relationTypes' in _dict:
            args['relation_types'] = _dict['relationTypes']
            del xtra['relationTypes']

        args.update(xtra)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Temporal object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this temporal model."""
        _dict = {}
        if hasattr(self, 'begin') and self.begin is not None:
            _dict['begin'] = self.begin
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'covered_text') and self.covered_text is not None:
            _dict['coveredText'] = self.covered_text
        if hasattr(self, 'temporal_type') and self.temporal_type is not None:
            _dict['temporalType'] = self.temporal_type
        if hasattr(self, 'relation_types') and self.relation_types is not None:
            _dict['relationTypes'] = self.relation_types
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __setattr__(self, name, value):
        properties = {'begin', 'end', 'covered_text', 'temporal_type', 'relation_types'}
        if not hasattr(self, '_additionalProperties'):
            super(Temporal, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(Temporal, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this Temporal object."""
        return json.dumps(self._to_dict(), indent=2)


class UnstructuredContainer(object):
    """
    UnstructuredContainer.
    :attr str text: (optional)
    :attr str id: (optional)
    :attr str type: (optional)
    :attr ContainerAnnotation data: (optional)
    :attr dict metadata: (optional)
    :attr int uid: (optional)
    """

    def __init__(self, text=None, id=None, type=None, data=None, metadata=None, uid=None):
        """
        Initialize a UnstructuredContainer object.
        :param str text: (optional)
        :param str id: (optional)
        :param str type: (optional)
        :param ContainerAnnotation data: (optional)
        :param dict metadata: (optional)
        :param int uid: (optional)
        """
        self.text = text
        self.id = id
        self.type = type
        self.data = data
        self.metadata = metadata
        self.uid = uid

    @classmethod
    def from_dict(cls, _dict):
        """Initialize a UnstructuredContainer object from a json dictionary."""
        args = {}
        if 'text' in _dict:
            args['text'] = _dict['text']
        if 'id' in _dict:
            args['id'] = _dict['id']
        if 'type' in _dict:
            args['type'] = _dict['type']
        if 'data' in _dict:
            args['data'] = ContainerAnnotation._from_dict(_dict['data'])
        if 'metadata' in _dict:
            args['metadata'] = _dict['metadata']
        if 'uid' in _dict:
            args['uid'] = _dict['uid']
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UnstructuredContainer object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'text') and self.text is not None:
            _dict['text'] = self.text
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'data') and self.data is not None:
            _dict['data'] = self.data._to_dict()
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self):
        """Return a `str` version of this UnstructuredContainer object."""
        return json.dumps(self._to_dict(), indent=2)
