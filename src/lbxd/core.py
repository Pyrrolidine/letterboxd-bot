import discord
import urllib.request
import requests
from bs4 import BeautifulSoup, SoupStrainer
from .lbxd_errors import *

api_file = open('TMDbAPI')
api_key = api_file.readline().strip()
api_file.close()
s = requests.Session()


def format_text(html, max_char):
    temp_text = '```'
    for br in html.find_all('br'):
        br.replace_with('\n')
    for paragraph in html.find_all('p'):
        for index, line in enumerate(paragraph.get_text().split('\n')):
            if index > 10:
                break
            temp_text += line.strip() + '\n'
        temp_text += '\n'

    text = temp_text[:max_char].strip()
    if len(temp_text) > max_char:
        text += '...'
    text += '```'
    return text
