import discord, urllib.request, string
from bs4 import BeautifulSoup

TOKEN = 'PRIVATETOKEN'

client = discord.Client()

def search_letterboxd(message, search_type):
    list_words = message.content.split()
    msg = "Could not find anything."

    if list_words[-1].isdigit() and search_type == "films/":
        try:
            contents = urllib.request.urlopen("https://letterboxd.com/film/{0}".format('-'.join(list_words[1:]))).read().decode('utf-8')
            return "https://letterboxd.com/film/{}".format('-'.join(list_words[1:]))
        except:
            pass

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

def get_info(message, has_link):
    msg = ""
    list_words = list()
    if has_link:
        list_words.extend(message.split('/'))
    else:
        list_words = message.content.split()

    if has_link:
        contents = urllib.request.urlopen(message).read().decode('utf-8')
    else:
        try:
            contents = urllib.request.urlopen("https://letterboxd.com/film/{}".format('-'.join(list_words[1:]).lower())).read().decode('utf-8')
        except:
            msg = "Could not find this film."
            return msg

    html_soup = BeautifulSoup(contents, "html.parser")

    info_html = html_soup.find(id="featured-film-header")
    info_h1 = info_html.find(class_="headline-1 js-widont prettify")

    name_film = ""
    if has_link:
        name_film = list_words[4]
    else:
        name_film = list_words[1]

    msg += "**" + info_h1.contents[0] + "** <https://letterboxd.com/film/{}>".format(name_film.lower()) + '\n'

    # Gets the director and year of release
    a_html = info_html.find_all('a')
    msg += "Year: " + a_html[0].contents[0] + '\n'
    msg += "Director: " + a_html[1].contents[0].contents[0] + '\n'

    # Gets the duration
    p_html = html_soup.find(class_="text-link text-footer")
    list_duration = p_html.contents[0].split()
    msg += ' '.join(list_duration[0:2]) + '\n'

    views_html = html_soup.find(class_="has-icon icon-watched icon-16 tooltip")
    msg += views_html['title']

    return msg

def get_favs(message):
    list_words = message.content.split()
    msg = "This user does not have any favourites."

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
        msg = "<https://letterboxd.com/{}> Letterboxd Favourite Films:\n\n".format(list_words[1])
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
            msg = "Hello, I'm LetterBot. My owner is Porkepik#2664.\nI'm still experimental and would appreciate feedback.\n\n__Commands__:\n\n**!film/!movie/!user/!list/!actor/!director**:  Search the specified item on Letterboxd and returns the first result.\n\n**!fav**:  Display the 4 favourite films of a Letterboxd member.\n\n**!info**:  Display informations about a film. This command performs a search, meaning a partial title may work.\nExample: !info mood for love\n\n**!qinfo**:  Display informations about a film. This command requires to type the title exactly like the url, except for spaces instead of dashes.\nExample: !qinfo in the mood for love\n\n**!del**:  Delete the last message the bot sent within a limit of the last 30 messages."
        elif message.content.startswith('!fav '):
            msg = get_favs(message)
        elif message.content.startswith('!film ') or message.content.startswith('!movie '):
            msg = search_letterboxd(message, "films/")
        elif message.content.startswith('!user '):
            msg = search_letterboxd(message, "people/")
        elif message.content.startswith('!actor '):
            msg = search_letterboxd(message, "actors/")
        elif message.content.startswith('!director '):
            msg = search_letterboxd(message, "directors/")
        elif message.content.startswith('!list '):
            msg = search_letterboxd(message, "lists/")
        elif message.content.startswith('!qinfo '):
            msg = get_info(message, False)
        elif message.content.startswith('!info '):
            film_link = search_letterboxd(message, "films/")
            msg = get_info(film_link, True)
        elif message.content.startswith('!del'):
            async for log_message in client.logs_from(message.channel, limit=30):
                if log_message.author == client.user:
                    await client.delete_message(message)
                    await client.delete_message(log_message)
                    break

        if len(msg) > 0:
            await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
