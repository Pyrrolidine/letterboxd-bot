from .core import *


class Film(object):

    def __init__(self, keywords, with_info=True, is_metropolis=False):
        self.has_year = False
        self.fix_search = False
        self.year = ''
        self.input_year = self.check_year(keywords)
        self.tmdb_id = self.check_if_fixed_search(keywords)
        if not self.fix_search:
            if self.has_year:
                search_response = self.load_tmdb_search(keywords)
                self.tmdb_id = self.get_tmdb_id(search_response, keywords)
            else:
                self.lbxd_id = self.load_lbxd_search(keywords)
        lbxd_html = self.get_lbxd_page()
        self.poster_path = self.get_poster(lbxd_html)
        if not with_info:
            return
        self.description = self.get_details_lbxd(lbxd_html)
        if is_metropolis:
            self.description += self.get_mkdb_rating()
        self.description += self.get_views(lbxd_html)

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

    def load_lbxd_search(self, keywords):
        try:
            keywords = keywords.replace('\\', '')
            keywords = ''.join(keywords.splitlines())
            path = urllib.parse.quote_plus(keywords.replace('/', ' '))
            page = s.get("https://letterboxd.com/search/films/{}/"
                         .format(path))
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            raise LbxdServerError("There was a problem trying to access "
                                  + "Letterboxd.")

        first_result = SoupStrainer('div', class_='film-detail-content')
        result_html = BeautifulSoup(page.text, 'lxml', parse_only=first_result)
        result_link = result_html.find('a')
        if result_link is not None:
            self.title = result_link.contents[0].strip()
            return result_link['href']
        else:
            raise LbxdNotFound("No film was found with this search.")

    def load_tmdb_search(self, keywords):
        api_url = "https://api.themoviedb.org/3/search/movie?api_key="\
                  + api_key
        keywords = ' '.join(keywords.split()[:-1])
        api_url += "&query=" + keywords.replace("’", "")
        api_url += "&year=" + self.input_year if self.has_year else ''

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

    def get_lbxd_page(self):
        if self.has_year or self.fix_search:
            lbxd_link = "https://letterboxd.com/tmdb/" + self.tmdb_id
        else:
            lbxd_link = "https://letterboxd.com" + self.lbxd_id
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

        content_only = SoupStrainer('div', id='film-page-wrapper')
        lbxd_html = BeautifulSoup(page.text, 'lxml',
                                  parse_only=content_only)
        if lbxd_html.find('div') is None:
            raise LbxdNotFound("This film doesn't have a Letterboxd page.")
        year_html = lbxd_html.find('small', class_='number')
        if year_html is not None:
            self.year = year_html.get_text()
        return lbxd_html

    def get_details_lbxd(self, lbxd_html):
        description = ''
        header_html = lbxd_html.find('section', id='featured-film-header')
        original_html = header_html.find('em')
        if original_html is not None:
            self.original_title = original_html.get_text().replace('’', '')
            self.original_title = self.original_title.replace('‘', '')
            description += '**Original Title**: ' + self.original_title + '\n'

        nb_directors = 0
        crew_html = lbxd_html.find('div', id='tab-crew')
        director_str = "**Director:** "
        if crew_html is not None:
            for crew in crew_html.find_all('a'):
                if crew['href'].startswith("/director"):
                    director_str += "{}, ".format(crew.get_text())
                    nb_directors += 1
            if nb_directors > 1:
                director_str = director_str.replace('irector:', 'irectors:')
            if nb_directors:
                description += director_str[:-2] + '\n'

        country_html = lbxd_html.find('div', id='tab-details')
        if country_html is not None:
            details_html = country_html.find_all('a')
            country_str = "**Country:** "
            plural_country = 0
            for detail in details_html:
                if detail['href'].startswith("/films/country/"):
                    country_str += "{}, ".format(detail.get_text())
                    plural_country += 1
            if plural_country > 1:
                country_str = country_str.replace('Country', 'Countries')
            if plural_country:
                description += country_str[:-2] + '\n'

        footer_html = lbxd_html.find('p', class_='text-link text-footer')
        list_footer_text = footer_html.get_text().split()
        if list_footer_text[1].startswith('min'):
            self.runtime = list_footer_text[0]
            description += '**Length:** ' + self.runtime + ' mins'
            if self.runtime == 1:
                description = description.replace('mins', 'min')
            description += '\n'

        genre_tab_html = lbxd_html.find(id='tab-genres')
        if genre_tab_html is not None:
            genres_str = '**Genre:** '
            nb_genres = 0
            genres_html = genre_tab_html.find_all('a')
            for genre in genres_html:
                genres_str += genre.get_text().title() + ', '
                nb_genres += 1
            if nb_genres > 1:
                genres_str = genres_str.replace('enre:', 'enres:')
            if nb_genres:
                genres_str = genres_str.replace('Tv', 'TV')
                description += genres_str[:-2] + '\n'

        return description

    def get_views(self, lbxd_html):
        stats_html = lbxd_html.find('ul', class_='film-stats')
        views_html = stats_html.find(class_="icon-watched")
        return "Watched by " + views_html.contents[0] + " members"

    def get_poster(self, lbxd_html):
        poster_html = lbxd_html.find('div', class_='film-poster')
        return poster_html.find('img', class_='image')['src']

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
        title += ' (' + self.year + ')' if len(self.year) else ''
        film_embed = discord.Embed(title=title, description=self.description,
                                   url=self.lbxd_url, colour=0xd8b437)
        film_embed.set_thumbnail(url=self.poster_path)

        return film_embed
