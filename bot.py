import discord, urllib.request, string
from bs4 import BeautifulSoup

TOKEN = 'PRIVATETOKEN'

client = discord.Client()

def search_letterboxd(message, search_type):
    list_words = message.content.split()
    msg = "Could not find anything."

    try:
        contents = urllib.request.urlopen("https://letterboxd.com/search/{0}{1}".format(search_type, '+'.join(list_words[1:]))).read().decode('utf-8')
    except:
        msg = "404 Error with this search link."
        return msg
    html_soup = BeautifulSoup(contents, "html.parser")

    results_html = html_soup.find('ul', class_="results")
    if results_html is None:
        return msg

    if search_type == "films/":
        search_html = results_html.find('span', class_="film-title-wrapper")
    elif search_type == "people/":
        search_html = results_html.find('div', class_="person-summary -search")
    else:
        search_html = results_html.find('h2', class_="title-2 prettify")

    a_link = search_html.find('a')
    link = a_link['href']
    msg = "https://letterboxd.com{}".format(link)

    return msg

def get_favs(message):
    list_words = message.content.split()
    msg = "This user does not have any favourites."

    print("https://letterboxd.com/{}".format(list_words[1]))
    try:
        contents = urllib.request.urlopen("https://letterboxd.com/{}".format(list_words[1])).read().decode('utf-8')
    except:
        msg = "Could not find this user."
        return msg
    html_soup = BeautifulSoup(contents, "html.parser")

    fav_html = html_soup.find(id="favourites")
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
            msg = "Hello, I'm LetterBot. My owner is Porkepik#2664.\nI'm still experimental and would appreciate feedback.\n\n__Commands__:\n\n**!film/!user/!list/!actor/!director**:  Search the specified item on Letterboxd and returns the first result.\n\n**!fav**:  Displays the 4 favourite films of a Letterboxd member."
        elif message.content.startswith('!fav '):
            msg = get_favs(message)
        elif message.content.startswith('!film '):
            msg = search_letterboxd(message, "films/")
        elif message.content.startswith('!user '):
            msg = search_letterboxd(message, "people/")
        elif message.content.startswith('!actor '):
            msg = search_letterboxd(message, "actors/")
        elif message.content.startswith('!director '):
            msg = search_letterboxd(message, "directors/")
        elif message.content.startswith('!list '):
            msg = search_letterboxd(message, "lists/")

        if len(msg) > 0:
            await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
