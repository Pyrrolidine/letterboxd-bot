from .core import *


class Crew(object):

    def __init__(self, input_name, search_type):
        self.url = self.search_letterboxd(input_name, search_type)
        crew_page_html = self.load_crew_page()
        self.display_name = ''
        self.api_url = self.get_tmdb_id(crew_page_html)
        self.description = self.get_movie_credits()
        self.description += self.get_details()
        self.pic_url = self.get_picture()

    def search_letterboxd(self, item, search_type):
        list_search_words = item.split()

        try:
            path = urllib.parse.quote('+'.join(list_search_words))
            page = s.get("https://letterboxd.com/search{0}{1}"
                         .format(search_type, path))
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if page.status_code == 404:
                raise LbxdNotFound("Could not find the film.")
            else:
                print(err)
                raise LbxdServerError("There was a problem trying to "
                                      + "access Letterboxd.com.")

        html_soup = BeautifulSoup(page.text, "lxml")
        results_html = html_soup.find('ul', class_='results')
        if results_html is None:
            raise LbxdNotFound("No results were found with this search.")

        search_html = results_html.find('h2', class_="title-2 prettify")

        link = search_html.find('a')['href']
        return "https://letterboxd.com{}".format(link)

    def load_crew_page(self):
        page = s.get(self.url)
        sidebar_only = SoupStrainer('aside', class_='sidebar')
        return BeautifulSoup(page.text, "lxml",
                             parse_only=sidebar_only)

    def get_tmdb_id(self, crew_page_html):
        tmdb_url = crew_page_html.find('a', class_='micro-button')['href']
        tmdb_id = tmdb_url.split('/')[-2]
        return "https://api.themoviedb.org/3/person/{}".format(tmdb_id)

    def get_movie_credits(self):
        credits_text = ''
        try:
            person_credits = s.get(self.api_url + "/movie_credits?api_key={}"
                                   .format(api_key))
            person_credits.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if person_credits.status_code == 404:
                raise LbxdNotFound("This person does not have a TMDb page.")
            else:
                print(err)
                raise LbxdServerError("There was a problem trying to access "
                                      + "TMDb.")

        director_credits = 0
        writer_credits = 0
        for crew_credit in person_credits.json()['crew']:
            if crew_credit['job'] == 'Director':
                director_credits += 1
            elif crew_credit['job'] == 'Writer':
                writer_credits += 1

        if director_credits:
            credits_text += "**Director**: " + str(director_credits) + '\n'
        if writer_credits:
            credits_text += "**Writer**: " + str(writer_credits) + '\n'

        acting_credits = len(person_credits.json()['cast'])
        if acting_credits:
            credits_text += "**Actor**: " + str(acting_credits) + '\n'

        return credits_text

    def get_details(self):
        details_text = ''
        try:
            person_tmdb = s.get(self.api_url + "?api_key={}".format(api_key))
            person_tmdb.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            raise LbxdServerError("There was a problem trying to access TMDb.")

        self.display_name = person_tmdb.json()['name']

        for element in person_tmdb.json():
            if person_tmdb.json()[element] is None:
                continue
            if element == 'birthday':
                details_text += "**Birthday**: " \
                                + person_tmdb.json()[element] + '\n'
            elif element == 'deathday':
                details_text += "**Day of Death**: " \
                                + person_tmdb.json()[element] + '\n'
            elif element == 'place_of_birth':
                details_text += "**Place of Birth**: " \
                                + person_tmdb.json()[element]

        return details_text

    def get_picture(self):
        img_url = ''
        try:
            person_img = s.get(self.api_url + "/images?api_key={}"
                               .format(api_key))
            person_img.raise_for_status()
            img_url = "https://image.tmdb.org/t/p/w200"
            highest_vote = 0
            for img in person_img.json()['profiles']:
                if img['vote_average'] > highest_vote:
                    highest_vote = img['vote_average']
            for index, img in enumerate(person_img.json()['profiles']):
                if img['vote_average'] == highest_vote:
                    img_url += img['file_path']
                    break
        except requests.exceptions.HTTPError as err:
            pass

        return img_url

    def create_embed(self):
        crew_embed = discord.Embed(title=self.display_name, url=self.url,
                                   description=self.description,
                                   colour=0xd8b437)
        crew_embed.set_thumbnail(url=self.pic_url)
        return crew_embed
