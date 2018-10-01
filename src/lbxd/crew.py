import requests

import config

from .core import api, create_embed
from .exceptions import LbxdNotFound


def crew_embed(input_name, alias):
    crew_dict = {'name': '', 'url': '', 'api_url': ''}
    lbxd_id, fixed_search = __check_if_fixed_search(input_name)
    person_json = __search_letterboxd(input_name, alias, lbxd_id, fixed_search)
    description = __get_details(person_json, crew_dict)
    description += __get_dates(crew_dict['api_url'])
    return create_embed(crew_dict['name'], crew_dict['url'], description,
                        __get_picture(crew_dict['api_url']))


def __check_if_fixed_search(keywords):
    for name, lbxd_id in config.SETTINGS['fixed_crew_search'].items():
        if name.lower() == keywords.lower():
            return lbxd_id, True
    return '', False


def __search_letterboxd(item, alias, lbxd_id, fixed_search):
    if fixed_search:
        response = api.api_call('contributor/' + lbxd_id)
        person_json = response.json()
    else:
        params = {'input': item, 'include': 'ContributorSearchItem'}
        if alias in ['a', 'actor']:
            params['contributionType'] = 'Actor'
        elif alias in ['d', 'director']:
            params['contributionType'] = 'Director'
        response = api.api_call('search', params)
        if not response.json()['items']:
            raise LbxdNotFound('No person was found with this search.')
        person_json = response.json()['items'][0]['contributor']
    return person_json


def __get_details(person_json, crew_dict):
    for link in person_json['links']:
        if link['type'] == 'tmdb':
            tmdb_id = link['id']
        elif link['type'] == 'letterboxd':
            crew_dict['url'] = link['url']
    crew_dict['api_url'] = 'https://api.themoviedb.org/3/person/{}'.format(
        tmdb_id)
    crew_dict['name'] = person_json['name']
    description = ''
    for contrib_stats in person_json['statistics']['contributions']:
        description += '**' + contrib_stats['type'] + ':** '
        description += str(contrib_stats['filmCount']) + '\n'
    return description


def __get_dates(api_url):
    details_text = ''
    url = api_url + '?api_key={}'.format(config.SETTINGS['tmdb'])
    try:
        person_tmdb = api.session.get(url)
        person_tmdb.raise_for_status()
    except requests.exceptions.HTTPError:
        return ''

    for element in person_tmdb.json():
        if not person_tmdb.json()[element]:
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


def __get_picture(api_url):
    try:
        person_img = api.session.get(
            api_url + '/images?api_key={}'.format(config.SETTINGS['tmdb']))
        person_img.raise_for_status()
        if not person_img.json()['profiles']:
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
