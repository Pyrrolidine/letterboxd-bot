import discord
import requests
import config
from bs4 import BeautifulSoup
from .api import *
from .exceptions import *

tmdb_api_key = config.keys['tmdb']
api_base = config.letterboxd['api_base']
api_key = config.letterboxd['api_key']
api_secret = config.letterboxd['api_secret']
api = API(api_base, api_key, api_secret)
s = requests.Session()


# Converting the review or list description in HTML to text
def format_text(input_html, max_char):
    html = BeautifulSoup(input_html, 'html.parser')
    text = '```' + html.text[:max_char].strip()
    if len(text) > max_char:
        text += '...'
    text += '```'
    return text
