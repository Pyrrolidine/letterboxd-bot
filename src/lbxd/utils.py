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


def update_json(bot_guilds, bot_commands):
    if not os.path.isfile('data_bot.txt'):
        json_dict = {'commands': []}
        for command in bot_commands:
            cmd_dict = dict()
            cmd_dict.setdefault('name', command.name)
            cmd_dict.setdefault('used', 0)
            json_dict['commands'].append(cmd_dict)
        with open('data_bot.txt', 'w') as data_file:
            json.dump(json_dict, data_file, indent=2, sort_keys=True)
