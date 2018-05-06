import discord
import urllib.request
from bs4 import BeautifulSoup, SoupStrainer
import requests

s = requests.Session()


def search_letterboxd(item, search_type):
    list_search_words = item.split()
    msg = ""
    check_year = False

    if search_type == '/films/':
        if list_search_words[-1].startswith('year:') \
                or list_search_words[-1].startswith('y:') \
                or list_search_words[-1][0] == '(' \
                and list_search_words[-1][-1] == ')' \
                and list_search_words[-1][1:-1].isdigit():
            check_year = True

    # If searching a film, and the last word is made of digits:
    # checks whether a film page link exists using name-digits
    if not check_year and list_search_words[-1].isdigit() \
            and search_type == "/films/":
        try:
            path = urllib.parse.quote('-'.join(list_search_words).lower())
            link = "https://letterboxd.com/film/{}".format(path)
            page = s.get(link)
            page.raise_for_status()
            return link
        except requests.exceptions.HTTPError:
            pass

    try:
        if check_year:
            path = urllib.parse.quote('+'.join(list_search_words[:-1]))
        else:
            path = urllib.parse.quote('+'.join(list_search_words))
        page = s.get("https://letterboxd.com/search{0}{1}"
                     .format(search_type, path))
        page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.code == 404:
            return "Could not find the film."
        else:
            print(err)
            return "There was a problem trying to access Letterboxd.com"

    # Fetch the results, if none then exits
    html_soup = BeautifulSoup(page.text, "lxml")
    results_html = html_soup.find('ul', class_='results')
    if results_html is None:
        return "No results were found with this search."

    if search_type == "/films/":
        if check_year:
            films_html = results_html.find_all('li')
            for index, search in enumerate(films_html):
                if index > 4:
                    break
                film_html = search.find('span', class_="film-title-wrapper")
                year_html = film_html.find('small', class_='metadata')
                if year_html is not None:
                    year = year_html.find('a').contents[0]
                else:
                    continue
                if year == list_search_words[-1].split(':')[-1]\
                        .strip('(').strip(')'):
                    link = film_html.find('a')['href']
                    return "https://letterboxd.com{}".format(link)
        search_html = results_html.find('span', class_='film-title-wrapper')
    else:
        search_html = results_html.find('h2', class_="title-2 prettify")

    link = search_html.find('a')['href']
    msg = "https://letterboxd.com{}".format(link)

    return msg


def get_info_film(link):
    msg = ""
    list_words_link = link.split('/')

    page = s.get(link)
    contents_only = SoupStrainer('div', id='film-page-wrapper')
    html_soup = BeautifulSoup(page.text, "lxml",
                              parse_only=contents_only)
    info_html = html_soup.find('section', id="featured-film-header")
    info_h1 = info_html.find(class_="headline-1 js-widont prettify")

    name_film = list_words_link[4]

    # Gets the image URL
    poster_html = html_soup.find('div', id='poster-col')
    image_url = poster_html.find('img', class_='image')['src']

    # Gets the director
    try:
        director = info_html.find('a', itemprop='director').find('span')
        msg += "**Director:** " + director.contents[0] + '\n'
    except AttributeError:
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
    views_html = html_soup.find(class_="icon-watched")
    msg += "Watched by " + views_html.contents[0] + " members"

    # Gets year
    year = ''
    try:
        year_html = info_html.find('small', itemprop='datePublished').find('a')
        year = ' (' + year_html.contents[0] + ')'
    except AttributeError:
        pass

    # Creates an embed with title, url and thumbnail
    info_embed = discord.Embed(title=info_h1.contents[0] + year,
                               description=msg,
                               url="https://letterboxd.com/film/{}"
                               .format(name_film.lower()),
                               colour=0xd8b437)
    info_embed.set_thumbnail(url=image_url)

    return info_embed


