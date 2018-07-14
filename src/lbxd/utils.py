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
        json_dict = {'servers': [], 'commands': []}
        for command in bot_commands:
            cmd_dict = dict()
            cmd_dict.setdefault('name', command.name)
            cmd_dict.setdefault('used', 0)
            json_dict['commands'].append(cmd_dict)
        for server in bot_guilds:
            server_dict = dict()
            server_dict.setdefault('id', server.id)
            server_dict.setdefault('delay', 0)
            server_dict.setdefault('slowtime', 0)
            server_dict.setdefault('timer', 0)
            json_dict['servers'].append(server_dict)
        with open('data_bot.txt', 'w') as data_file:
            json.dump(json_dict, data_file, indent=2, sort_keys=True)
    else:
        with open('data_bot.txt') as data_file:
            data = json.load(data_file)
        for server in data['servers']:
            server['delay'] = 0
            server['timer'] = 0
        with open('data_bot.txt', 'w') as data_file:
            json.dump(data, data_file, indent=2, sort_keys=True)
