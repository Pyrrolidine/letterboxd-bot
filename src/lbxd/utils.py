from .core import *
import os.path
import json


def check_lbxd():
    lbxd_link = '[Letterboxd](https://letterboxd.com/)'
    status_embed = discord.Embed(colour=0xd8b437)
    status_embed.set_author(name="Letterboxd Status",
                            icon_url="https://i.imgur.com/5VALKVy.jpg",
                            url="https://letterboxd.com/")
    try:
        page = s.get("https://letterboxd.com")
        page.raise_for_status()
        status_embed.description = ':white_check_mark: {} is **up**'\
                                   .format(lbxd_link)
    except requests.exceptions.HTTPError:
        status_embed.description = ':x: ' + lbxd_link + ' is **down**'
    return status_embed
