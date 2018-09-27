import discord
from discord.ext import commands
import lbxd
import config
import asyncio
import requests

bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command('help')


@bot.event
async def on_ready():
    print('Logged in {0} servers as {1}'.format(
        len(bot.guilds), bot.user.name))
    bot.loop.create_task(update_stats())


async def update_stats():
    while True:
        await bot.change_presence(
            activity=discord.Game('!helplb - {} servers'.format(
                len(bot.guilds))))
        await asyncio.sleep(900)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('This command requires a parameter.')
        return
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            'The bot needs the {} permission to use this command.'.format(
                ', '.join(err for err in error.missing_perms)))
        return
    elif isinstance(error, commands.CommandNotFound)\
            or isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.HTTPException)\
                and error.original.status == 403:
            return
        elif isinstance(error.original, requests.exceptions.ConnectionError):
            await ctx.send('The command failed due to connection issues.')
            return
    await ctx.send('The command crashed, a report was sent to the dev.')
    print(ctx.message.content)
    raise error


async def send_msg(ctx, msg):
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.event
async def on_command_completion(ctx):
    log_channel = bot.get_channel(494198610028920832)
    await log_channel.send(ctx.command.name)


# Commands


@bot.command()
async def helplb(ctx):
    msg = lbxd.utils.help_lbxd()
    await send_msg(ctx, msg)


@bot.command(aliases=['u'])
async def user(ctx, arg):
    try:
        cmd_user = lbxd.user.User(arg)
        msg = cmd_user.embed
    except lbxd.exceptions.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command()
async def diary(ctx, arg):
    try:
        cmd_user = lbxd.user.User(arg, False)
        cmd_diary = lbxd.diary.Diary(cmd_user)
        msg = cmd_diary.embed
    except lbxd.exceptions.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['c', 'a', 'actor', 'd', 'director'])
async def crew(ctx, *, arg):
    try:
        crew = lbxd.crew.Crew(arg, ctx.invoked_with)
        msg = crew.embed
    except lbxd.exceptions.LbxdErrors as err:
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
        msg = cmd_film.embed
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
        msg = cmd_list.embed
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
        msg = cmd_review.embed
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
        if log_message.author.id == bot.user.id and not found_bot_msg:
            bot_message = log_message
            found_bot_msg = True
        elif found_bot_msg:
            first_word = log_message.content.split()[0]
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


bot.run(config.keys['discord'])
