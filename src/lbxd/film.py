import re

import requests

import config

from .core import api, create_embed
from .exceptions import LbxdNotFound


class Film:
    def __init__(self, keywords, with_info=True, with_mkdb=False):
        self.has_year = False
        self.fixed_search = False
        self.url = ''
        self.poster_path = ''
        self.title = ''
        self.tmdb_id = ''
        self.year = 0
        self.input_year = self.__check_year(keywords)
        self.lbxd_id = self.__check_if_fixed_search(keywords)
        film_json = self.__search_request(keywords)
        self.__get_details(film_json)
        if not with_info:
            return
        description = self.create_description()
        if with_mkdb:
            description += self.__get_mkdb_rating()
        description += self.__get_stats()
        title = self.title
        if self.year:
            title += ' (' + str(self.year) + ')'
        self.embed = create_embed(title, self.lbxd_url, description,
                                  self.poster_path)

    def __check_year(self, keywords):
        last_word = keywords.split()[-1]
        if re.fullmatch(r'\(\d{4}\)', last_word) is not None:
            self.has_year = True
            return last_word.replace('(', '').replace(')', '')
        return ''

    def __check_if_fixed_search(self, keywords):
        for title, lbxd_id in config.fixed_film_search.items():
            if title.lower() == keywords.lower():
                self.fixed_search = True
                return lbxd_id
        return ''

    def __search_request(self, keywords):
        found = False
        if self.has_year:
            keywords = ' '.join(keywords.split()[:-1])
        if self.fixed_search:
            film_json = api.api_call('film/{}'.format(self.lbxd_id)).json()
        else:
            params = {'input': keywords, 'include': 'FilmSearchItem'}
            response = api.api_call('search', params)
            results = response.json()['items']
            if not results:
                raise LbxdNotFound('No film was found with this search.')
            if self.has_year:
                for result in results:
                    if not result['film'].get('releaseYear'):
                        continue
                    film_year = str(result['film']['releaseYear'])
                    if film_year == self.input_year:
                        film_json = result['film']
                        found = True
                        break
            else:
                film_json = results[0]['film']
        if self.has_year and not found:
            raise LbxdNotFound('No film was found with this search.')
        return film_json

    def __get_details(self, film_json):
        self.lbxd_id = film_json['id']
        self.title = film_json['name']
        self.year = film_json.get('releaseYear')
        for link in film_json['links']:
            if link['type'] == 'letterboxd':
                self.lbxd_url = link['url']
            elif link['type'] == 'tmdb':
                self.tmdb_id = link['id']

        if not film_json.get('poster'):
            return
        for poster in film_json['poster']['sizes']:
            if poster['height'] > 400:
                self.poster_path = poster['url']
                break
        if not self.poster_path:
            self.poster_path = film_json['poster']['sizes'][0]['url']

    def create_description(self):
        text = ''
        film_json = api.api_call('film/{}'.format(self.lbxd_id)).json()

        original_title = film_json.get('originalName')
        if original_title:
            text += '**Original Title:** ' + original_title + '\n'

        director_str = ''
        director_count = 0
        for contribution in film_json['contributions']:
            if contribution['type'] == 'Director':
                for director in contribution['contributors']:
                    director_count += 1
                    director_str += director['name'] + ', '
                break
        if director_str:
            if director_count > 1:
                text += '**Directors:** '
            else:
                text += '**Director:** '
            text += director_str[:-2] + '\n'

        text += self.get_countries()
        runtime = film_json.get('runTime')
        text += '**Length:** ' + str(runtime) + ' mins\n' if runtime else ''

        genres_str = ''
        genres_count = 0
        for genre in film_json['genres']:
            genres_str += genre['name'] + ', '
            genres_count += 1
        if genres_str:
            if genres_count > 1:
                text += '**Genres:** '
            else:
                text += '**Genre:** '
            text += genres_str[:-2] + '\n'

        return text

    def get_countries(self):
        api_url = 'https://api.themoviedb.org/3/movie/' + self.tmdb_id\
                  + '?api_key=' + config.keys['tmdb']
        country_text = ''
        try:
            response = api.session.get(api_url)
            response.raise_for_status()
            country_str = ''
            country_count = 0
            if response.json()['title'] == self.title:
                for country in response.json()['production_countries']:
                    country_count += 1
                    if country['name'] == 'United Kingdom':
                        country_str += 'UK, '
                    elif country['name'] == 'United States of America':
                        country_str += 'USA, '
                    else:
                        country_str += country['name'] + ', '
                if country_str:
                    if country_count > 1:
                        country_text += '**Countries:** '
                    else:
                        country_text += '**Country:** '
                    country_text += country_str[:-2] + '\n'
        except requests.exceptions.HTTPError:
            pass
        return country_text

    def __get_stats(self):
        text = ''
        response = api.api_call('film/{}/statistics'.format(self.lbxd_id))
        stats_json = response.json()
        views = stats_json['counts']['watches']
        if views > 9999:
            views = str(round(views / 1000)) + 'k'
        elif views > 999:
            views = str(round(views / 1000, 1)) + 'k'
        if stats_json.get('rating'):
            rating = stats_json['rating']
            ratings_count = stats_json['counts']['ratings']
            if ratings_count > 999:
                ratings_count = str(round(ratings_count / 1000, 1)) + 'k'
            text += '**Average Rating:** ' + str(round(rating, 2))
            text += ' out of ' + str(ratings_count) + ' ratings\n'
        text += 'Watched by ' + str(views) + ' members'
        return text

    def __get_mkdb_rating(self):
        mkdb_url = self.lbxd_url.replace('letterboxd.com', 'eiga.me/api')
        try:
            page = api.session.get(mkdb_url + 'summary')
            page.raise_for_status()
        except requests.exceptions.HTTPError:
            return ''
        if not page.json()['total']:
            return ''
        avg_rating = page.json()['mean']
        nb_ratings = page.json()['total']
        mkdb_description = '**MKDb Average:** [' + str(avg_rating)
        mkdb_description += ' out of ' + str(nb_ratings) + ' ratings\n]'
        mkdb_description += '(' + mkdb_url.replace('/api', '') + ')'
        return mkdb_description
