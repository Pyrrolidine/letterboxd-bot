from .api import api_call
from .core import create_embed
from .user import user_embed


def diary_embed(username):
    username, display_name, user_lbxd_id, avatar_url = user_embed(
        username, False)
    url = 'https://letterboxd.com/{}/films/diary'.format(username)
    title = 'Recent diary activity from {}'.format(display_name)
    return create_embed(title, url, __get_activity(user_lbxd_id), avatar_url)


def __get_activity(lbxd_id):
    params = {
        'member': lbxd_id,
        'memberRelationship': 'Owner',
        'where': 'HasDiaryDate'
    }
    response = api_call('log-entries', params)
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
            if str(diary_entry['rating'])[-1] == '5':
                description += '½'
        if diary_entry['like']:
            description += ' ♥'
        if diary_entry['diaryDetails']['rewatch']:
            description += ' ↺'
        if diary_entry.get('review'):
            description += ' ☰'
        description += '\n'
    return description
