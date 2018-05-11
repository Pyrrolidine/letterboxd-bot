import discord
from discord.ext import commands
import lbxd

token_file = open('Token')
TOKEN = token_file.readline().strip()

bot = commands.Bot(command_prefix='!', case_insensitive=True,
                   activity=discord.Game('Say !helplb'))


@bot.command()
async def helplb(ctx):
    help_file = open('help.txt')
    msg = ''.join(help_file.readlines())
    await ctx.send(msg)


@bot.command()
async def checklb(ctx):
    msg = lbxd.check_lbxd()
    await ctx.send(msg)


@bot.command(aliases=['u'])
async def user(ctx, arg):
    msg = lbxd.get_user_info(arg)
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.command(aliases=['a'])
async def actor(ctx, *, arg):
    actor_url = lbxd.search_letterboxd(arg, "/actors/")
    if actor_url.startswith('https://'):
        msg = lbxd.get_crew_info(actor_url)
    else:
        msg = actor_url
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.command(aliases=['d'])
async def director(ctx, *, arg):
    director_url = lbxd.search_letterboxd(arg, "/directors/")
    if director_url.startswith('https://'):
        msg = lbxd.get_crew_info(director_url)
    else:
        msg = director_url
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.command(aliases=['movie', 'f'])
async def film(ctx, *, arg):
    film_link = lbxd.search_letterboxd(arg, "/films/")
    if film_link.startswith('https://'):
        msg = lbxd.get_info_film(film_link)
    else:
        msg = film_link
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.command(aliases=['l'])
async def list(ctx, user, *args):
    if len(args):
        msg = lbxd.find_list(user.strip(','), ' '.join(str(i) for i in args))
    else:
        msg = "This command requires at least 2 words,"
        msg += " the first for the username, and at least one more"
        msg += " for a list title."
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.command(aliases=['r'])
async def review(ctx, user, *args):
    if len(args):
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
    else:
        msg = "This command requires at least 2 words,"
        msg += " the first for the username, and at least one more"
        msg += " for a film title."
    if isinstance(msg, discord.Embed):
        await ctx.send(embed=msg)
    else:
        await ctx.send(msg)


@bot.command(name='del')
@commands.bot_has_permissions(manage_messages=True)
async def delete(ctx):
    message = ctx.message
    await message.delete()
    command_to_erase = lbxd.del_last_line(message.guild.id,
                                          message.channel.id)
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
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('This command requires a parameter.')
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send('{} is needed to use this command.'
                       .format(', '.join(err for err in error.missing_perms)))
    else:
        raise error


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        await bot.process_commands(message)
        if not isinstance(message.channel, discord.DMChannel):
            with open('history_{}.txt'.format(message.guild.id), 'a') as f:
                f.write(str(message.channel.id) + ' ' + str(message.id) + '\n')
            lbxd.limit_history(30, message.guild.id)
    else:
        # Redirects PMs to me
        if isinstance(message.channel, discord.DMChannel):
            porkepik = await bot.get_user_info(81412646271717376)
            await porkepik.send('`' + str(message.author)
                                + '`\n\n' + message.content)


@bot.event
async def on_message_edit(before, after):
    if after.author == bot.user:
        return

    if isinstance(after.channel, discord.DMChannel):
        porkepik = await bot.get_user_info(81412646271717376)
        await porkepik.send('**Edit**:\n`' + str(after.author)
                            + '`\n\n' + after.content)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)
