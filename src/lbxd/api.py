import hashlib
import hmac
import time
import uuid
from .core import *

# Credits for this file goes to bobtiki
# https://github.com/bobtiki/letterboxd


class API(object):

    def __init__(self, api_base, api_key, api_secret):
        self.api_base = api_base
        self.api_key = api_key
        self.api_secret = api_secret

        self.session = requests.Session()
        self.session.params = {}

    def api_call(self, path, params={}, form=None, headers={}, method="get"):
        url = f"{self.api_base}/{path}"
        params = self.__add_unique_params(params)
        request = requests.Request(
            method.upper(), url, params=params, data=[], headers=headers
        )
        prepared_request = self.session.prepare_request(request)
        signature = self.__sign(
            method=prepared_request.method,
            url=prepared_request.url,
            body=prepared_request.body,
        )
        prepared_request.prepare_url(prepared_request.url,
                                     {"signature": signature})
        try:
            response = self.session.send(prepared_request)
        except requests.exceptions.HTTPError as error:
            print(error)
            raise LbxdServerError('There was a problem trying to access'
                                  + ' Letterboxd.')

        if response.ok:
            return response
        else:
            response.raise_for_status()
            return response

    def __add_unique_params(self, params):
        params["apikey"] = self.api_key
        # nonce: UUID string, must be unique for each API request
        params["nonce"] = uuid.uuid4()
        # timestamp: number of seconds since epoch, Jan 1, 1970 (UTC)
        params["timestamp"] = int(time.time())
        return params

    def __sign(self, method, url, body=""):
        # Create the salted bytestring
        if body is None:
            body = ""
        signing_bytestring = b"\x00".join(
            [str.encode(method), str.encode(url), str.encode(body)]
        )
        # applying an HMAC/SHA-256 transformation, using our API Secret
        signature = hmac.new(
            str.encode(self.api_secret), signing_bytestring,
            digestmod=hashlib.sha256
        )
        # get the string representation of the hash
        signature_string = signature.hexdigest()
        return signature_string
