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
        await client.send_message(porkepik, str(message.author)
                                  + '\n__Message__:\n\n' + message.content)
        return

    if not message.content.startswith('!'):
        return

    msg = ""
    list_cmd_words = message.content.split()

    if message.content in ['!helplb', '!helpletterboxd', '!helplbxd']:
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
        actor_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]),
                                           "/actors/")
        msg = lbxd.get_crew_info(actor_url) \
            if actor_url.startswith('https://letterboxd.com') \
            else "Could not find this actor."

    elif list_cmd_words[0] in ['!director', '!d']:
        director_url = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]),
                                              "/directors/")
        msg = lbxd.get_crew_info(director_url) \
            if director_url.startswith('https://letterboxd.com') \
            else "Could not find this director."

    elif list_cmd_words[0] in ['!review', '!r']:
        if len(list_cmd_words) > 2:
            film_link = lbxd.search_letterboxd(' '.join(list_cmd_words[2:]),
                                               "/films/")
            if film_link.startswith("https://letterboxd.com"):
                split_film_link = film_link.split('/')
                film = split_film_link[-1] \
                    if len(split_film_link[-1]) > 0 \
                    else split_film_link[-2]
                msg = lbxd.get_review(film, list_cmd_words[1].strip(','))
            else:
                msg = "Could not find the film."
        else:
            msg = "This command requires at least 2 words,"
            msg += " the first for the username, and at least one more"
            msg += " for a film title."

    elif list_cmd_words[0] in ['!film', '!movie', '!f']:
        film_link = lbxd.search_letterboxd(' '.join(list_cmd_words[1:]),
                                           "/films/")
        msg = lbxd.get_info_film(film_link) \
            if film_link.startswith('https://letterboxd.com') \
            else "Could not find the film."

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
