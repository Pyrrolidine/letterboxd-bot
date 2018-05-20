from .core import *


class Film(object):

    def __init__(self, keywords, with_info=True):
        self.has_year = False
        self.year = ''
        self.input_year = self.check_year(keywords)
        search_response = self.load_tmdb_search(keywords)
        self.tmdb_id = self.get_tmdb_id(search_response)
        lbxd_page = self.get_lbxd_page()
        self.poster_path = self.get_poster()
        if with_info:
            self.description = self.get_credits()
            self.description += self.get_details()
            self.description += self.get_views(lbxd_page)

    def check_year(self, keywords):
        last_word = keywords.split()[-1]
        if not last_word.isdigit():
            last_word = last_word.lower().replace('y:', '')
            last_word = last_word.replace('(', '').replace(')', '')
            if last_word.isdigit():
                self.has_year = True
                return last_word

    def load_tmdb_search(self, keywords):
        api_url = "https://api.themoviedb.org/3/search/movie?api_key="\
                  + api_key
        if self.has_year:
            keywords = ' '.join(keywords.split()[:-1])
        query = urllib.parse.quote_plus(keywords)
        api_url += "&query=" + query
        api_url += "&year=" + self.input_year if self.has_year else ''

        try:
            search_results = s.get(api_url)
            search_results.raise_for_status()
            return search_results
        except requests.exceptions.HTTPError as err:
            print(err)
            print('LINK:' + api_url)
            raise LbxdServerError("There was a problem trying to access TMDb.")

    def get_tmdb_id(self, search_response):
        if len(search_response.json()['results']):
            film_json = search_response.json()['results'][0]
            self.title = film_json['title']
            return str(film_json['id'])
        else:
            raise LbxdNotFound("There were no results with this search.")

    def get_credits(self):
        api_url = "https://api.themoviedb.org/3/movie/" + self.tmdb_id
        api_url += "/credits?api_key=" + api_key
        try:
            tmdb_credits = s.get(api_url)
            tmdb_credits.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print('LINK:' + api_url)
            raise LbxdServerError("There was a problem trying to access TMDb.")

        description = "**Director**: "
        nb_directors = 0
        for crew_member in tmdb_credits.json()['crew']:
            if crew_member['job'] == 'Director':
                nb_directors += 1
                if nb_directors > 1:
                    description = description.replace('irector*', 'irectors*')
                    description += ', '
                description += crew_member['name']
        if nb_directors:
            return description + '\n'
        return ''

    def get_details(self):
        api_url = "https://api.themoviedb.org/3/movie/" + self.tmdb_id
        api_url += "?api_key=" + api_key
        try:
            tmdb_info = s.get(api_url)
            tmdb_info.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print('LINK:' + api_url)
            raise LbxdServerError("There was a problem trying to access TMDb.")

        self.release_date = tmdb_info.json()['release_date']
        if self.release_date is not None:
            self.year = self.release_date.split('-')[0]

        self.runtime = tmdb_info.json()['runtime']
        self.countries = tmdb_info.json()['production_countries']
        description = ''
        if len(self.countries):
            description += '**Country**: '
            for index, country in enumerate(self.countries):
                if index:
                    description = description.replace('Country**',
                                                      'Countries**')
                    description += ', '
                description += country['name']
            description += '\n'
        if self.runtime is not None:
            description += '**Length**: ' + str(self.runtime) + ' mins'
            if self.runtime == 1:
                description = description.replace('mins', 'min')
            description += '\n'

        return description

    def get_lbxd_page(self):
        lbxd_link = "https://letterboxd.com/tmdb/" + self.tmdb_id
        try:
            page = s.get(lbxd_link)
            page.raise_for_status()
            self.lbxd_url = page.url
        except requests.exceptions.HTTPError as err:
            if page.status_code == 404:
                raise LbxdNotFound("This film doesn't have a Letterboxd page.")
            print(err)
            raise LbxdServerError("There was a problem trying to access "
                                  + "Letterboxd.")
        return page

    def get_views(self, page):
        stats_only = SoupStrainer('ul', class_='film-stats')
        stats_html = BeautifulSoup(page.text, "lxml", parse_only=stats_only)

        views_html = stats_html.find(class_="icon-watched")
        return "Watched by " + views_html.contents[0] + " members"

    def get_poster(self):
        try:
            page = s.get(self.lbxd_url + 'image-150')
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if page.status_code == 404:
                raise LbxdNotFound("This film doesn't have a Letterboxd page.")
            print(err)
            raise LbxdServerError("There was a problem trying to access "
                                  + "Letterboxd.")
        image_html = BeautifulSoup(page.text, 'lxml')
        return image_html.find('img')['src']

    def create_embed(self):
        title = self.title
        title += ' (' + self.year + ')' if len(self.year) else ''
        film_embed = discord.Embed(title=title, description=self.description,
                                   url=self.lbxd_url, colour=0xd8b437)
        film_embed.set_thumbnail(url=self.poster_path)

        return film_embed
