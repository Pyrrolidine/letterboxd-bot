import discord
import time
from discord.ext import commands
import lbxd
import dbl
import asyncio
import json
import requests
import config

TOKEN = config.keys['discord']
bot = commands.Bot(command_prefix='!', case_insensitive=True,
                   activity=discord.Game('!helplb - boxdbot.com'),
                   owner_id=81412646271717376)
bot.remove_command('help')
start_time = 0
cmd_list = list()
#with open('dbl_token') as token_file:
#    dbl_token = token_file.readline().strip()
#dblpy = dbl.Client(bot, dbl_token)


@bot.event
async def on_ready():
    print('Logged in {} servers as'.format(len(bot.guilds)))
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await asyncio.sleep(1)
    # List of commands and their aliases to be recognized when !del is used
    for command in bot.commands:
        cmd_list.append(command.name)
        for alias in command.aliases:
            cmd_list.append(alias)
    #bot.loop.create_task(update_stats())


# Update the server count of the discordbots.org page
async def update_stats():
    while True:
        try:
            await dblpy.post_server_count()
        except Exception:
            pass
        await asyncio.sleep(1800)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.guild is not None:
        if message.guild.id in [264445053596991498]:
            return

    await bot.process_commands(message)
    # Redirects PMs to me
    if not message.content.startswith('!'):
        if isinstance(message.channel, discord.DMChannel):
            porkepik = await bot.get_user_info(81412646271717376)
            await porkepik.send('`' + str(message.author)
                                + '`\n\n' + message.content)


# To track the time it took to respond
@bot.before_invoke
async def before_invoke(ctx):
    global start_time
    start_time = time.perf_counter()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('This command requires a parameter.')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send('The bot needs the {} permission to use this command.'
                       .format(', '.join(err for err in error.missing_perms)))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You need the {} permission to use this command.'
                       .format(', '.join(err for err in error.missing_perms)))
    elif isinstance(error, commands.BadArgument):
        await ctx.send('The command failed likely due to the handling of a'
                       + ' special character.')
    elif isinstance(error, commands.CommandNotFound)\
            or isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, requests.exceptions.HTTPError):
            if error.original.status_code >= 500:
                await ctx.send('The command failed due to server issues.')
        if isinstance(error.original, discord.HTTPException)\
                and error.original.status == 403:
            return
        print('CommandInvokeError: ', ctx.message.content)
        raise error
    else:
        print(ctx.message.content)
        raise error


# Abstraction sending the response either as an embed or normal message
async def send_msg(ctx, msg):
    if isinstance(msg, discord.Embed):
        # Displays the response time in the test server
        if ctx.guild is not None and ctx.guild.id == 335569261080739863:
            global start_time
            msg.set_footer(text="cmd time: {:.3}"
                           .format(time.perf_counter() - start_time))
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


# Commands


@bot.command()
async def helplb(ctx):
    with open('help.txt') as help_f:
        help_embed = discord.Embed(colour=discord.Color.from_rgb(54, 57, 62))
        help_embed.set_thumbnail(url="https://i.imgur.com/Kr1diFu.png")
        help_embed.set_author(name="Letterboxd Bot",
                              icon_url="https://i.imgur.com/5VALKVy.jpg",
                              url="https://boxdbot.com/")
        help_embed.set_footer(text="Created by Porkepik#2664",
                              icon_url="https://i.imgur.com/li4cLpd.png")
        for line in help_f:
            if not line.startswith('!'):
                continue
            help_embed.add_field(name=line, value=next(help_f), inline=False)
        help_embed.description = "[Invite Bot](https://discordapp.com/oauth2"\
                                + "/authorize?client_id=437737824255737857"\
                                + "&permissions=93248&scope=bot) | "\
                                + "[Website](https://boxdbot.com) | "\
                                + "[GitLab](https://gitlab.com/Porkepik/"\
                                + "PublicLetterboxdDiscordBot)"
    await send_msg(ctx, help_embed)


@bot.command()
async def checklb(ctx):
    msg = lbxd.utils.check_lbxd()
    await send_msg(ctx, msg)


@bot.command(aliases=['u'])
async def user(ctx, arg):
    try:
        cmd_user = lbxd.user.User(arg)
        msg = cmd_user.create_embed()
    except lbxd.core.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['c', 'a', 'actor', 'd', 'director'])
async def crew(ctx, *, arg):
    try:
        crew = lbxd.crew.Crew(arg, ctx.invoked_with)
        msg = crew.create_embed()
    except lbxd.core.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['movie', 'f'])
async def film(ctx, *, arg):
    try:
        # eiga.me ratings for specific servers
        if ctx.guild is not None and ctx.guild.id in config.mkdb_servers:
            cmd_film = lbxd.film.Film(arg, True, True)
        else:
            cmd_film = lbxd.film.Film(arg)
        msg = cmd_film.create_embed()
    except lbxd.core.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


async def check_if_two_args(ctx):
    msg = ctx.message.content.split()
    if len(msg) < 3:
        await ctx.send('This command requires 2 parameters.')
    return len(msg) > 2


@bot.command(aliases=['l'])
@commands.check(check_if_two_args)
async def list(ctx, username, *args):
    try:
        cmd_user = lbxd.user.User(username, False)
        cmd_list_ = lbxd.list_.List(cmd_user, ' '.join(str(i) for i in args))
        msg = cmd_list_.create_embed()
    except lbxd.core.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['r'])
@commands.check(check_if_two_args)
async def review(ctx, user, *args):
    try:
        cmd_film = lbxd.film.Film(' '.join(str(i) for i in args), False)
        cmd_user = lbxd.user.User(user, False)
        cmd_review = lbxd.review.Review(cmd_user, cmd_film)
        msg = cmd_review.create_embed()
    except lbxd.core.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(name='del')
@commands.bot_has_permissions(manage_messages=True)
async def delete(ctx):
    await ctx.message.delete()
    found_bot_msg = False
    found_usr_cmd = False
    async for log_message in ctx.channel.history(limit=30):
        if found_bot_msg:
            if not log_message.content.startswith('!'):
                continue
            for cmd in cmd_list:
                if log_message.content.startswith('!{} '.format(cmd))\
                   or log_message.content in ['!checklb', '!helplb']:
                    cmd_message = log_message
                    found_usr_cmd = True
                    break
            if found_usr_cmd:
                break
        if log_message.author == bot.user and not found_bot_msg:
            bot_message = log_message
            found_bot_msg = True

    if found_usr_cmd:
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            if not cmd_message.author.id == ctx.author.id:
                return
        await bot_message.delete()
        await cmd_message.delete()


bot.run(TOKEN)
