import discord, urllib.request, string
from bs4 import BeautifulSoup

TOKEN = 'PRIVATETOKENHERE'

client = discord.Client()

def search_letterboxd(message, search_type):
    list_words = message.content.split()
    msg = "Could not find anything."

    contents = urllib.request.urlopen("https://letterboxd.com/search/{}".format(list_words[1:])).read().decode('utf-8')

    list_links = contents.split()

    for word in list_links:
        if word.startswith('href="/{}'.format(search_type)):
            msg = "https://letterboxd.com" + word[6:-2]

    return msg

def get_favs(message):
    list_words = message.content.split()
    msg = "Could not find the user's favourites."

    try:
        contents = urllib.request.urlopen("https://letterboxd.com/{}".format(list_words[1])).read().decode('utf-8')
    except:
        msg = "Could not find this user."
        return msg
    html_soup = BeautifulSoup(contents, "html.parser")

    fav_html = html_soup.find_all(id="favourites")[0]
    fav_span = fav_html.find_all('span')
    fav_links = list()

    for div in fav_html.find_all('div'):
        fav_links.append(div['data-film-link'])

    if len(fav_span) > 0:
        msg = ""
    for index, span in enumerate(fav_span):
        msg += "{}".format(span.contents)[2:-2]
        msg += ": <https://letterboxd.com{}>".format(fav_links[index][:-1])
        msg += "\n"

    return msg

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!'):
        msg = ""
        if message.content.startswith('!help'):
            msg = "Hello, I'm LetterBot. My owner is Porkepik#2664.\nI'm currently not providing any commands as we are working on API related issues."
        elif message.content.startswith('!fav '):
            msg = get_favs(message)
        elif message.content.startswith('!film '):
            #msg = search_letterboxd(message, "film/")
            msg = "Sorry, I'm currently broken. :sob:"
        elif message.content.startswith('!user '):
            #msg = search_letterboxd(message, "")
            msg = "Sorry, I'm currently broken. :sob:"
        elif message.content.startswith('!actor '):
            #msg = search_letterboxd(message, "actor/")
            msg = "Sorry, I'm currently broken. :sob:"
        elif message.content.startswith('!director '):
            #msg = search_letterboxd(message, "director/")
            msg = "Sorry, I'm currently broken. :sob:"
        elif message.content.startswith('!list '):
            #msg = search_letterboxd(message, "list")
            msg = "Sorry, I'm currently broken. :sob:"

        if len(msg) > 0:
            await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)