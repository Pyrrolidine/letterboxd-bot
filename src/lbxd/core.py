import discord
import urllib.request
import requests
from bs4 import BeautifulSoup, SoupStrainer
from .lbxd_errors import *

api_file = open('TMDbAPI')
api_key = api_file.readline().strip()
api_file.close()
imgur_file = open('Imgur')
imgur_token = imgur_file.readline().strip()
imgur_file.close()
token_header = {'Authorization': 'Bearer {}'.format(imgur_token)}
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

    text = '\n' + temp_text[:max_char].strip()
    if len(temp_text) > max_char:
        text += '...'
    text += '```'
    return text


def limit_history(max_size, server_id):
    # If there are more than max_size lines
    # in the command history file (unique to each servers), deletes the oldest
    with open('history_{}.txt'.format(server_id)) as f:
        lines = f.readlines()
    if len(lines) > max_size:
        with open('history_{}.txt'.format(server_id), 'w') as f:
            f.writelines(lines[1:])


def del_last_line(server_id, channel_id):
    msg_id_to_erase = ""
    try:
        with open('history_{}.txt'.format(server_id)) as f:
            lines = f.readlines()
            if not len(lines):
                return ""

        with open('history_{}.txt'.format(server_id), 'a') as f:
            f.seek(0)
            f.truncate()
            for index, line in enumerate(lines[::-1]):
                if line.split()[0] == channel_id:
                    msg_id_to_erase = lines.pop(-1-index).split()[1]
                    if len(lines):
                        f.writelines(lines)
                    break
    except FileNotFoundError:
        open('history_{}.txt'.format(server_id), 'w')

    return msg_id_to_erase


def check_lbxd():
    try:
        page = s.get("https://letterboxd.com")
        page.raise_for_status()
        return "Letterboxd is up."
    except requests.exceptions.HTTPError:
        return "Letterboxd is down."
