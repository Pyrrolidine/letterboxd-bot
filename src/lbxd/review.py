from .core import api, create_embed, format_text
from .exceptions import LbxdNotFound


def review_embed(user, film):
    activity_url = film.lbxd_url.replace('.com/', '.com/{}/'.format(
        user.username)) + 'activity'
    response, nb_reviews = __find_reviews(user, film)
    description, embed_url = __create_description(response, activity_url)

    if nb_reviews > 1:
        embed_url = activity_url
    review_word = 'entries' if nb_reviews > 1 else 'entry'
    title = '{0} {1} of {2} ({3})'.format(user.display_name, review_word,
                                          film.title, film.year)
    return create_embed(title, embed_url, description, film.poster_path)


def __find_reviews(user, film):
    params = {
        'film': film.lbxd_id,
        'member': user.lbxd_id,
        'memberRelationship': 'Owner'
    }
    response = api.api_call('log-entries', params).json()
    nb_reviews = len(response['items'])
    if not nb_reviews:
        raise LbxdNotFound(
            '{0} does not have logged activity for {1} ({2}).'.format(
                user.display_name, film.title, film.year))
    return response, nb_reviews


def __create_description(response, activity_url):
    description = ''
    preview_done = False
    for review in response['items']:
        if len(description) > 1500:
            description += '**[Click here for more activity]({})**'.format(
                activity_url)
            break
        for link in review['links']:
            if link['type'] == 'letterboxd':
                review_link = link['url']
                break
        word = 'Entry'
        if review.get('review'):
            word = 'Review'
        description += '**[{}]('.format(word) + review_link + ')** '
        if review.get('diaryDetails'):
            date = review['diaryDetails']['diaryDate']
            description += '**' + date + '** '
        if review.get('rating'):
            description += '★' * int(review['rating'])
            if str(review['rating'])[-1] == '5':
                description += '½'
        if review['like']:
            description += ' ♥'
        description += '\n'
        if not preview_done:
            preview = __create_preview(review)
            if preview:
                description += preview
                preview_done = True
    return description, review_link


def __create_preview(review):
    preview = ''
    if review.get('review'):
        if review['review']['containsSpoilers']:
            preview += '```This review may contain spoilers.```'
        else:
            preview += format_text(review['review']['lbml'], 400)
    return preview
