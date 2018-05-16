from .core import *


class List(object):

    def __init__(self, username, keywords):
        self.lists_url = "https://letterboxd.com/" + username + "/lists/"
        self.nb_films = ''
        self.poster_link = ''
        self.url = self.find_list(keywords)
        list_page_html = self.load_list_page()
        self.description = self.get_description(list_page_html)
        self.poster_url = self.get_thumbnail()

    def find_list(self, keywords):
        list_link = ''
        i = 1
        match = False

        while i <= 10:
            try:
                page = s.get(self.lists_url + 'page/{}'.format(i))
                page.raise_for_status()
            except requests.exceptions.HTTPError as err:
                if page.status_code == 404:
                    raise LbxdNotFound('The user does not exist.')
                print(err)
                raise LbxdServerError("There was a problem trying to access "
                                      + "Letterboxd.com.")

            lists_only = SoupStrainer('section', class_='list-set')
            lists_html = BeautifulSoup(page.text, 'lxml',
                                       parse_only=lists_only)

            user_lists = lists_html.find_all('div', class_='film-list-summary')
            if not len(user_lists):
                break

            for user_list in user_lists:
                self.list_name = user_list.find('h2').get_text().strip()
                list_link = "https://letterboxd.com"\
                            + user_list.find('a')['href']
                self.nb_films = user_list.find('small').get_text()

                for word in keywords.lower().split():
                    if word in self.list_name.lower():
                        match = True
                    else:
                        match = False
                        break

                if match:
                    self.poster_link = user_list.parent\
                                      .find('li')['data-target-link']
                    i = 20
                    break
            i += 1

        if i < 20:
            raise LbxdNotFound("Could not find a list matching those "
                               + "keywords within the first 10 pages.")
        return list_link

    def load_list_page(self):
        try:
            page = s.get(self.url)
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            raise LbxdServerError('There was a problem trying to access '
                                  + 'Letterboxd.com.')

        o_l = SoupStrainer('section',
                           class_='section col-17 col-main overflow clearfix')
        list_page_html = BeautifulSoup(page.text, 'lxml',
                                       parse_only=o_l)
        self.display_name = list_page_html.find('a', class_='name').contents[0]

        return list_page_html

    def get_description(self, list_page_html):
        description = "By **" + self.display_name.strip() + '**\n'\
                      + self.nb_films + '\n'
        description_text = list_page_html.find('div', class_='body-text')
        if description_text is not None:
            description += format_text(description_text, 300)
        return description

    def get_thumbnail(self):
        poster_link = "https://letterboxd.com" + self.poster_link + 'image-150'
        poster_page = s.get(poster_link)
        poster_html = BeautifulSoup(poster_page.text, 'lxml')
        return poster_html.find('img')['src']

    def create_embed(self):
        list_embed = discord.Embed(title=self.list_name, url=self.url,
                                   colour=0xd8b437,
                                   description=self.description)
        list_embed.set_thumbnail(url=self.poster_url)
        return list_embed
