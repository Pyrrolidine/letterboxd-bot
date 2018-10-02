import hashlib
import hmac
import logging
import time
import uuid

import requests

from config import SETTINGS

from .exceptions import LbxdServerError

api_session = requests.Session()


def api_call(path, params=None):
    url = SETTINGS['letterboxd']['api_base'] + path
    if not params:
        params = dict()
    params = __add_unique_params(params)
    request = requests.Request('GET', url, params=params)
    prepared_request = api_session.prepare_request(request)
    signature = __sign(
        method=prepared_request.method, url=prepared_request.url)
    prepared_request.prepare_url(prepared_request.url,
                                 {'signature': signature})
    try:
        response = api_session.send(prepared_request)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        if error.response and error.response.status_code == 404:
            return ''
        logging.warning('API Error:\n' + str(error))
        raise LbxdServerError('A request to the Letterboxd API failed.' +
                              ' This may be due to a server issue.')
    return response


def __add_unique_params(params):
    params['apikey'] = SETTINGS['letterboxd']['api_key']
    params['nonce'] = uuid.uuid4()
    params['timestamp'] = int(time.time())
    return params


def __sign(method, url, body=''):
    # Create the salted bytestring
    signing_bytestring = b'\x00'.join(
        [str.encode(method),
         str.encode(url),
         str.encode(body)])
    # applying an HMAC/SHA-256 transformation, using our API Secret
    signature = hmac.new(
        str.encode(SETTINGS['letterboxd']['api_secret']),
        signing_bytestring,
        digestmod=hashlib.sha256)
    # get the string representation of the hash
    signature_string = signature.hexdigest()
    return signature_string
