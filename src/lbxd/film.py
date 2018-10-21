""" Film command functions
    film_details() is used by review.py
    It uses the TMDb API to get the production countries of a film
"""

from re import fullmatch

import requests
from config import SETTINGS

from .api import api_call, api_session
from .helpers import create_embed
from .exceptions import LbxdNotFound


def film_embed(keywords, with_mkdb=False):
    input_year, has_year = __check_year(keywords)
    lbxd_id, fixed_search = __check_if_fixed_search(keywords)
    film_json = __search_request(keywords, has_year, input_year, fixed_search,
                                 lbxd_id)
    lbxd_id = film_json['id']
    title = film_json['name']
    year = film_json.get('releaseYear')
    lbxd_url, tmdb_id, poster_path = __get_links(film_json)
    description = __create_description(lbxd_id, tmdb_id, title)
    if with_mkdb:
        description += __get_mkdb_rating(lbxd_url)
    description += __get_stats(lbxd_id)
    if year:
        title += ' (' + str(year) + ')'
    return create_embed(title, lbxd_url, description, poster_path)


def film_details(keywords):
    input_year, has_year = __check_year(keywords)
    lbxd_id, fixed_search = __check_if_fixed_search(keywords)
    film_json = __search_request(keywords, has_year, input_year, fixed_search,
                                 lbxd_id)
    lbxd_id = film_json['id']
    title = film_json['name']
    year = film_json.get('releaseYear')
    lbxd_url, _, poster_path = __get_links(film_json)
    return lbxd_id, title, year, poster_path, lbxd_url


def __check_year(keywords):
    last_word = keywords.split()[-1]
    if fullmatch(r'\(\d{4}\)', last_word):
        return last_word.replace('(', '').replace(')', ''), True
    return '', False


def __check_if_fixed_search(keywords):
    for title, lbxd_id in SETTINGS['fixed_film_search'].items():
        if title.lower() == keywords.lower():
            return lbxd_id, True
    return '', False


def __search_request(keywords, has_year, input_year, fixed_search, lbxd_id):
    found = False
    if has_year:
        keywords = ' '.join(keywords.split()[:-1])
    if fixed_search:
        film_json = api_call('film/{}'.format(lbxd_id)).json()
    else:
        params = {'input': keywords, 'include': 'FilmSearchItem'}
        response = api_call('search', params)
        results = response.json()['items']
        if not results:
            raise LbxdNotFound('No film was found with this search.')
        if has_year:
            for result in results:
                if not result['film'].get('releaseYear'):
                    continue
                film_year = str(result['film']['releaseYear'])
                if film_year == input_year:
                    film_json = result['film']
                    found = True
                    break
        else:
            film_json = results[0]['film']
    if has_year and not found:
        raise LbxdNotFound('No film was found with this search.')
    return film_json


def __get_links(film_json):
    for link in film_json['links']:
        if link['type'] == 'letterboxd':
            lbxd_url = link['url']
        elif link['type'] == 'tmdb':
            tmdb_id = link['id']

    poster_path = ''
    if film_json.get('poster'):
        for poster in film_json['poster']['sizes']:
            if poster['height'] > 400:
                poster_path = poster['url']
                break
        if not poster_path:
            poster_path = film_json['poster']['sizes'][0]['url']
    return lbxd_url, tmdb_id, poster_path


def __create_description(lbxd_id, tmdb_id, title):
    description = ''
    film_json = api_call('film/{}'.format(lbxd_id)).json()

    original_title = film_json.get('originalName')
    if original_title:
        description += '**Original Title:** ' + original_title + '\n'

    director_str = ''
    for contribution in film_json['contributions']:
        if contribution['type'] == 'Director':
            for dir_count, director in enumerate(contribution['contributors']):
                director_str += director['name'] + ', '
            break
    if director_str:
        if dir_count:
            description += '**Directors:** '
        else:
            description += '**Director:** '
        description += director_str[:-2] + '\n'

    description += __get_countries(tmdb_id, title)
    runtime = film_json.get('runTime')
    description += '**Length:** ' + str(runtime) + ' mins\n' if runtime else ''

    genres_str = ''
    for genres_count, genre in enumerate(film_json['genres']):
        genres_str += genre['name'] + ', '
    if genres_str:
        if genres_count:
            description += '**Genres:** '
        else:
            description += '**Genre:** '
        description += genres_str[:-2] + '\n'

    return description


def __get_countries(tmdb_id, title):
    api_url = 'https://api.themoviedb.org/3/movie/' + tmdb_id\
                + '?api_key=' + SETTINGS['tmdb']
    country_text = ''
    try:
        response = api_session.get(api_url)
        response.raise_for_status()
        country_str = ''
        if response.json()['title'] == title:
            for count, country in enumerate(
                    response.json()['production_countries']):
                if country['name'] == 'United Kingdom':
                    country_str += 'UK, '
                elif country['name'] == 'United States of America':
                    country_str += 'USA, '
                else:
                    country_str += country['name'] + ', '
            if country_str:
                if count:
                    country_text += '**Countries:** '
                else:
                    country_text += '**Country:** '
                country_text += country_str[:-2] + '\n'
    except requests.exceptions.HTTPError:
        pass
    return country_text


def __get_mkdb_rating(lbxd_url):
    mkdb_url = lbxd_url.replace('letterboxd.com', 'eiga.me/api')
    try:
        page = api_session.get(mkdb_url + 'summary')
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


def __get_stats(lbxd_id):
    text = ''
    response = api_call('film/{}/statistics'.format(lbxd_id))
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
