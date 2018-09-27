from .core import api, create_embed
from .exceptions import LbxdNotFound
import config
import requests


class Crew:
    def __init__(self, input_name, alias):
        self._api_url = ''
        self._name = ''
        self._url = ''
        self._fixed_search = False
        lbxd_id = self.__check_if_fixed_search(input_name)
        person_json = self.__search_letterboxd(input_name, alias, lbxd_id)
        description = self.__get_details(person_json)
        description += self.__get_dates()
        self.embed = create_embed(self._name, self._url, description,
                                  self.__get_picture())

    def __check_if_fixed_search(self, keywords):
        for name, lbxd_id in config.fixed_crew_search.items():
            if name.lower() == keywords.lower():
                self._fixed_search = True
                return lbxd_id
        return ''

    def __search_letterboxd(self, item, alias, lbxd_id):
        if self._fixed_search:
            response = api.api_call('contributor/' + lbxd_id)
            person_json = response.json()
        else:
            params = {'input': item, 'include': 'ContributorSearchItem'}
            if alias in ['a', 'actor']:
                params['contributionType'] = 'Actor'
            elif alias in ['d', 'director']:
                params['contributionType'] = 'Director'
            response = api.api_call('search', params)
            if not len(response.json()['items']):
                raise LbxdNotFound('No person was found with this search.')
            person_json = response.json()['items'][0]['contributor']
        return person_json

    def __get_details(self, person_json):
        for link in person_json['links']:
            if link['type'] == 'tmdb':
                tmdb_id = link['id']
            elif link['type'] == 'letterboxd':
                self._url = link['url']
        self._api_url = 'https://api.themoviedb.org/3/person/{}'.format(
            tmdb_id)
        self._name = person_json['name']
        description = ''
        for contrib_stats in person_json['statistics']['contributions']:
            description += '**' + contrib_stats['type'] + ':** '
            description += str(contrib_stats['filmCount']) + '\n'
        return description

    def __get_dates(self):
        details_text = ''
        url = self._api_url + '?api_key={}'.format(config.keys['tmdb'])
        try:
            person_tmdb = api.session.get(url)
            person_tmdb.raise_for_status()
        except requests.exceptions.HTTPError:
            return ''

        for element in person_tmdb.json():
            if person_tmdb.json()[element] is None:
                continue
            if element == 'birthday':
                details_text += '**Birthday:** ' \
                                + person_tmdb.json()[element] + '\n'
            elif element == 'deathday':
                details_text += '**Day of Death:** ' \
                                + person_tmdb.json()[element] + '\n'
            elif element == 'place_of_birth':
                details_text += '**Place of Birth:** ' \
                                + person_tmdb.json()[element]
        return details_text

    def __get_picture(self):
        try:
            person_img = api.session.get(self._api_url + '/images?api_key={}'.
                                         format(config.keys['tmdb']))
            person_img.raise_for_status()
            if not len(person_img.json()['profiles']):
                return ''
            img_url = 'https://image.tmdb.org/t/p/w200'
            highest_vote = 0
            for img in person_img.json()['profiles']:
                if img['vote_average'] >= highest_vote:
                    highest_vote = img['vote_average']
                    path = img['file_path']
            return img_url + path
        except requests.exceptions.HTTPError:
            return ''
