import discord, urllib.request, string
from bs4 import BeautifulSoup

TOKEN = 'PRIVATE-TOKEN'

client = discord.Client()

def search_letterboxd(message, search_type):
    list_words_message = message.content.split()
    msg = "Could not find anything."

    # If searching a film, and the last word is made of digits, checks whether a film page link exists using the name with a year of release or number
    if list_words_message[-1].isdigit() and search_type == "films/":
        try:
            contents = urllib.request.urlopen("https://letterboxd.com/film/{0}".format('-'.join(list_words_message[1:]))).read().decode('utf-8')
            return "https://letterboxd.com/film/{}".format('-'.join(list_words_message[1:]))
        except:
            pass

    try:
        contents = urllib.request.urlopen("https://letterboxd.com/search/{0}{1}".format(search_type, '+'.join(list_words_message[1:]))).read().decode('utf-8')
    except:
        return msg
    html_soup = BeautifulSoup(contents, "html.parser")

    # Gets the first result in the list
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

def get_info(link):
    msg = ""
    list_words_link = link.split('/')

    contents = urllib.request.urlopen(link).read().decode('utf-8')
    html_soup = BeautifulSoup(contents, "html.parser")
    info_html = html_soup.find(id="featured-film-header")
    info_h1 = info_html.find(class_="headline-1 js-widont prettify")

    # Gets the title and link
    name_film = list_words_link[4]
    msg += "**" + info_h1.contents[0] + "** <https://letterboxd.com/film/{}>".format(name_film.lower()) + '\n'

    # Gets the director and year of release
    a_html = info_html.find_all('a')
    msg += "Year: " + a_html[0].contents[0] + '\n'
    msg += "Director: " + a_html[1].contents[0].contents[0] + '\n'

    # Gets the country
    div_html = html_soup.find('div', id='tab-details')
    details_html = div_html.find_all('a')
    msg += "Country: "
    plural_country = 0
    for detail in details_html:
        if detail['href'].startswith("/films/country/"):
            msg += "{}, ".format(detail.contents[0])
            plural_country += 1
    if plural_country > 1:
        msg = msg.replace('Country', 'Countries')
    msg = msg[:-2] + '\n'

    # Gets the duration
    p_html = html_soup.find(class_="text-link text-footer")
    list_duration = p_html.contents[0].split()
    msg += ' '.join(list_duration[0:2]) + '\n'

    # Gets the total views
    views_html = html_soup.find(class_="has-icon icon-watched icon-16 tooltip")
    msg += views_html['title']

    return msg

def get_favs(message):
    list_words_message = message.content.split()
    msg = "This user does not have any favourites."

    try:
        contents = urllib.request.urlopen("https://letterboxd.com/{}".format(list_words_message[1])).read().decode('utf-8')
    except:
        msg = "Could not find this user."
        return msg

    html_soup = BeautifulSoup(contents, "html.parser")
    fav_html = html_soup.find(id="favourites")
    span_html = fav_html.find_all('span')
    fav_links = list()

    for div in fav_html.find_all('div'):
        fav_links.append(div['data-film-link'])

    if len(span_html) > 0:
        msg = "<https://letterboxd.com/{}> Letterboxd Favourite Films:\n\n".format(list_words_message[1])
    for index, span in enumerate(span_html):
        msg += "{}".format(span.contents)[2:-2]
        msg += ": <https://letterboxd.com{}>".format(fav_links[index][:-1]) + "\n"

    return msg

def limit_history(max_size, server_id):
    with open('history_{}.txt'.format(server_id)) as f:
        lines = f.readlines()
    if len(lines) > max_size:
        with open('history_{}.txt'.format(server_id), 'w') as f:
            f.writelines(lines[1:])

def del_last_line(server_id):
    command_to_erase = ""
    try:
        with open('history_{}.txt'.format(server_id)) as f:
            lines = f.readlines()
            if len(lines) == 0:
                return ""

        with open('history_{}.txt'.format(server_id), 'a') as f:
            f.seek(0)
            f.truncate()
            command_to_erase = lines[-1][:-1]
            f.writelines(lines[:-1])
    except FileNotFoundError:
        with open('history_{}.txt'.format(server_id), 'w') as f:
            pass

    return command_to_erase


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!'):
        msg = ""
        if message.content.startswith('!help'):
            msg += "Hello, I'm LetterBot. My owner is Porkepik#2664.\nI'm still experimental and I would appreciate feedback.\n\n__Commands__:\n\n"
            msg += "**!film/!movie/!user/!list/!actor/!director**:  Search the specified item on Letterboxd and returns the first result.\n\n"
            msg += "**!fav**:  Display the 4 favourite films of a Letterboxd member.\n\n"
            msg += "**!info**:  Display informations on a film. This command performs a search, meaning a partial title may work.\nExample: !info mood for love\n\n"
            msg += "**!del**:  Delete the last message the bot sent within a limit of the last 30 messages."
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
        elif message.content.startswith('!info '):
            film_link = search_letterboxd(message, "films/")
            msg = get_info(film_link) if len(film_link) > 0 else "Could not find anything."
        elif message.content.startswith('!del'):
            command_to_erase = del_last_line(message.server.id)
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

        if len(msg) > 0:
            with open('history_{}.txt'.format(message.server.id), 'a') as f:
                f.write(message.content + '\n')
            limit_history(20, message.server.id)
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

client.run(TOKEN)