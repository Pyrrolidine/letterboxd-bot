import discord
import urllib.request
import requests
from bs4 import BeautifulSoup, SoupStrainer
from .lbxd_errors import *
from .api import *

with open('TMDbAPI') as api_file:
    tmdb_api_key = api_file.readline().strip()
s = requests.Session()
with open('LBXDAPI') as api_file:
    lines = api_file.readlines()
    api_base = lines[0].strip()
    api_key = lines[1].strip()
    api_secret = lines[2].strip()
api = API(api_base, api_key, api_secret)


def format_text(input_html, max_char):
    html = BeautifulSoup(input_html, 'html.parser')
    text = '```' + html.text[:max_char].strip()
    if len(text) > max_char:
        text += '...'
    text += '```'
    return text
