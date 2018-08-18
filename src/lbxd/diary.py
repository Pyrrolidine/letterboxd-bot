from .core import api
import discord


class Diary(object):
    def __init__(self, user):
        self.user = user
        self.description = self.get_activity()

    def get_activity(self):
        params = {
            'member': self.user.lbxd_id,
            'memberRelationship': 'Owner',
            'where': 'HasDiaryDate'
        }
        response = api.api_call('log-entries', params)
        description = ''
        for n_entries, diary_entry in enumerate(response.json()['items']):
            if n_entries > 4:
                break
            for link in diary_entry['links']:
                if link['type'] == 'letterboxd':
                    entry_url = link['url']
                    break
            description += '**[' + diary_entry['film']['name']
            film_year = diary_entry['film'].get('releaseYear')
            if film_year:
                description += ' ({})'.format(film_year)
            description += ']({})**\n'.format(entry_url)
            if diary_entry.get('diaryDetails'):
                description += '**' + \
                    diary_entry['diaryDetails']['diaryDate'] + '** '
            if diary_entry.get('rating'):
                description += '★' * int(diary_entry['rating'])
                if abs(diary_entry['rating'] * 10) % 10:
                    description += '½'
            if diary_entry['like']:
                description += ' ♥'
            description += '\n'
        return description

    def create_embed(self):
        title = 'Recent diary activity from {}'.format(self.user.display_name)
        diary_embed = discord.Embed(
            title=title,
            url=self.user.url + '/films/diary/',
            colour=0xd8b437,
            description=self.description)
        diary_embed.set_thumbnail(url=self.user.avatar_url)
        return diary_embed
