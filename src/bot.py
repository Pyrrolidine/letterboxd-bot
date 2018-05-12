import discord
from discord.ext import commands
import lbxd

token_file = open('Token')
TOKEN = token_file.readline().strip()

bot = commands.Bot(command_prefix='!', case_insensitive=True,
                   activity=discord.Game('Say !helplb'))
bot.remove_command('help')


async def send_msg(ctx, msg):
    keep_history(ctx.message)
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


def keep_history(message):
    if not isinstance(message.channel, discord.DMChannel):
        with open('history_{}.txt'.format(message.guild.id), 'a') as f:
            f.write(str(message.channel.id) + ' ' + str(message.id) + '\n')
        lbxd.limit_history(30, str(message.guild.id))


@bot.command()
async def helplb(ctx):
    help_file = open('help.txt')
    msg = ''.join(help_file.readlines())
    await send_msg(ctx, msg)


@bot.command()
async def checklb(ctx):
    msg = lbxd.check_lbxd()
    await send_msg(ctx, msg)


@bot.command(aliases=['u'])
async def user(ctx, arg):
    msg = lbxd.get_user_info(arg)
    await send_msg(ctx, msg)


@bot.command(aliases=['a'])
async def actor(ctx, *, arg):
    msg = lbxd.search_letterboxd(arg, "/actors/")
    if msg.startswith('https://'):
        msg = lbxd.get_crew_info(msg)
    await send_msg(ctx, msg)


@bot.command(aliases=['d'])
async def director(ctx, *, arg):
    msg = lbxd.search_letterboxd(arg, "/directors/")
    if msg.startswith('https://'):
        msg = lbxd.get_crew_info(msg)
    await send_msg(ctx, msg)


@bot.command(aliases=['movie', 'f'])
async def film(ctx, *, arg):
    msg = lbxd.search_letterboxd(arg, "/films/")
    if msg.startswith('https://'):
        msg = lbxd.get_info_film(msg)
    await send_msg(ctx, msg)


async def check_if_two_args(ctx):
    msg = ctx.message.content.split()
    if len(msg) < 3:
        await ctx.send('This command requires at least 2 parameters.')
    return len(msg) > 2


@bot.command(aliases=['l'])
@commands.check(check_if_two_args)
async def list(ctx, user, *args):
    msg = lbxd.find_list(user.strip(','), ' '.join(str(i) for i in args))
    await send_msg(ctx, msg)


@bot.command(aliases=['r'])
@commands.check(check_if_two_args)
async def review(ctx, user, *args):
    film_link = lbxd.search_letterboxd(' '.join(str(i) for i in args),
                                       "/films/")
    if film_link.startswith("https://letterboxd.com"):
        split_film_link = film_link.split('/')
        if len(split_film_link[-1]) > 0:
            film = split_film_link[-1]
        else:
            film = split_film_link[-2]
        msg = lbxd.get_review(film, user.strip(','))
    else:
        msg = film_link
    await send_msg(ctx, msg)


@bot.command(name='del')
@commands.bot_has_permissions(manage_messages=True)
async def delete(ctx):
    await ctx.message.delete()
    command_to_erase = lbxd.del_last_line(str(ctx.message.guild.id),
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
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)
