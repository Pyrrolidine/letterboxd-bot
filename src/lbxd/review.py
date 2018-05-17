from .core import *
from .film import *


# TODO HANDLE FILM OBJECT
class Review(object):

    def __init__(self, username, Film):
        self.username = username
        self.film = Film
        split_film_link = self.film.lbxd_url.split('/')
        if len(split_film_link[-1]) > 0:
            lbxd_name = split_film_link[-1]
        else:
            lbxd_name = split_film_link[-2]
        self.url = "https://letterboxd.com/{0}/film/{1}/activity"\
                   .format(self.username, lbxd_name)
        activity_html = self.load_activity_page_html()
        self.display_name = ''
        self.n_reviews = 0
        self.review_link = ''
        self.description = self.find_reviews(activity_html)

    def load_activity_page_html(self):
        try:
            page = s.get(self.url)
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if page.status_code == 404:
                raise LbxdNotFound('The user ' + self.username
                                   + "doesn't exist")
            print(err)
            raise LbxdServerError('There was a problem trying to access '
                                  + 'Letterboxd.com')

        contents_only = SoupStrainer('div', class_="activity-table")
        activity_html = BeautifulSoup(page.text, "lxml",
                                      parse_only=contents_only)
        if not activity_html.find('div'):
            raise LbxdNotFound('{0} has not seen {1}.'
                               .format(self.username, self.film.title))
        return activity_html

    def find_reviews(self, activity_html):
        rows_html = activity_html.find_all('section',
                                           class_="activity-row -basic")
        description = ''

        for row in rows_html:
            summary_html = row.find('p', class_="activity-summary")
            activity_type = summary_html.find('span', class_='context')
            if activity_type is None:
                break

            if not activity_type.get_text().strip().startswith('reviewed'):
                continue

            self.n_reviews += 1
            # Shares a link to the activity page if more than 5 reviews
            if self.n_reviews > 5:
                description += '[More reviews]({})'.format(link)
                break
            rating = summary_html.find('span', class_="rating")
            date = summary_html.find('span', class_="nobr")
            self.review_link = "https://letterboxd.com"\
                               + summary_html.contents[3]['href']
            description += '[**Review**]({0}) '.format(self.review_link)
            description += '' if rating is None else rating.get_text() + '  '
            description += date.contents[0] if date is not None else ''
            description += '\n'

            if self.n_reviews == 1:
                description += self.get_review_preview()

        if len(description) == 0:
            raise LbxdNotFound('{0} does not have a review for {1}.'
                               .format(self.username, self.film.title))

        self.display_name = rows_html[0].find('a', class_='avatar')\
            .contents[1]['alt']
        return description

    def get_review_preview(self):
        try:
            page_review = s.get(self.review_link)
            page_review.raise_for_status()
        except requests.exceptions.HTTPError:
            return ''
        review_only = SoupStrainer('div', class_='review body-text'
                                                 ' -prose -hero -loose')
        review_preview = BeautifulSoup(page_review.text, "lxml",
                                       parse_only=review_only)
        if review_preview.find('div', class_='contains-spoilers') is not None:
            spoiler_warning = "This review may contain spoilers."
            preview = '\n```' + spoiler_warning + '```'
        else:
            review_text = review_preview.find('div', itemprop='reviewBody')
            preview = format_text(review_text, 400)

        return preview

    def create_embed(self):
        review_word = 'reviews' if self.n_reviews > 1 else 'review'
        embed_link = self.url if self.n_reviews > 1 else self.review_link

        review_embed = discord.Embed(title="{0} {1} of {2}"
                                     .format(self.display_name,
                                             review_word, self.film.title),
                                     url=embed_link, colour=0xd8b437,
                                     description=self.description)

        review_embed.set_thumbnail(url=self.film.poster_path)

        return review_embed
