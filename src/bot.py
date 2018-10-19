import logging
from asyncio import sleep

import discord
import requests
from config import SETTINGS
from discord.ext import commands
from lbxd.crew import crew_embed
from lbxd.diary import diary_embed
from lbxd.exceptions import LbxdErrors
from lbxd.film import film_embed
from lbxd.list_ import list_embed
from lbxd.review import review_embed
from lbxd.user import user_embed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%m/%d %H:%M:%S')

bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command('help')


@bot.event
async def on_ready():
    logging.info(
        'Logged in %d servers as %s' % (len(bot.guilds), bot.user.name))
    bot.loop.create_task(update_stats())


async def update_stats():
    while True:
        await bot.change_presence(
            activity=discord.Game('!helplb - {} servers'.format(
                len(bot.guilds))))
        await sleep(900)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('This command requires a parameter.')
        return
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            'The bot needs the {} permission to use this command.'.format(
                ', '.join(err for err in error.missing_perms)))
        return
    if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
        return
    if isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.HTTPException)\
                and error.original.status == 403:
            return
        if isinstance(error.original, requests.exceptions.ConnectionError):
            await ctx.send('The command failed due to connection issues.')
            return
    await ctx.send('The command crashed, a report was sent to the dev.')
    logging.error(ctx.message.content)
    raise error


async def send_msg(ctx, msg):
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.event
async def on_command_completion(ctx):
    if SETTINGS['log_channel']:
        log_channel = bot.get_channel(SETTINGS['log_channel'])
        await log_channel.send(ctx.command.name)


# Commands


@bot.command()
async def helplb(ctx):
    help_embed = discord.Embed(colour=discord.Color.from_rgb(54, 57, 62))
    help_embed.set_thumbnail(url='https://i.imgur.com/Kr1diFu.png')
    help_embed.set_author(
        name='Letterboxd Bot', icon_url='https://i.imgur.com/5VALKVy.jpg')
    help_embed.set_footer(
        text='Created by Porkepik#2664',
        icon_url='https://i.imgur.com/li4cLpd.png')
    for key, value in SETTINGS['help'].items():
        help_embed.add_field(name=key, value=value, inline=False)
    help_embed.description = '[Invite Bot](https://discordapp.com/oauth2'\
        + '/authorize?client_id=437737824255737857'\
        + '&permissions=93248&scope=bot) | '\
        + '[GitHub](https://github.com/Porkepik/LetterboxdDiscordBot)'
    await ctx.send(embed=help_embed)


@bot.command(aliases=['u'])
async def user(ctx, username):
    try:
        msg = user_embed(username)
    except LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command()
async def diary(ctx, username):
    try:
        msg = diary_embed(username)
    except LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['c', 'a', 'actor', 'd', 'director'])
async def crew(ctx, *, arg):
    try:
        msg = crew_embed(arg, ctx.invoked_with)
    except LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['movie', 'f'])
async def film(ctx, *, arg):
    try:
        # eiga.me ratings for specific servers
        if ctx.guild and ctx.guild.id in SETTINGS['mkdb_servers']:
            msg = film_embed(arg, True, True)
        else:
            msg = film_embed(arg)
    except LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


async def check_if_two_args(ctx):
    msg = ctx.message.content.split()
    if len(msg) < 3:
        await ctx.send('This command requires 2 parameters.')
    return len(msg) > 2


@bot.command(aliases=['l'], name='list')
@commands.check(check_if_two_args)
async def list_(ctx, username, *args):
    try:
        msg = list_embed(username, ' '.join(str(i) for i in args))
    except LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['r'])
@commands.check(check_if_two_args)
async def review(ctx, username, *args):
    try:
        msg = review_embed(username, ' '.join(str(i) for i in args))
    except LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(name='del')
@commands.bot_has_permissions(manage_messages=True)
async def delete(ctx):
    await ctx.message.delete()
    found_bot_msg = False
    found_usr_cmd = False
    cmd_list = []
    # Get list of commands and their aliases
    for command in bot.commands:
        cmd_list.append(command.name)
        for alias in command.aliases:
            cmd_list.append(alias)

    async for log_message in ctx.channel.history(limit=30):
        if log_message.author.id == bot.user.id and not found_bot_msg:
            bot_message = log_message
            found_bot_msg = True
        elif found_bot_msg:
            if log_message.content:
                first_word = log_message.content.split()[0]
            else:
                return
            for cmd in cmd_list:
                if first_word == '!{}'.format(cmd):
                    found_usr_cmd = True
                    break
            if found_usr_cmd:
                cmd_message = log_message
                break

    if found_usr_cmd:
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            if not cmd_message.author.id == ctx.author.id:
                return
        await bot_message.delete()
        await cmd_message.delete()


bot.run(SETTINGS['discord'])
