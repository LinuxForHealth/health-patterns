# coding: utf-8

# Copyright 2019 IBM All Rights Reserved.
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

from .authenticators import (Authenticator, BasicAuthenticator, BearerTokenAuthenticator,
                             CloudPakForDataAuthenticator, IAMAuthenticator, NoAuthAuthenticator)
from .utils import read_external_sources

def get_authenticator_from_environment(service_name: str) -> Authenticator:
    """Look for external configuration of authenticator.

    Try to get authenticator from external sources, with the following priority:
    1. Credentials file(ibm-credentials.env)
    2. Environment variables
    3. VCAP Services(Cloud Foundry)

    Args:
        service_name: The service name.

    Returns:
        The authenticator found from service information.
    """
    authenticator = None
    config = read_external_sources(service_name)
    if config:
        authenticator = __construct_authenticator(config)
    return authenticator

def __construct_authenticator(config: dict) -> Authenticator:
    auth_type = config.get('AUTH_TYPE').lower() if config.get('AUTH_TYPE') else 'iam'
    authenticator = None

    if auth_type == 'basic':
        authenticator = BasicAuthenticator(
            username=config.get('USERNAME'),
            password=config.get('PASSWORD'))
    elif auth_type == 'bearertoken':
        authenticator = BearerTokenAuthenticator(
            bearer_token=config.get('BEARER_TOKEN'))
    elif auth_type == 'cp4d':
        authenticator = CloudPakForDataAuthenticator(
            username=config.get('USERNAME'),
            password=config.get('PASSWORD'),
            url=config.get('AUTH_URL'),
            disable_ssl_verification=config.get('AUTH_DISABLE_SSL'))
    elif auth_type == 'iam' and config.get('APIKEY'):
        authenticator = IAMAuthenticator(
            apikey=config.get('APIKEY'),
            url=config.get('AUTH_URL'),
            client_id=config.get('CLIENT_ID'),
            client_secret=config.get('CLIENT_SECRET'),
            disable_ssl_verification=config.get('AUTH_DISABLE_SSL'),
            scope=config.get('SCOPE'))
    elif auth_type == 'noauth':
        authenticator = NoAuthAuthenticator()

    return authenticator
