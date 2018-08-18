from .core import api
import discord


class Diary(object):
    def __init__(self, user):
        self.user = user
        self.description = self.get_activity()

    def get_activity(self):
        params = {
            'include': 'DiaryEntryActivity',
            'where': 'OwnActivity',
            'perPage': 50
        }
        response = api.api_call('member/{}/activity'.format(self.user.lbxd_id),
                                params)
        description = ''
        n_entries = 0
        for entry in response.json()['items']:
            if n_entries > 4:
                break
            if not entry.get('diaryEntry'):
                continue
            diary_entry = entry['diaryEntry']
            n_entries += 1
            for link in diary_entry['links']:
                if link['type'] == 'letterboxd':
                    entry_url = link['url']
                    break
            description += '**[' + diary_entry['film']['name']
            film_year = ' ({})'.format(diary_entry['film'].get('releaseYear'))
            if film_year:
                description += film_year
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
            url=self.user.url,
            colour=0xd8b437,
            description=self.description)
        diary_embed.set_thumbnail(url=self.user.avatar_url)
        return diary_embed
