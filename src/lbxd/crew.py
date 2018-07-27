from .core import *


class Crew(object):

    def __init__(self, input_name, alias):
        self.description = self.search_letterboxd(input_name, alias)
        self.description += self.get_details()
        self.pic_url = self.get_picture()

    def search_letterboxd(self, item, alias):
        params = {'input': item,
                  'include': 'ContributorSearchItem'}
        if alias in ['a', 'actor']:
            params['contributionType'] = 'Actor'
        elif alias in ['d', 'director']:
            params['contributionType'] = 'Director'
        response = api.api_call('search', params)
        if not len(response.json()['items']):
            raise LbxdNotFound('No person was found with this search.')
        person_json = response.json()['items'][0]['contributor']
        for link in person_json['links']:
            if link['type'] == 'tmdb':
                tmdb_id = link['id']
            elif link['type'] == 'letterboxd':
                self.url = link['url']
        self.api_url = "https://api.themoviedb.org/3/person/{}".format(tmdb_id)

        description = ''
        for contrib_stats in person_json['statistics']['contributions']:
            description += '**' + contrib_stats['type'] + ':** '
            description += str(contrib_stats['filmCount']) + '\n'
        return description

    def get_details(self):
        details_text = ''
        url = self.api_url + "?api_key={}".format(tmdb_api_key)
        try:
            person_tmdb = s.get(url)
            person_tmdb.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            raise LbxdServerError("There was a problem trying to access TMDb.")

        self.display_name = person_tmdb.json()['name']

        for element in person_tmdb.json():
            if person_tmdb.json()[element] is None:
                continue
            if element == 'birthday':
                details_text += "**Birthday:** " \
                                + person_tmdb.json()[element] + '\n'
            elif element == 'deathday':
                details_text += "**Day of Death:** " \
                                + person_tmdb.json()[element] + '\n'
            elif element == 'place_of_birth':
                details_text += "**Place of Birth:** " \
                                + person_tmdb.json()[element]

        return details_text

    def get_picture(self):
        img_url = ''
        try:
            person_img = s.get(self.api_url + "/images?api_key={}"
                               .format(tmdb_api_key))
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
