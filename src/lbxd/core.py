import config
from discord import Embed
from .api import API
from html.parser import HTMLParser

api = API(config.letterboxd['api_base'], config.letterboxd['api_key'],
          config.letterboxd['api_secret'])


class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.text = ''
        HTMLParser.__init__(self)

    def handle_data(self, data):
        self.text += data


# Converting the review or list description in HTML to text
def format_text(input_html, max_char):
    html = MyHTMLParser()
    html.feed(input_html)
    text = '```' + html.text[:max_char].strip()
    text += '...```' if len(text) > max_char else '```'
    return text


def create_embed(title, url, descript, thumbnail_url, image_url=''):
    embed = Embed(title=title, url=url, colour=0xd8b437, description=descript)
    embed.set_thumbnail(url=thumbnail_url)
    if len(image_url):
        embed.set_image(url=image_url)
    return embed
