from .core import api, format_text, create_embed
from .exceptions import LbxdNotFound


class List:
    def __init__(self, user, keywords):
        self._list_name = ''
        self._url = ''
        self._poster_url = ''
        list_lbxd_id = self.find_list(keywords, user.lbxd_id)
        description = self.get_infos(list_lbxd_id)
        self.embed = create_embed(self._list_name, self._url, description,
                                  self._poster_url)

    def find_list(self, keywords, user_lbxd_id):
        params = {
            'member': user_lbxd_id,
            'memberRelationship': 'Owner',
            'perPage': 50,
            'where': 'Published'
        }
        response = api.api_call('lists', params).json()
        match = False
        for user_list in response['items']:
            self._list_name = user_list['name']
            for word in keywords.lower().split():
                if word in self._list_name.lower():
                    match = True
                else:
                    match = False
                    break
            if match:
                return user_list['id']
        raise LbxdNotFound('No list was found (limit to 50 most recent).\n' +
                           'Make sure the first word is a **username**.')

    def get_infos(self, list_lbxd_id):
        list_json = api.api_call('list/{}'.format(list_lbxd_id)).json()
        for link in list_json['links']:
            if link['type'] == 'letterboxd':
                self._url = link['url']
                break
        description = 'By **' + list_json['owner']['displayName'] + '**\n'
        description += str(list_json['filmCount']) + ' films\nPublished '
        description += list_json['whenPublished'].split('T')[0].strip() + '\n'
        if list_json.get('descriptionLbml'):
            description += format_text(list_json['descriptionLbml'], 300)
        if len(list_json['previewEntries']):
            poster_json = list_json['previewEntries'][0]['film'].get('poster')
            if poster_json:
                film_posters = poster_json
                for poster in film_posters['sizes']:
                    if poster['height'] > 400:
                        self._poster_url = poster['url']
                        break
        return description
