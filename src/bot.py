import discord
from discord.ext import commands
import lbxd
import config
import time
import dbl
import asyncio
import requests

TOKEN = config.keys['discord']
bot = commands.Bot(
    command_prefix='!',
    case_insensitive=True,
    activity=discord.Game('!helplb - boxdbot.com'))
bot.remove_command('help')
start_time = 0
# dblpy = dbl.Client(bot, config.keys['dbl'])


@bot.event
async def on_ready():
    print('Logged in {} servers as'.format(len(bot.guilds)))
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    # bot.loop.create_task(update_stats())


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
    message.content = message.content.replace('’', '').replace('‘', '')
    await bot.process_commands(message)


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
    elif isinstance(error, commands.CommandNotFound)\
            or isinstance(error, commands.CheckFailure):
        pass
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.HTTPException)\
                and error.original.status == 403:
            return
        elif isinstance(error.original, requests.exceptions.ConnectionError):
            await ctx.send('The command failed due to connection issues.')
        else:
            await ctx.send('The command crashed, a report was sent to the dev')
            print('CommandInvokeError: ', ctx.message.content)
            raise error
    else:
        print(ctx.message.content)
        raise error


# Abstraction sending the response either as an embed or normal message
async def send_msg(ctx, msg):
    if isinstance(msg, discord.Embed):
        # Displays the response time in the test server
        if ctx.guild is not None and ctx.guild.id in config.test_server:
            global start_time
            msg.set_footer(text='cmd time: {:.3}'
                           .format(time.perf_counter() - start_time))
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


# Commands


@bot.command()
async def helplb(ctx):
    msg = lbxd.utils.help_lbxd()
    await send_msg(ctx, msg)


@bot.command()
async def checklb(ctx):
    msg = lbxd.utils.check_lbxd()
    await send_msg(ctx, msg)


@bot.command(aliases=['u'])
async def user(ctx, arg):
    try:
        cmd_user = lbxd.user.User(arg)
        msg = cmd_user.create_embed()
    except lbxd.exceptions.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command()
async def diary(ctx, arg):
    try:
        cmd_user = lbxd.user.User(arg)
        cmd_diary = lbxd.diary.Diary(cmd_user)
        msg = cmd_diary.create_embed()
    except lbxd.exceptions.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['c', 'a', 'actor', 'd', 'director'])
async def crew(ctx, *, arg):
    try:
        crew = lbxd.crew.Crew(arg, ctx.invoked_with)
        msg = crew.create_embed()
    except lbxd.exceptions.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['movie', 'f'])
async def film(ctx, *, arg):
    try:
        # eiga.me ratings for specific servers
        if ctx.guild is not None and ctx.guild.id in config.mkdb_servers:
            if ctx.channel.id in config.mkdb_only_channels:
                cmd_film = lbxd.film.Film(arg, True, True, True)
            else:
                cmd_film = lbxd.film.Film(arg, True, True)
        else:
            cmd_film = lbxd.film.Film(arg)
        msg = cmd_film.create_embed()
    except lbxd.exceptions.LbxdErrors as err:
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
        cmd_list = lbxd.list_.List(cmd_user, ' '.join(str(i) for i in args))
        msg = cmd_list.create_embed()
    except lbxd.exceptions.LbxdErrors as err:
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
    except lbxd.exceptions.LbxdErrors as err:
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
        if log_message.author == bot.user and not found_bot_msg:
            bot_message = log_message
            found_bot_msg = True
        elif found_bot_msg:
            for cmd in cmd_list:
                if log_message.content.startswith('!{} '.format(cmd)):
                    found_usr_cmd = True
                    break
            if log_message.content in ['!checklb', '!helplb']:
                found_usr_cmd = True
            if found_usr_cmd:
                cmd_message = log_message
                break

    if found_usr_cmd:
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            if not cmd_message.author.id == ctx.author.id:
                return
        await bot_message.delete()
        await cmd_message.delete()


bot.run(TOKEN)
