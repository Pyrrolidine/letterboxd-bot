import config
import discord


def help_lbxd():
    help_embed = discord.Embed(colour=discord.Color.from_rgb(54, 57, 62))
    help_embed.set_thumbnail(url='https://i.imgur.com/Kr1diFu.png')
    help_embed.set_author(
        name='Letterboxd Bot',
        icon_url='https://i.imgur.com/5VALKVy.jpg',
        url='https://boxdbot.com/')
    help_embed.set_footer(
        text='Created by Porkepik#2664',
        icon_url='https://i.imgur.com/li4cLpd.png')
    for key, value in config.help_text.items():
        help_embed.add_field(name=key, value=value, inline=False)
    help_embed.description = '[Invite Bot](https://discordapp.com/oauth2'\
        + '/authorize?client_id=437737824255737857'\
        + '&permissions=93248&scope=bot) | [Website](https://boxdbot.com)'\
        + ' | [GitLab](https://gitlab.com/Porkepik/LetterboxdDiscordBot)'
    return help_embed