def get_user_info(message):
    user = message.content.split()[1]

    try:
        page = s.get("https://letterboxd.com/{}".format(user))
        page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.code == 404:
            return "Could not find this user."
        else:
            print(err)
            return "There was a problem trying to access Letterboxd.com"

    contents_only = SoupStrainer('div', class_='content-wrap')
    html_soup = BeautifulSoup(page.text, "lxml",
                              parse_only=contents_only)

    # Gets the display name
    name_div_html = html_soup.find('div', class_='profile-person-info')
    display_name = name_div_html.find('h1', class_='title-1').contents[0]

    msg = ""

    # Gets metadata
    metadata_html = html_soup.find('ul', class_='person-metadata')
    if metadata_html is not None:
        try:
            location = metadata_html.find('li', class_='icon-location')\
                    .get_text()
            if isinstance(location, str):
                msg += '**' + location + '** -- '
        except AttributeError:
            pass

    # Gets amout of films viewed
    nbfilms_html = html_soup.find('ul', class_='stats')
    nbfilms = nbfilms_html.find('a').contents[0].contents[0]
    msg += "**" + nbfilms + " films**\n"

    # Gets favourites
    fav_html = html_soup.find(id="favourites")
    a_html = fav_html.find_all('a')

    if len(a_html) > 0:
        msg += '**Favourite Films**:\n'
    for fav in a_html:
        msg += '[' + fav['title'] + ']'
        msg += "(https://letterboxd.com{})".format(fav['href'][:-1]) + '\n'

    # Gets the avatar
    img_div_html = html_soup.find('div', class_='profile-avatar')
    img_link = img_div_html.find('img')['src']

    user_embed = discord.Embed(title=display_name,
                               url="https://letterboxd.com/{}".format(user),
                               description=msg,
                               colour=0xd8b437)
    user_embed.set_thumbnail(url=img_link)

    return user_embed


def get_crew_info(crew_url):
    msg = ""
    page = s.get(crew_url)
    contents_only = SoupStrainer('div', class_='content-wrap')
    html_soup = BeautifulSoup(page.text, "lxml",
                              parse_only=contents_only)

    # Gets the display name
    name_div_html = html_soup.find('div', class_='contextual-title')
    display_name = name_div_html.find('h1',
                                      class_='title-1 prettify').contents[2]

    # Gets film credits, if the person has done at least 2 types of them
    menu_html = html_soup.find('section',
                               class_='smenu-wrapper smenu-wrapper-left')
    has_multiple_jobs = False
    if menu_html is not None:
        has_multiple_jobs = True
        jobs_html = list()
        jobs_html.append(menu_html.find('span'))
        jobs_html.extend(menu_html.find_all('a'))
        for job in jobs_html:
            job_title = job.contents[0].strip()
            if job_title in ['Director', 'Writer', 'Actor', 'Producer']:
                msg += '**' + job_title + '**: '
                try:
                    msg += job.contents[1].contents[0] + '\n'
                except IndexError:
                    msg += '1\n'

    # Goes to the TMDB page
    sidebar_html = html_soup.find('aside', class_='sidebar')
    tmdb_url = sidebar_html.find('a', class_='micro-button')['href']
    try:
        page_tmdb = s.get(tmdb_url)
        page_tmdb.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.code == 404:
            return "This person does not have a TMDb page."
        else:
            print(err)
            return "There was a problem trying to access TMDb"
    tmdb_html_soup = BeautifulSoup(page_tmdb.text, "lxml")

    # Gets informations
    facts_html = tmdb_html_soup.find('section', class_='facts left_column')
    if facts_html is not None:
        infos_html = facts_html.find_all('p')
        for info in infos_html:
            try:
                info_type = info.find('bdi').contents[0]
            except AttributeError:
                continue
            if info_type in ['Birthday', 'Day of Death', 'Place of Birth']\
                    and info.contents[1].strip() != '-'\
               or info_type == 'Known Credits' and not has_multiple_jobs:
                msg += "**" + info_type + "**: " + info.contents[1] + '\n'

    crew_embed = discord.Embed(title=display_name, url=crew_url,
                               description=msg, colour=0xd8b437)

    # Gets the picture
    try:
        img_link = tmdb_html_soup.find('img', class_='poster')['src']
        crew_embed.set_thumbnail(url=img_link)
    except TypeError:
        pass

    return crew_embed


