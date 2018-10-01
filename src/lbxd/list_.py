from .core import api, create_embed, format_text
from .exceptions import LbxdNotFound


def list_embed(user, keywords):
    list_dict = {'name': '', 'url': '', 'poster_url': '', 'id': ''}
    list_dict['id'] = __find_list(keywords, user.lbxd_id, list_dict)
    description = __get_infos(list_dict)
    return create_embed(list_dict['name'], list_dict['url'], description,
                        list_dict['poster_url'])


def __find_list(keywords, user_lbxd_id, list_dict):
    params = {
        'member': user_lbxd_id,
        'memberRelationship': 'Owner',
        'perPage': 50,
        'where': 'Published'
    }
    response = api.api_call('lists', params).json()
    match = False
    for user_list in response['items']:
        for word in keywords.lower().split():
            if word in user_list['name'].lower():
                match = True
                list_dict['name'] = user_list['name']
            else:
                match = False
                break
        if match:
            return user_list['id']
    raise LbxdNotFound('No list was found (limit to 50 most recent).\n' +
                       'Make sure the first word is a **username**.')


def __get_infos(list_dict):
    list_json = api.api_call('list/{}'.format(list_dict['id'])).json()
    for link in list_json['links']:
        if link['type'] == 'letterboxd':
            list_dict['url'] = link['url']
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
                    list_dict['poster_url'] = poster['url']
                    break
    return description
