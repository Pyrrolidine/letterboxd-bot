import discord, urllib.request
from bs4 import BeautifulSoup

def search_letterboxd(item, search_type):
    list_search_words = item.split()
    msg = "Could not find anything."

    # If searching a film, and the last word is made of digits, checks whether a film page link exists using the name with a year of release or number
    if list_search_words[-1].isdigit() and search_type == "films/":
        try:
            link = "https://letterboxd.com/film/{}".format('-'.join(list_search_words))
            contents = urllib.request.urlopen(link).read().decode('utf-8')
            return link
        except:
            pass

    try:
        contents = urllib.request.urlopen("https://letterboxd.com/search/{0}{1}".format(search_type, '+'.join(list_search_words))).read().decode('utf-8')
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

def get_info_film(link):
    msg = ""
    list_words_link = link.split('/')

    contents = urllib.request.urlopen(link).read().decode('utf-8')
    html_soup = BeautifulSoup(contents, "html.parser")
    info_html = html_soup.find(id="featured-film-header")
    info_h1 = info_html.find(class_="headline-1 js-widont prettify")

    name_film = list_words_link[4]
    a_html = info_html.find_all('a')

    # Gets the image URL
    poster_html = html_soup.find('div', id='poster-col')
    image_url = poster_html.find('img', class_='image')['src']

    # Gets the director
    try:
        msg += "**Director:** " + a_html[1].contents[0].contents[0] + '\n'
    except:
        pass

    # Gets the country
    div_html = html_soup.find('div', id='tab-details')
    details_html = div_html.find_all('a')
    country_str = "**Country:** "
    plural_country = 0
    for detail in details_html:
        if detail['href'].startswith("/films/country/"):
            country_str += "{}, ".format(detail.contents[0])
            plural_country += 1
    if plural_country > 1:
        country_str = country_str.replace('Country', 'Countries')
    if plural_country != 0:
        msg += country_str[:-2] + '\n'

    # Gets the duration
    p_html = html_soup.find(class_="text-link text-footer")
    list_duration = p_html.contents[0].split()
    if list_duration[1] == "mins":
        msg += '**Length:** ' + ' '.join(list_duration[0:2]) + '\n'

    # Gets the total views
    views_html = html_soup.find(class_="has-icon icon-watched icon-16 tooltip")
    msg += "Watched by " + views_html.contents[0] + " members"

    # Gets year
    year = ""
    try:
        year = ' (' + a_html[0].contents[0] + ')'
    except:
        pass
    # Creates an embed with title, url and thumbnail
    info_embed = discord.Embed(title=info_h1.contents[0] + year, description=msg, url="https://letterboxd.com/film/{}".format(name_film.lower()), colour=0xd8b437)
    info_embed.set_thumbnail(url=image_url)

    return info_embed

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
    a_html = fav_html.find_all('a')

    if 'title' not in a_html[0].attrs:
        return "{} does not have favourites.".format(list_words_message[1])

    if len(a_html) > 0:
        msg = "**[{0}](https://letterboxd.com/{0}) Letterboxd Favourite Films**\n\n".format(list_words_message[1].capitalize())
    for fav in a_html:
        msg += '[' + fav['title'] + ']'
        msg += "(https://letterboxd.com{})".format(fav['href'][:-1]) + '\n'

    # Gets the avatar
    img_div_html = html_soup.find('div', class_='profile-avatar')
    img_link = img_div_html.contents[1].contents[1]['src']

    fav_embed = discord.Embed(title='', description=msg, colour=0xd8b437)
    fav_embed.set_thumbnail(url=img_link)

    return fav_embed

def get_review(film, user):
    msg = ""
    film_name = ' '.join(film.split('-'))
    link = "https://letterboxd.com/{0}/film/{1}/activity".format(user, film)

    # Opens the activity page, if it fails, then the user doesn't exist because we already checked the film title in search_letterboxd
    try:
        contents = urllib.request.urlopen(link).read().decode('utf-8')
    except:
        msg = "{} doesn't exist.".format(user)
        return msg

    html_soup = BeautifulSoup(contents, "html.parser")
    activity_html = html_soup.find('div', class_="activity-table")

    if activity_html is None:
        return "{0} has not seen {1}.".format(user, film_name)

    rows_html = activity_html.find_all('section', class_="activity-row -basic")
    list_link = list()
    for row in rows_html:
        summary_html = row.find('p', class_="activity-summary")
        try:
            if summary_html.contents[3].contents[1].contents[0][1:].startswith('reviewed'):
                list_link.append(summary_html.contents[3]['href'])
        except:
            pass

    # Iterates through the review links found, if there are more than 4, shares a link to the activity page and doesn't display anymore links
    for index, review_link in enumerate(list_link[::-1]):
        if index > 3:
            msg += "More reviews: <{}>".format(link)
            break
        if index == 0:
            msg += "https://letterboxd.com{}\n".format(review_link)
        else:
            msg += "<https://letterboxd.com{}>\n".format(review_link)

    if len(list_link) == 0:
        return "{0} does not have a review for {1}.".format(user, film_name)
    return msg

def limit_history(max_size, server_id):
    # If there are more than max_size lines in the command history file (unique to each servers), deletes the oldest
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
        # Creates the file if it doesn't exist already
        with open('history_{}.txt'.format(server_id), 'w') as f:
            pass

    return command_to_erase

def check_lbxd():
    msg = "Letterboxd is up."
    try:
        content = urllib.request.urlopen("https://letterboxd.com")
    except urllib.error.HTTPError as e:
        msg = "Letterboxd is down."
    return msg