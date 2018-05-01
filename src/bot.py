import discord, lbxd

TOKEN = 'PRIVATE-TOKEN'

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
        msg += "Hello, I'm {}. My owner is Porkepik#2664.\nI'm still experimental and I would appreciate feedback.\n\n__Commands__:\n\n".format(client.user.display_name)
        msg += "**!film/!movie/!actor/!director**:  Search the specified item on Letterboxd and returns the first result.\n\n"
        msg += "**!user**:  Display informations and the featured favourite films of a Letterboxd member. It requires the Letterboxd username, not the display name.\n\n"
        msg += "**!review**: Display the reviews of a film from a specified user. The first word should be the username, then keywords for the film title. An optional comma can be added after the username for readability.\nExample:\n!review porkepik story floating weeds\n!review porkepik, story floating weeds\nBoth return Porkepik's review of A Story of Floating Weeds (1934)\n\n"
        msg += "**!checklb**: Check letterboxd.com to see if the website is down.\n\n"
        msg += "**!del**:  Delete the last message the bot sent within a limit of the last 30 messages. The bot requires the \"manage messages\" permission."
    elif message.content.startswith('!user ') or message.content.startswith('!fav '):
        msg = lbxd.get_user_info(message)
    elif message.content.startswith('!actor '):
        actor_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]), "actors/")
        msg = lbxd.get_crew_info(actor_url) if actor_url.startswith('https://letterboxd.com') else "Could not find this actor."
    elif message.content.startswith('!director '):
        director_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]), "directors/")
        msg = lbxd.get_crew_info(director_url) if director_url.startswith('https://letterboxd.com') else "Could not find this director."
    elif message.content.startswith('!review '):
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
    elif message.content == '!checklb':
        msg = lbxd.check_lbxd()
    elif message.content.startswith('!film ') or message.content.startswith('!movie '):
        film_link = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]), "films/")
        msg = lbxd.get_info_film(film_link) if film_link.startswith('https://letterboxd.com') else "Could not find the film."
    elif message.content.startswith('!del'):
        command_to_erase = lbxd.del_last_line(message.server.id, message.channel.id)
        deleted_message = False
        async for log_message in client.logs_from(message.channel, limit=30):
            if log_message.author == client.user and deleted_message == False:
                await client.delete_message(message)
                deleted_message = True
                await client.delete_message(log_message)
                if len(command_to_erase) == 0:
                    break
            if log_message.content == command_to_erase:
                await client.delete_message(log_message)
                break

    # Checks if a message is an embed, and if it isn't empty before sending something
    if isinstance(msg, discord.Embed) or len(msg) > 0:
        with open('history_{}.txt'.format(message.server.id), 'a') as f:
            f.write(message.channel.id + message.content + '\n')
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
