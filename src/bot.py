import discord
from discord.ext import commands
import lbxd

token_file = open('Token')
TOKEN = token_file.readline().strip()

bot = commands.Bot(command_prefix='!', case_insensitive=True)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Redirects PMs to me
    if isinstance(message.channel, discord.DMChannel):
        porkepik = await bot.get_user_info(81412646271717376)
        await porkepik.send('`' + str(message.author)
                            + '`\n\n' + message.content)
        return

    if not message.content.startswith('!'):
        return

    msg = ""
    list_cmd_words = message.content.split()

    if message.content == '!helplb':
        help_file = open('help.txt')
        msg = ''.join(help_file.readlines())

    elif message.content == '!checklb':
        msg = lbxd.check_lbxd()

    elif message.content == '!del':
        await message.delete()
        command_to_erase = lbxd.del_last_line(message.guild.id,
                                              message.channel.id)
        deleted_message = False
        async for log_message in message.channel.history(limit=30):
            if log_message.author == bot.user and not deleted_message:
                deleted_message = True
                await log_message.delete()
                if not len(command_to_erase):
                    break
            if str(log_message.id) == command_to_erase:
                await log_message.delete()
                break

    elif len(list_cmd_words) < 2:
        return

    elif list_cmd_words[0] in ['!user', '!u']:
        msg = lbxd.get_user_info(message)

    elif list_cmd_words[0] in ['!actor', '!a']:
        actor_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]),
                                           "/actors/")
        if actor_url.startswith('https://'):
            msg = lbxd.get_crew_info(actor_url)
        else:
            msg = actor_url

    elif list_cmd_words[0] in ['!list', '!l']:
        if len(list_cmd_words) > 2:
            msg = lbxd.find_list(list_cmd_words[1].strip(','),
                                 ' '.join(list_cmd_words[2:]))
        else:
            msg = "This command requires at least 2 words,"
            msg += " the first for the username, and at least one more"
            msg += " for a list title."

    elif list_cmd_words[0] in ['!director', '!d']:
        director_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]),
                                              "/directors/")
        if director_url.startswith('https://'):
            msg = lbxd.get_crew_info(director_url)
        else:
            msg = director_url

    elif list_cmd_words[0] in ['!review', '!r']:
        if len(list_cmd_words) > 2:
            film_link = lbxd.search_letterboxd(' '.join(list_cmd_words[2:]),
                                               "/films/")
            if film_link.startswith("https://letterboxd.com"):
                split_film_link = film_link.split('/')
                if len(split_film_link[-1]) > 0:
                    film = split_film_link[-1]
                else:
                    film = split_film_link[-2]
                msg = lbxd.get_review(film, list_cmd_words[1].strip(','))
            else:
                msg = film_link
        else:
            msg = "This command requires at least 2 words,"
            msg += " the first for the username, and at least one more"
            msg += " for a film title."

    elif list_cmd_words[0] in ['!film', '!movie', '!f']:
        film_link = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]),
                                           "/films/")
        if film_link.startswith('https://'):
            msg = lbxd.get_info_film(film_link)
        else:
            msg = film_link

    # Checks if a message is an embed and isn't empty before sending something
    if isinstance(msg, discord.Embed) or len(msg) > 0:
        with open('history_{}.txt'.format(message.guild.id), 'a') as f:
            f.write(str(message.channel.id) + ' ' + str(message.id) + '\n')
        lbxd.limit_history(20, message.guild.id)
        if isinstance(msg, discord.Embed):
            await message.channel.send(embed=msg)
        else:
            await message.channel.send(msg)


@bot.event
async def on_message_edit(before, after):
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

    bot.activity = discord.Game(name='Say !helplb')

bot.run(TOKEN)
