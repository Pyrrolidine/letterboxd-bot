from .core import api, format_text
from .exceptions import LbxdNotFound
import discord


class List(object):
    def __init__(self, user, keywords):
        self.user = user
        self.list_name = ''
        self.url = ''
        self.poster_url = ''
        self.lbxd_id = self.find_list(keywords)
        self.description = self.get_infos()

    def find_list(self, keywords):
        params = {
            'member': self.user.lbxd_id,
            'memberRelationship': 'Owner',
            'perPage': 50,
            'where': 'Published'
        }
        response = api.api_call('lists', params).json()
        match = False
        for user_list in response['items']:
            self.list_name = user_list['name']
            for word in keywords.lower().split():
                if word in self.list_name.lower():
                    match = True
                else:
                    match = False
                    break
            if match:
                return user_list['id']
        raise LbxdNotFound('No list was found (limit to 50 most recent).\n' +
                           'Make sure the first word is a **username**.')

    def get_infos(self):
        list_json = api.api_call('list/{}'.format(self.lbxd_id)).json()
        for link in list_json['links']:
            if link['type'] == 'letterboxd':
                self.url = link['url']
                break
        description = 'By **' + list_json['owner']['displayName'] + '**\n'
        description += str(list_json['filmCount']) + ' films\nPublished '
        description += list_json['whenPublished'].split('T')[0].strip() + '\n'
        if list_json.get('descriptionLbml'):
            description += format_text(list_json['descriptionLbml'], 300)
        poster_json = list_json['previewEntries'][0]['film'].get('poster')
        if poster_json:
            film_posters = poster_json
            for poster in film_posters['sizes']:
                if poster['height'] > 400:
                    self.poster_url = poster['url']
                    break
        return description

    def create_embed(self):
        list_embed = discord.Embed(
            title=self.list_name,
            url=self.url,
            colour=0xd8b437,
            description=self.description)
        list_embed.set_thumbnail(url=self.poster_url)
        return list_embed
