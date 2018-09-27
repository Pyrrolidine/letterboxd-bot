import hashlib
import hmac
import time
import uuid
import requests
from .exceptions import LbxdServerError

# Credits for this file goes to bobtiki
# https://github.com/bobtiki/letterboxd


class API:
    def __init__(self, api_base, api_key, api_secret):
        self._api_base = api_base
        self._api_key = api_key
        self._api_secret = api_secret
        self.session = requests.Session()

    def api_call(self, path, params={}):
        url = f'{self._api_base}/{path}'
        params = self.__add_unique_params(params)
        request = requests.Request('GET', url, params=params)
        prepared_request = self.session.prepare_request(request)
        signature = self.__sign(
            method=prepared_request.method, url=prepared_request.url)
        prepared_request.prepare_url(prepared_request.url,
                                     {'signature': signature})
        try:
            response = self.session.send(prepared_request)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            if error.response is not None and error.response.status_code == 404:
                return ''
            print('API Error:\n' + str(error))
            raise LbxdServerError('A request to the Letterboxd API failed.' +
                                  ' This may be due to a server issue.')
        return response

    def __add_unique_params(self, params):
        params['apikey'] = self._api_key
        params['nonce'] = uuid.uuid4()
        params['timestamp'] = int(time.time())
        return params

    def __sign(self, method, url, body=''):
        # Create the salted bytestring
        signing_bytestring = b'\x00'.join(
            [str.encode(method),
             str.encode(url),
             str.encode(body)])
        # applying an HMAC/SHA-256 transformation, using our API Secret
        signature = hmac.new(
            str.encode(self._api_secret),
            signing_bytestring,
            digestmod=hashlib.sha256)
        # get the string representation of the hash
        signature_string = signature.hexdigest()
        return signature_string
