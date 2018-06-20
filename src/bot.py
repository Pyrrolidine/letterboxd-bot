import discord
import time
from discord.ext import commands
import lbxd

token_file = open('Token')
TOKEN = token_file.readline().strip()

bot = commands.Bot(command_prefix='!', case_insensitive=True,
                   activity=discord.Game('!helplb - v1.4.2'))
bot.remove_command('help')
start_time = 0


@bot.before_invoke
async def before_invoke(ctx):
    global start_time
    start_time = time.perf_counter()


async def send_msg(ctx, msg):
    keep_history(ctx.message)
    if isinstance(msg, discord.Embed):
        global start_time
        # Checks if the command took more than 5 seconds
        if time.perf_counter() - start_time > 5:
            msg.set_footer(text="The bot was slow to respond."
                                + " This may be due to a server issue "
                                + "from a third-party service.")
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


def keep_history(message):
    if not isinstance(message.channel, discord.DMChannel):
        with open('history_{}.txt'.format(message.guild.id), 'a') as f:
            f.write(str(message.channel.id) + ' ' + str(message.id) + '\n')
        lbxd.utils.limit_history(30, str(message.guild.id))


@bot.command()
async def helplb(ctx):
    with open('help.txt') as help_f:
        help_embed = discord.Embed(colour=0xd8b437)
        help_embed.set_author(name="LetterboxdBot",
                              icon_url="https://i.imgur.com/5VALKVy.jpg",
                              url="https://gitlab.com/Porkepik/"
                                   + "PublicLetterboxdDiscordBot")
        help_embed.set_footer(text="Created by Porkepik#2664",
                              icon_url="https://i.imgur.com/li4cLpd.png")
        for line in help_f:
            if not line.startswith('!'):
                continue
            help_embed.add_field(name=line, value=next(help_f), inline=False)
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
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['a'])
async def actor(ctx, *, arg):
    try:
        actor = lbxd.crew.Crew(arg, "/actors/")
        msg = actor.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['d'])
async def director(ctx, *, arg):
    try:
        director = lbxd.crew.Crew(arg, "/directors/")
        msg = director.create_embed()
    except lbxd.lbxd_errors.LbxdErrors as err:
        msg = err
    await send_msg(ctx, msg)


@bot.command(aliases=['movie', 'f'])
async def film(ctx, *, arg):
    try:
        # eiga.me ratings for a specific server and my test server
        if ctx.guild.id in [316973025386037268, 335569261080739863]:
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
    command_to_erase = lbxd.utils.del_last_line(str(ctx.message.guild.id),
                                                str(ctx.message.channel.id))
    deleted_message = False
    async for log_message in ctx.channel.history(limit=30):
        if log_message.author == bot.user and not deleted_message:
            deleted_message = True
            await log_message.delete()
            if not len(command_to_erase):
                break
        if str(log_message.id) == command_to_erase:
            await log_message.delete()
            break


@bot.event
async def on_command_error(ctx, error):
    keep_history(ctx.message)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('This command requires a parameter.')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send('The bot needs the {} permission to use this command.'
                       .format(', '.join(err for err in error.missing_perms)))
    elif isinstance(error, commands.CommandNotFound)\
            or isinstance(error, commands.CheckFailure):
        pass
    else:
        raise error


@bot.event
async def on_message(message):
    if message.author == bot.user:
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

bot.run(TOKEN)
