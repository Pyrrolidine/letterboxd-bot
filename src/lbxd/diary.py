from .core import api, create_embed


def diary_embed(user):
    url = user.url + '/films/diary'
    title = 'Recent diary activity from {}'.format(user.display_name)
    return create_embed(title, url, __get_activity(user.lbxd_id),
                        user.avatar_url)


def __get_activity(lbxd_id):
    params = {
        'member': lbxd_id,
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
