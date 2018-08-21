from .core import api, format_text
from .exceptions import LbxdNotFound
import discord


class Review(object):
    def __init__(self, user, film):
        self.user = user
        self.film = film
        self.n_reviews = 0
        self.review_url = ''
        self.activity_url = self.film.lbxd_url.replace(
            '.com/', '.com/{}/'.format(self.user.username)) + 'activity'
        response = self.find_reviews()
        self.description = self.create_description(response)

    def find_reviews(self):
        params = {
            'film': self.film.lbxd_id,
            'member': self.user.lbxd_id,
            'memberRelationship': 'Owner'
        }
        response = api.api_call('log-entries', params).json()
        self.n_reviews = len(response['items'])
        if not self.n_reviews:
            raise LbxdNotFound(
                '{0} does not have logged activity for {1} ({2}).'.format(
                    self.user.display_name, self.film.title, self.film.year))
        return response

    def create_description(self, response):
        description = ''
        preview_done = False
        for review in response['items']:
            if len(description) > 1500:
                description += '**[Click here for more activity]({})**'.format(
                    self.activity_url)
                break
            for link in review['links']:
                if link['type'] == 'letterboxd':
                    self.review_url = link['url']
                    break
            word = 'Entry'
            if review.get('review'):
                word = 'Review'
            description += '**[{}]('.format(word) + self.review_url + ')** '
            if review.get('diaryDetails'):
                date = review['diaryDetails']['diaryDate']
                description += '**' + date + '** '
            if review.get('rating'):
                description += '★' * int(review['rating'])
                if abs(review['rating'] * 10) % 10:
                    description += '½'
            if review['like']:
                description += ' ♥'
            description += '\n'
            if not preview_done:
                preview = self.create_preview(review)
                if len(preview):
                    description += preview
                    preview_done = True
        return description

    def create_preview(self, review):
        preview = ''
        if review.get('review'):
            if review['review']['containsSpoilers']:
                preview += '```This review may contain spoilers.```'
            else:
                preview += format_text(review['review']['lbml'], 400)
        return preview

    def create_embed(self):
        review_word = 'entries' if self.n_reviews > 1 else 'entry'
        if self.n_reviews > 1:
            embed_url = self.activity_url
        else:
            embed_url = self.review_url

        review_embed = discord.Embed(
            title='{0} {1} of {2} ({3})'
            .format(self.user.display_name, review_word, self.film.title,
                    self.film.year),
            url=embed_url,
            colour=0xd8b437,
            description=self.description)
        review_embed.set_thumbnail(url=self.film.poster_path)

        return review_embed
