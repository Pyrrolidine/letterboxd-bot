""" API request preparation
    Only one public function: api_call()
    It takes an endpoint and an optional dictionary of parameters
"""

import hashlib
import hmac
import time
import uuid
from urllib.parse import urlencode
import aiohttp
from config import SETTINGS
from .exceptions import LbxdServerError

class API:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def api_call(self, path, params=None, letterboxd=True, is_json=True):
        if not params:
            params = dict()
        api_url = path
        if letterboxd:
            url = SETTINGS['letterboxd']['api_base'] + path
            params['apikey'] = SETTINGS['letterboxd']['api_key']
            params['nonce'] = str(uuid.uuid4())
            params['timestamp'] = int(time.time())
            url += '?' + urlencode(params)
            api_url = url + '&signature=' + self.__sign(url)
        async with self.session.get(api_url) as resp:
            if resp.status >= 500:
                raise LbxdServerError('A request to the Letterboxd API failed.' +
                                      ' This may be due to a server issue.')
            elif resp.status >= 400:
                return ''
            if is_json:
                response = await resp.json()
            else:
                response = await resp.read()
        return response

    def __sign(self, url, body=''):
        # Create the salted bytestring
        signing_bytestring = b'\x00'.join(
            [str.encode('GET'),
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


bot_api = API()
