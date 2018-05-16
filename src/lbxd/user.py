from .core import *


class User(object):

    def __init__(self, username):
        self.url = "https://letterboxd.com/{}".format(username)
        self.profile_html = self.load_profile()
        self.display_name = self.get_display_name()
        self.description = self.get_metadata()
        self.description += self.get_nb_films_viewed()
        self.description += self.get_favourites()
        self.avatar_url = self.get_avatar()

    def load_profile(self):
        try:
            page = s.get(self.url)
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if page.status_code == 404:
                raise LbxdNotFound('Could not find this user.')
            print(err)
            raise LbxdServerError('There was a problem trying to access'
                                  + ' Letterboxd.com')

        contents_only = SoupStrainer('div', class_='content-wrap')
        return BeautifulSoup(page.text, "lxml", parse_only=contents_only)

    def get_display_name(self):
        name_div_html = self.profile_html.find('div',
                                               class_='profile-person-info')
        return name_div_html.find('h1', class_='title-1').contents[0]

    def get_metadata(self):
        metadata_html = self.profile_html.find('ul', class_='person-metadata')
        if metadata_html is not None:
            location_html = metadata_html.find('li', class_='icon-location')
            if location_html is not None:
                location = location_html.get_text()
                if isinstance(location, str):
                    return '**' + location + '** -- '
        return ''

    def get_nb_films_viewed(self):
        nbfilms_html = self.profile_html.find('ul', class_='stats')
        nbfilms = nbfilms_html.find('a').contents[0].contents[0]
        return "**" + nbfilms + " films**\n"

    def get_favourites(self):
        fav_text = ''
        fav_html = self.profile_html.find(id="favourites")
        a_html = fav_html.find_all('a')

        if a_html[0].get('title') is not None:
            fav_text += '**Favourite Films**:\n'
            for fav in a_html:
                fav_text += '[' + fav['title'] + ']'
                fav_text += "(https://letterboxd.com{})"\
                            .format(fav['href'][:-1]) + '\n'

        return fav_text

    def get_avatar(self):
        img_div_html = self.profile_html.find('div', class_='profile-avatar')
        return img_div_html.find('img')['src']

    def create_embed(self):
        user_embed = discord.Embed(title=self.display_name, url=self.url,
                                   description=self.description,
                                   colour=0xd8b437)
        user_embed.set_thumbnail(url=self.avatar_url)

        return user_embed
