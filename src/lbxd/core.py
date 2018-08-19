import config
from bs4 import BeautifulSoup
from .api import API

api = API(config.letterboxd['api_base'], config.letterboxd['api_key'],
          config.letterboxd['api_secret'])


# Converting the review or list description in HTML to text
def format_text(input_html, max_char):
    html = BeautifulSoup(input_html, 'html.parser')
    text = '```' + html.text[:max_char].strip()
    text += '...```' if len(text) > max_char else '```'
    return text