def get_review(film, user):
    msg = ""
    link = "https://letterboxd.com/{0}/film/{1}/activity".format(user, film)

    # Opens the activity page, if it fails, the user doesn't exist
    # We already checked the film title in search_letterboxd
    try:
        page = s.get(link)
        page.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.code == 404:
            return "{} doesn't exist.".format(user)
        else:
            print(err)
            return "There was a problem trying to access Letterboxd.com"

    contents_only = SoupStrainer('div', class_="content-wrap")
    html_soup = BeautifulSoup(page.text, "lxml",
                              parse_only=contents_only)
    activity_html = html_soup.find('div', class_="activity-table")
    name_html = html_soup.find('h1', class_='headline-2')
    film_name = name_html.contents[3].contents[0]

    if activity_html is None:
        return "{0} has not seen {1}.".format(user, film_name)

    rows_html = activity_html.find_all('section', class_="activity-row -basic")
    try:
        display_name = rows_html[0].find('a', class_='avatar')\
                .contents[1]['alt']
    except AttributeError:
        pass

    n_reviews = 0
    review_link = ""

    for row in rows_html:
        summary_html = row.find('p', class_="activity-summary")
        activity_type = summary_html.find('span', class_='context')
        if activity_type is None:
            break

        if not activity_type.get_text().strip().startswith('reviewed'):
            continue

        n_reviews += 1
        # Shares a link to the activity page if more than 5 reviews
        if n_reviews > 5:
            msg += '[More reviews]({})'.format(link)
            break
        rating = summary_html.find('span', class_="rating")
        date = summary_html.find('span', class_="nobr")
        review_link = "https://letterboxd.com"\
            + summary_html.contents[3]['href']
        msg += '[**Review**]({0}) '.format(review_link)
        msg += rating.contents[0] + '  ' if rating is not None else ''
        msg += date.contents[0] if date is not None else ''
        msg += '\n'

        # Gets a preview of the first review
        if n_reviews > 1:
            continue

        review = ""
        try:
            page_review = s.get(review_link)
            page_review.raise_for_status()
        except requests.exceptions.HTTPError:
            continue
        review_only = SoupStrainer('div', itemprop="reviewBody")
        review_preview = BeautifulSoup(page_review.text, "lxml",
                                       parse_only=review_only)
        for br in review_preview.find_all('br'):
            br.replace_with('\n')
        for paragraph in review_preview.find_all('p'):
            for index, text in enumerate(paragraph.get_text().split('\n')):
                if index > 10:
                    break
                review += text.strip() + '\n'
            review += '\n'
        msg += '\n```' + review[:400].strip()
        if len(review) > 400:
            msg += '...'
        msg += '```'

    if len(msg) == 0:
        return "{0} does not have a review for {1}.".format(user, film_name)

    # Gets the film poster
    poster_html = html_soup.find('section', class_='poster-list')
    poster_url = poster_html.find('img')['src']

    review_word = 'reviews' if n_reviews > 1 else 'review'
    embed_link = link if n_reviews > 1 else review_link

    review_embed = discord.Embed(title="{0} {1} of {2}".format(display_name,
                                 review_word, film_name),
                                 url=embed_link, colour=0xd8b437,
                                 description=msg)
    review_embed.set_thumbnail(url=poster_url)

    return review_embed


def limit_history(max_size, server_id):
    # If there are more than max_size lines
    # in the command history file (unique to each servers), deletes the oldest
    with open('history_{}.txt'.format(server_id)) as f:
        lines = f.readlines()
    if len(lines) > max_size:
        with open('history_{}.txt'.format(server_id), 'w') as f:
            f.writelines(lines[1:])


def del_last_line(server_id, channel_id):
    msg_id_to_erase = ""
    try:
        with open('history_{}.txt'.format(server_id)) as f:
            lines = f.readlines()
            if len(lines) == 0:
                return ""

        with open('history_{}.txt'.format(server_id), 'a') as f:
            f.seek(0)
            f.truncate()
            for index, line in enumerate(lines[::-1]):
                if line.split(' ')[0] == channel_id:
                    msg_id_to_erase = lines.pop(-1-index).split()[1]
                    break
            f.writelines(lines)
    except FileNotFoundError:
        # Creates the file if it doesn't exist already
        with open('history_{}.txt'.format(server_id), 'w') as f:
            pass

    return msg_id_to_erase


def check_lbxd():
    msg = "Letterboxd is up."
    try:
        page = s.get("https://letterboxd.com")
        page.raise_for_status()
    except requests.exceptions.HTTPError:
        msg = "Letterboxd is down."
    return msg
