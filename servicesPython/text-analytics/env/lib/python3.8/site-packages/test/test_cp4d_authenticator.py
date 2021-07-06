# pylint: disable=missing-docstring
import json

import pytest
import responses
import jwt

from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator

def test_iam_authenticator():
    authenticator = CloudPakForDataAuthenticator(
        'my_username', 'my_password', 'http://my_url')
    assert authenticator is not None
    assert authenticator.token_manager.url == 'http://my_url/v1/preauth/validateAuth'
    assert authenticator.token_manager.username == 'my_username'
    assert authenticator.token_manager.password == 'my_password'
    assert authenticator.token_manager.disable_ssl_verification is False
    assert authenticator.token_manager.headers is None
    assert authenticator.token_manager.proxies is None

    authenticator.set_disable_ssl_verification(True)
    assert authenticator.token_manager.disable_ssl_verification is True

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


def test_iam_authenticator_validate_failed():
    with pytest.raises(ValueError) as err:
        CloudPakForDataAuthenticator('my_username', None, 'my_url')
    assert str(err.value) == 'The username and password shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        CloudPakForDataAuthenticator(None, 'my_password', 'my_url')
    assert str(err.value) == 'The username and password shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        CloudPakForDataAuthenticator('my_username', 'my_password', None)
    assert str(err.value) == 'The url shouldn\'t be None.'

    with pytest.raises(ValueError) as err:
        CloudPakForDataAuthenticator('{my_username}', 'my_password', 'my_url')
    assert str(err.value) == 'The username and password shouldn\'t start or end with curly brackets or quotes. '\
                             'Please remove any surrounding {, }, or \" characters.'

    with pytest.raises(ValueError) as err:
        CloudPakForDataAuthenticator('my_username', '{my_password}', 'my_url')
    assert str(err.value) == 'The username and password shouldn\'t start or end with curly brackets or quotes. '\
                             'Please remove any surrounding {, }, or \" characters.'

    with pytest.raises(ValueError) as err:
        CloudPakForDataAuthenticator('my_username', 'my_password', '{my_url}')
    assert str(err.value) == 'The url shouldn\'t start or end with curly brackets or quotes. '\
                             'Please remove any surrounding {, }, or \" characters.'


@responses.activate
def test_get_token():
    url = "https://test"
    access_token_layout = {
        "username": "dummy",
        "role": "Admin",
        "permissions": [
            "administrator",
            "manage_catalog"
        ],
        "sub": "admin",
        "iss": "sss",
        "aud": "sss",
        "uid": "sss",
        "iat": 1559324664,
        "exp": 1559324664
    }

    access_token = jwt.encode(access_token_layout,
                              'secret', algorithm='HS256',
                              headers={'kid': '230498151c214b788dd97f22b85410a5'})
    response = {
        "accessToken": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "expiration": 1524167011,
        "refresh_token": "jy4gl91BQ"
    }
    responses.add(responses.GET, url + '/v1/preauth/validateAuth', body=json.dumps(response), status=200)

    authenticator = CloudPakForDataAuthenticator(
        'my_username', 'my_password', url)

    request = {'headers': {}}
    authenticator.authenticate(request)
    assert request['headers']['Authorization'] is not None
