from .core import *


class Review(object):
    def __init__(self, user, film):
        self.user = user
        self.film = film
        self.description = self.find_reviews()

    def find_reviews(self):
        params = {
            'film': self.film.lbxd_id,
            'member': self.user.lbxd_id,
            'memberRelationship': 'Owner'
        }
        response = api.api_call('log-entries', params).json()
        self.n_reviews = len(response['items'])
        if not self.n_reviews:
            raise LbxdNotFound('{0} does not have activity for {1} ({2}).'
                               .format(self.user.display_name, self.film.title,
                                       self.film.year))

        description = ''
        preview_done = False
        for review in response['items']:
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
                if not review.get('review'):
                    continue
                if review['review']['containsSpoilers']:
                    spoiler_warning = 'This review may contain spoilers.'
                    description += '```' + spoiler_warning + '```'
                else:
                    description += format_text(review['review']['lbml'], 400)
                preview_done = True
        return description

    def create_embed(self):
        review_word = 'entries' if self.n_reviews > 1 else 'entry'
        if self.n_reviews > 1:
            embed_url = self.film.lbxd_url.replace(
                '.com/', '.com/{}/'.format(self.user.user))
            embed_url += 'activity'
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
