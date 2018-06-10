from .core import *


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
