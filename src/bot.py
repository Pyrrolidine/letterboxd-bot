import discord
import lbxd

token_file = open('Token')
TOKEN = token_file.readline().strip()

client = discord.Client()
porkepik = discord.User()
porkepik.id = '81412646271717376'


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Redirects PMs to me
    if message.channel.is_private:
        await client.send_message(porkepik, '`' + str(message.author)
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
        await client.delete_message(message)
        command_to_erase = lbxd.del_last_line(message.server.id,
                                              message.channel.id)
        deleted_message = False
        async for log_message in client.logs_from(message.channel, limit=30):
            if log_message.author == client.user and not deleted_message:
                deleted_message = True
                await client.delete_message(log_message)
                if not len(command_to_erase):
                    break
            if log_message.id == command_to_erase:
                await client.delete_message(log_message)
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
        with open('history_{}.txt'.format(message.server.id), 'a') as f:
            f.write(message.channel.id + ' ' + message.id + '\n')
        lbxd.limit_history(20, message.server.id)
        if isinstance(msg, discord.Embed):
            await client.send_message(message.channel, embed=msg)
        else:
            await client.send_message(message.channel, msg)


@client.event
async def on_message_edit(before, after):
    if after.channel.is_private:
        await client.send_message(porkepik, '**Edit**:\n`' + str(after.author)
                                  + '`\n\n' + after.content)
        return


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    await client.change_presence(game=discord.Game(name='Say !helplb'))

client.run(TOKEN)
