""" List command functions
    Call user_embed() first
"""

from .api import api_call
from .helpers import create_embed, format_text
from .exceptions import LbxdNotFound
from .user import user_embed


def list_embed(username, keywords):
    __, __, user_lbxd_id, __ = user_embed(username, False)
    list_id = __find_list(keywords, user_lbxd_id)
    description, url, poster_url, name = __get_infos(list_id)
    return create_embed(name, url, description, poster_url)


def __find_list(keywords, user_lbxd_id):
    params = {
        'member': user_lbxd_id,
        'memberRelationship': 'Owner',
        'perPage': 50,
        'where': 'Published'
    }
    response = api_call('lists', params).json()
    match = False
    for user_list in response['items']:
        for word in keywords.lower().split():
            if word in user_list['name'].lower():
                match = True
            else:
                match = False
                break
        if match:
            return user_list['id']
    raise LbxdNotFound('No list was found (limit to 50 most recent).\n' +
                       'Make sure the first word is a **username**.')


def __get_infos(list_id):
    list_json = api_call('list/{}'.format(list_id)).json()
    for link in list_json['links']:
        if link['type'] == 'letterboxd':
            url = link['url']
            break
    description = 'By **' + list_json['owner']['displayName'] + '**\n'
    description += str(list_json['filmCount']) + ' films\nPublished '
    description += list_json['whenPublished'].split('T')[0].strip() + '\n'
    if list_json.get('descriptionLbml'):
        description += format_text(list_json['descriptionLbml'], 300)
    if list_json['previewEntries']:
        poster_json = list_json['previewEntries'][0]['film'].get('poster')
        if poster_json:
            film_posters = poster_json
            for poster in film_posters['sizes']:
                if poster['height'] > 400:
                    poster_url = poster['url']
                    break
    return description, url, poster_url, list_json['name']
