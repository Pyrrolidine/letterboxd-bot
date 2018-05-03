import discord, lbxd

token_file = open('Token')
TOKEN = token_file.readline().strip()

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith('!'):
        return

    msg = ""
    list_cmd_words = message.content.split()
    if message.content in ['!helplb', '!helpletterboxd', '!helplbxd']:
        msg += "Hello, I'm LetterboxdBot. My owner is Porkepik#2664.\nI'm still experimental and I would appreciate feedback."
        msg += "\n\n---------------\nCommands\n---------------\n\n"
        msg += "**!film/!movie/!f <film-name> (<year>)**\n\nSearch a film on Letterboxd. The year is optional and can also be specified with y: instead of parentheses.\n__Example__: !film man knew too much y:1934\nReturns the 1934 original Hitchock film, not specifying the year returns the more popular 50's film.\n\n"
        msg += "**!director/!d/!actor/!a <name>**\n\nSearch a filmmaker or an actor.\n\n"
        msg += "**!user/!u <username>**\n\nDisplay informations and the featured favourite films of a Letterboxd member. It requires the Letterboxd username, not the display name.\n\n"
        msg += "**!review/!r <username> <film-name> (<year>)**\n\nDisplay the reviews of a film from a specified user. The year is optional.\n__Example__: !review porkepik floating weeds (1934)\nReturns Porkepik's review of A Story of Floating Weeds (1934)\n\n"
        msg += "**!checklb**\n\nCheck letterboxd.com to see if the website is down.\n\n"
        msg += "**!del**\n\nDelete the last message the bot sent within a limit of the last 30 messages. The bot requires the \"manage messages\" permission."
    elif message.content == '!checklb':
        msg = lbxd.check_lbxd()
    elif message.content == '!del':
        await client.delete_message(message)
        command_to_erase = lbxd.del_last_line(message.server.id, message.channel.id)
        deleted_message = False
        async for log_message in client.logs_from(message.channel, limit=30):
            if log_message.author == client.user and deleted_message == False:
                deleted_message = True
                await client.delete_message(log_message)
                if len(command_to_erase) == 0:
                    break
            if log_message.id == command_to_erase:
                await client.delete_message(log_message)
                break
    elif len(list_cmd_words) < 2:
        return
    elif list_cmd_words[0] in ['!user', '!fav', '!u']:
        msg = lbxd.get_user_info(message)
    elif list_cmd_words[0] in ['!actor', '!a']:
        actor_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]), "actors/")
        msg = lbxd.get_crew_info(actor_url) if actor_url.startswith('https://letterboxd.com') else "Could not find this actor."
    elif list_cmd_words[0] in ['!director', '!d']:
        director_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]), "directors/")
        msg = lbxd.get_crew_info(director_url) if director_url.startswith('https://letterboxd.com') else "Could not find this director."
    elif list_cmd_words[0] in ['!review', '!r']:
        if len(list_cmd_words) > 2:
            film_link = lbxd.search_letterboxd(' '.join(list_cmd_words[2:]), "films/")
            if film_link.startswith("https://letterboxd.com"):
                split_film_link = film_link.split('/')
                film = split_film_link[-1] if len(split_film_link[-1]) > 0 else split_film_link[-2]
                msg = lbxd.get_review(film, list_cmd_words[1].strip(','))
            else:
                msg = "Could not find the film."
        else:
            msg = "This command requires at least 2 words, the first for the username, and at least one more for a film title."
    elif list_cmd_words[0] in ['!film', '!movie', '!f']:
        film_link = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]), "films/")
        msg = lbxd.get_info_film(film_link) if film_link.startswith('https://letterboxd.com') else "Could not find the film."

    # Checks if a message is an embed, and if it isn't empty before sending something
    if isinstance(msg, discord.Embed) or len(msg) > 0:
        with open('history_{}.txt'.format(message.server.id), 'a') as f:
            f.write(message.channel.id + ' ' + message.id + '\n')
        lbxd.limit_history(20, message.server.id)
        if isinstance(msg, discord.Embed):
            await client.send_message(message.channel, embed=msg)
        else:
            await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print('Connected on:')
    for server in client.servers:
        print(server)
    print('------')

    await client.change_presence(game=discord.Game(name='Say !helplb'))

client.run(TOKEN)
