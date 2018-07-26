from .core import *


class Film(object):

    def __init__(self, keywords, with_info=True, is_metropolis=False):
        self.has_year = False
        self.fix_search = False
        self.year = ''
        self.input_year = self.check_year(keywords)
        self.tmdb_id = self.check_if_fixed_search(keywords)
        self.search_request(keywords)
        if not self.fix_search:
            if self.has_year:
                search_response = self.load_tmdb_search(keywords)
                self.tmdb_id = self.get_tmdb_id(search_response, keywords)
        if not with_info:
            return
        self.description = self.create_description()
        if is_metropolis:
            self.description += self.get_mkdb_rating()

    def check_year(self, keywords):
        last_word = keywords.split()[-1]
        if not last_word.isdigit():
            last_word = last_word.lower().replace('y:', '')
            last_word = last_word.replace('(', '').replace(')', '')
            if last_word.isdigit():
                self.has_year = True
                return last_word

    def check_if_fixed_search(self, keywords):
        with open('film_search_fix.txt') as fix_file:
            for line in fix_file:
                for title in line.strip().split('/'):
                    if title.lower() == keywords.lower():
                        id_line = next(fix_file).strip().split('/')
                        self.title = id_line[1]
                        self.fix_search = True
                        return id_line[0]
        return ''

    def search_request(self, keywords):
        params = {'input': keywords,
                  'include': 'FilmSearchItem'}
        response = api.api_call('search', params)
        film_json = response.json()['items'][0]['film']
        self.lbxd_id = film_json['id']
        self.title = film_json['name']
        try:
            self.year = film_json['releaseYear']
        except KeyError:
            self.year = 0
        for link in film_json['links']:
            if link['type'] == 'letterboxd':
                self.lbxd_url = link['url']
                break
        self.poster_path = ''
        try:
            for poster in film_json['poster']['sizes']:
                if poster['height'] > 400:
                    self.poster_path = poster['url']
                    break
            if not len(self.poster_path):
                self.poster_path = film_json['poster']['sizes'][0]['url']
        except KeyError:
            pass

    def create_description(self):
        text = ''
        film_json = api.api_call('film/{}'.format(self.lbxd_id)).json()
        try:
            text += '**Original Title:** ' + film_json['originalName'] + '\n'
        except KeyError:
            pass
        try:
            text += '**Length:** ' + str(film_json['runTime']) + ' mins\n'
        except KeyError:
            pass
        text += '**Genres:** '
        for genre in film_json['genres']:
            text += genre['name'] + ', '
        return text[:-2] + '\n'

    def load_tmdb_search(self, keywords):
        api_url = "https://api.themoviedb.org/3/search/movie?api_key="\
                  + api_key
        keywords = ' '.join(keywords.split()[:-1])
        api_url += "&query=" + keywords.replace("’", "")
        api_url += "&year=" + self.input_year if self.has_year else ''
        if not len(keywords):
            raise LbxdNotFound('You need to specify a keyword or title.')

        try:
            search_results = s.get(api_url)
            search_results.raise_for_status()
            if not len(search_results.json()['results']):
                raise LbxdNotFound("No film was found with this search.")
            return search_results
        except requests.exceptions.HTTPError as err:
            print(err)
            raise LbxdServerError("There was a problem trying to access TMDb.")

    def get_tmdb_id(self, search_response, keywords):
        film_json = search_response.json()['results'][0]
        for search in search_response.json()['results']:
            if search['release_date'].split('-')[0] == self.input_year:
                film_json = search
                break
        self.title = film_json['title']
        return str(film_json['id'])

    def get_mkdb_rating(self):
        try:
            page = s.get(self.lbxd_url.replace("letterboxd.com", "eiga.me"))
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return ''
        mkdb_html = BeautifulSoup(page.text, 'lxml')
        rating_html = mkdb_html.find('div', class_='card-body-summary')
        if rating_html is None:
            return ''
        avg_rating_html = rating_html.find('h4')
        if avg_rating_html is None:
            return ''
        avg_rating = avg_rating_html.get_text()
        row_lists = mkdb_html.find_all('section', class_='film-rating-group')
        nb_ratings = 0
        for row in row_lists:
            nb_ratings += len(row.find_all('li'))
        mkdb_description = '**MKDb Average:** [' + avg_rating
        mkdb_description += ' out of ' + str(nb_ratings) + ' ratings\n]'
        mkdb_description += '(' + page.url + ')'
        return mkdb_description

    def create_embed(self):
        title = self.title
        if self.year:
            title += ' (' + str(self.year) + ')'
        film_embed = discord.Embed(title=title, description=self.description,
                                   url=self.lbxd_url, colour=0xd8b437)
        if len(self.poster_path):
            film_embed.set_thumbnail(url=self.poster_path)

        return film_embed
