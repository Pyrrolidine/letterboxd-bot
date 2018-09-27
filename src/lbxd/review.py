from .core import api, format_text, create_embed
from .exceptions import LbxdNotFound


class Review:
    def __init__(self, user, film):
        self._user = user
        self._film = film
        self._num_reviews = 0
        self._review_url = ''
        activity_url = self._film.lbxd_url.replace(
            '.com/', '.com/{}/'.format(self._user.username)) + 'activity'
        response = self.__find_reviews()
        description = self.__create_description(response, activity_url)

        if self._num_reviews > 1:
            embed_url = activity_url
        else:
            embed_url = self._review_url
        review_word = 'entries' if self._num_reviews > 1 else 'entry'
        title = '{0} {1} of {2} ({3})'.format(self._user.display_name,
                                              review_word, self._film.title,
                                              self._film.year)
        self.embed = create_embed(title, embed_url, description,
                                  self._film.poster_path)

    def __find_reviews(self):
        params = {
            'film': self._film.lbxd_id,
            'member': self._user.lbxd_id,
            'memberRelationship': 'Owner'
        }
        response = api.api_call('log-entries', params).json()
        self._num_reviews = len(response['items'])
        if not self._num_reviews:
            raise LbxdNotFound(
                '{0} does not have logged activity for {1} ({2}).'.format(
                    self._user.display_name, self._film.title,
                    self._film.year))
        return response

    def __create_description(self, response, activity_url):
        description = ''
        preview_done = False
        for review in response['items']:
            if len(description) > 1500:
                description += '**[Click here for more activity]({})**'.format(
                    activity_url)
                break
            for link in review['links']:
                if link['type'] == 'letterboxd':
                    self._review_url = link['url']
                    break
            word = 'Entry'
            if review.get('review'):
                word = 'Review'
            description += '**[{}]('.format(word) + self._review_url + ')** '
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
                preview = self.__create_preview(review)
                if len(preview):
                    description += preview
                    preview_done = True
        return description

    def __create_preview(self, review):
        preview = ''
        if review.get('review'):
            if review['review']['containsSpoilers']:
                preview += '```This review may contain spoilers.```'
            else:
                preview += format_text(review['review']['lbml'], 400)
        return preview
