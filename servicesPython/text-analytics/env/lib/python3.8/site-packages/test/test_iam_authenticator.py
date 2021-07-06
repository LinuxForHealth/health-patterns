# pylint: disable=missing-docstring
import json

import pytest
import responses
import jwt

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def test_iam_authenticator():
    authenticator = IAMAuthenticator(apikey='my_apikey')
    assert authenticator is not None
    assert authenticator.token_manager.url == 'https://iam.cloud.ibm.com'
    assert authenticator.token_manager.client_id is None
    assert authenticator.token_manager.client_secret is None
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None
    assert authenticator.token_manager.apikey == 'my_apikey'
    assert authenticator.token_manager.scope is None

    authenticator.set_client_id_and_secret('tom', 'jerry')
    assert authenticator.token_manager.client_id == 'tom'
    assert authenticator.token_manager.client_secret == 'jerry'

    authenticator.set_scope('scope1 scope2 scope3')
    assert authenticator.token_manager.scope == 'scope1 scope2 scope3'

    with pytest.raises(TypeError) as err:
        authenticator.set_headers('dummy')
    assert str(err.value) == 'headers must be a dictionary'

    authenticator.set_headers({'dummy': 'headers'})
    assert authenticator.token_manager.headers == {'dummy': 'headers'}

    with pytest.raises(TypeError) as err:
        authenticator.set_proxies('dummy')
    assert str(err.value) == 'proxies must be a dictionary'

    authenticator.set_proxies({'dummy': 'proxies'})
    assert authenticator.token_manager.proxies == {'dummy': 'proxies'}

def test_iam_authenticator_with_scope():
    authenticator = IAMAuthenticator(apikey='my_apikey', scope='scope1 scope2')
    assert authenticator is not None
    assert authenticator.token_manager.scope == 'scope1 scope2'


def test_iam_authenticator_validate_failed():
    with pytest.raises(ValueError) as err:
        IAMAuthenticator(None)
    assert str(err.value) == 'The apikey shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        IAMAuthenticator('{apikey}')
    assert str(
        err.value
    ) == 'The apikey shouldn\'t start or end with curly brackets or quotes. '\
         'Please remove any surrounding {, }, or \" characters.'

    with pytest.raises(ValueError) as err:
        IAMAuthenticator('my_apikey', client_id='my_client_id')
    assert str(
        err.value) == 'Both client_id and client_secret should be initialized.'

    with pytest.raises(ValueError) as err:
        IAMAuthenticator('my_apikey', client_secret='my_client_secret')
    assert str(
        err.value) == 'Both client_id and client_secret should be initialized.'


@responses.activate
def test_get_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    access_token_layout = {
        "username": "dummy",
        "role": "Admin",
        "permissions": ["administrator", "manage_catalog"],
        "sub": "admin",
        "iss": "sss",
        "aud": "sss",
        "uid": "sss",
        "iat": 1559324664,
        "exp": 1559324664
    }

    access_token = jwt.encode(
        access_token_layout,
        'secret',
        algorithm='HS256',
        headers={
            'kid': '230498151c214b788dd97f22b85410a5'
        })
    response = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }
    responses.add(
        responses.POST, url=url, body=json.dumps(response), status=200)

    authenticator = IAMAuthenticator('my_apikey')
    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] is not None
