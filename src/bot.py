import discord
import time
from discord.ext import commands
import lbxd
import dbl
import logging
import asyncio
import json

with open('Token') as token_file:
    TOKEN = token_file.readline().strip()

bot = commands.Bot(command_prefix='!', case_insensitive=True,
                   activity=discord.Game('!helplb'),
                   owner_id=81412646271717376)
bot.remove_command('help')
start_time = 0
cmd_list = list()

#with open('dbl_token') as token_file:
#    dbl_token = token_file.readline().strip()
#dblpy = dbl.Client(bot, dbl_token)
#logger = logging.getLogger('bot')


async def update_stats():
    while True:
        logger.info('attempting to post server count')
        try:
            await dblpy.post_server_count()
            logger.info('posted server count ({})'
                        .format(len(bot.guilds)))
        except Exception as e:
            logger.exception('Failed to post server count\n{}: {}'
                             .format(type(e).__name__, e))
        await asyncio.sleep(1800)


@bot.before_invoke
async def before_invoke(ctx):
    global start_time
    start_time = time.perf_counter()


async def on_cooldown(ctx):
    with open('data_bot.txt') as data_file:
        data = json.load(data_file)
    owner_bot = await bot.is_owner(ctx.author)

    for server in data['servers']:
        if server['id'] == ctx.guild.id:
            delay = server['delay']

            if time.perf_counter() > float(server['timer'])\
              and int(server['timer']):
                server['delay'] = 0
                server['timer'] = 0
                server['slowtime'] = 0
            if ctx.author.permissions_in(ctx.channel).manage_messages\
              or owner_bot:
                return True
            elif time.perf_counter() > delay:
                server['delay'] = time.perf_counter()\
                                  + float(server['slowtime'])
                with open('data_bot.txt', 'w') as data_file:
                    json.dump(data, data_file, indent=2, sort_keys=True)
                return True
            else:
                await ctx.message.add_reaction('🚫')
                await ctx.message.add_reaction('🐢')
                return False


async def send_msg(ctx, msg):
    if isinstance(msg, discord.Embed):
        if ctx.guild is not None and ctx.guild.id == 335569261080739863:
            global start_time
            msg.set_footer(text="cmd time: {:.3}"
                           .format(time.perf_counter() - start_time))
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.command()
@commands.check(on_cooldown)
async def helplb(ctx):
    with open('help.txt') as help_f:
        help_embed = discord.Embed(colour=discord.Color.from_rgb(54, 57, 62))
        help_embed.set_thumbnail(url="https://i.imgur.com/Kr1diFu.png")
        help_embed.set_author(name="Letterboxd Bot",
                              icon_url="https://i.imgur.com/5VALKVy.jpg",
                              url="https://discordbots.org/bot/"
                                   + "437737824255737857")
        help_embed.set_footer(text="Created by Porkepik#2664",
                              icon_url="https://i.imgur.com/li4cLpd.png")
        for line in help_f:
            if not line.startswith('!'):
                continue
            help_embed.add_field(name=line, value=next(help_f), inline=False)
        help_embed.description = "[Invite Bot](https://discordapp.com/oauth2"\
                                + "/authorize?client_id=437737824255737857"\
                                + "&permissions=93248&scope=bot)"
    await send_msg(ctx, help_embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def slowlb(ctx, user_slowtime, timer='0'):
    if not user_slowtime.isdigit() or not timer.isdigit():
        return
    if float(user_slowtime) < 0:
        user_slowtime = '0'
    if float(timer) < 0:
        timer = '0'
    with open('data_bot.txt') as data_file:
        data = json.load(data_file)

    for server in data['servers']:
        if server['id'] == ctx.guild.id:
            server['slowtime'] = user_slowtime
            server['timer'] = time.perf_counter() + (float(timer) * 60)
            server['delay'] = 0
            with open('data_bot.txt', 'w') as data_file:
                json.dump(data, data_file, indent=2, sort_keys=True)
            break

    if float(user_slowtime):
        msg = "A **slow mode** of **" + user_slowtime + " seconds**"
        if float(timer):
            msg += " for the next **" + timer + " minutes**"
        msg += " has been enabled."
        await ctx.send(msg)
    else:
        await ctx.send("Slow mode disabled.")


@bot.command()
@commands.check(on_cooldown)
async def checklb(ctx):
    msg = lbxd.utils.check_lbxd()
    await send_msg(ctx, msg)


@bot.command(aliases=['u'])
@commands.check(on_cooldown)
async def user(ctx, arg):
    try:
        cmd_user = lbxd.user.User(arg)
        msg = cmd_user.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['a'])
@commands.check(on_cooldown)
async def actor(ctx, *, arg):
    try:
        actor = lbxd.crew.Crew(arg, "/actors/")
        msg = actor.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['d'])
@commands.check(on_cooldown)
async def director(ctx, *, arg):
    try:
        director = lbxd.crew.Crew(arg, "/directors/")
        msg = director.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['movie', 'f'])
@commands.check(on_cooldown)
async def film(ctx, *, arg):
    try:
        # eiga.me ratings for specific servers
        mkdb_servers = []
        with open('mkdb_servers.txt') as mkdb_file:
            for str_mkdb_server in mkdb_file:
                mkdb_servers.append(int(str_mkdb_server.strip()))
        if ctx.guild is not None and ctx.guild.id in mkdb_servers:
            cmd_film = lbxd.film.Film(arg, True, True)
        else:
            cmd_film = lbxd.film.Film(arg)
        msg = cmd_film.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


async def check_if_two_args(ctx):
    msg = ctx.message.content.split()
    if len(msg) < 3:
        await ctx.send('This command requires at least 2 parameters.')
    return len(msg) > 2


@bot.command(aliases=['l'])
@commands.check(on_cooldown)
@commands.check(check_if_two_args)
async def list(ctx, user, *args):
    try:
        cmd_list = lbxd.list_.List(user.strip(','),
                                   ' '.join(str(i) for i in args))
        msg = cmd_list.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['r'])
@commands.check(on_cooldown)
@commands.check(check_if_two_args)
async def review(ctx, user, *args):
    try:
        cmd_film = lbxd.film.Film(' '.join(str(i) for i in args), False)
        cmd_review = lbxd.review.Review(user.strip(','), cmd_film)
        msg = cmd_review.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
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
    else:
        print(ctx.message.content)
        raise error


@bot.event
async def on_guild_join(guild):
    guild_dict = dict()
    guild_dict.setdefault('id', guild.id)
    guild_dict.setdefault('delay', 0)
    guild_dict.setdefault('slowtime', 0)
    guild_dict.setdefault('timer', 0)
    with open('data_bot.txt') as data_file:
        data = json.load(data_file)
    data['servers'].append(guild_dict)
    with open('data_bot.txt', 'w') as data_file:
        json.dump(data, data_file, indent=2, sort_keys=True)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.guild is not None:
        if message.guild.id in [264445053596991498]:
            return

    await bot.process_commands(message)
    if not message.content.startswith('!'):
        # Redirects PMs to me
        if isinstance(message.channel, discord.DMChannel):
            porkepik = await bot.get_user_info(81412646271717376)
            await porkepik.send('`' + str(message.author)
                                + '`\n\n' + message.content)


@bot.event
async def on_ready():
    print('Logged in {} servers as'.format(len(bot.guilds)))
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    lbxd.utils.update_json(bot.guilds)
    await asyncio.sleep(2)
    for command in bot.commands:
        cmd_list.append(command.name)
        for alias in command.aliases:
            cmd_list.append(alias)
    #bot.loop.create_task(update_stats())


bot.run(TOKEN)
