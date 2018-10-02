from .core import api, create_embed, format_text
from .exceptions import LbxdNotFound
from .film import film_embed
from .user import user_embed


def review_embed(username, film_search):
    username, display_name, user_lbxd_id, __ = user_embed(username, False)
    film_lbxd_id, film_title, film_year, poster_path, film_lbxd_url = film_embed(
        film_search, False)
    activity_url = film_lbxd_url.replace(
        '.com/', '.com/{}/'.format(username)) + 'activity'
    response, nb_reviews = __find_reviews(user_lbxd_id, display_name,
                                          film_lbxd_id, film_title, film_year)
    description, embed_url = __create_description(response, activity_url)

    if nb_reviews > 1:
        embed_url = activity_url
    review_word = 'entries' if nb_reviews > 1 else 'entry'
    title = '{0} {1} of {2} ({3})'.format(display_name, review_word,
                                          film_title, film_year)
    return create_embed(title, embed_url, description, poster_path)


def __find_reviews(user_lbxd_id, display_name, film_lbxd_id, film_title,
                   film_year):
    params = {
        'film': film_lbxd_id,
        'member': user_lbxd_id,
        'memberRelationship': 'Owner'
    }
    response = api.api_call('log-entries', params).json()
    nb_reviews = len(response['items'])
    if not nb_reviews:
        raise LbxdNotFound(
            '{0} does not have logged activity for {1} ({2}).'.format(
                display_name, film_title, film_year))
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
