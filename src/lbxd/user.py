from .core import api, create_embed
from .exceptions import LbxdNotFound
import config
import subprocess
import os
import cloudinary
import cloudinary.uploader
import urllib.request

cloudinary.config(
    cloud_name=config.cloudinary['cloud_name'],
    api_key=config.cloudinary['api_key'],
    api_secret=config.cloudinary['api_secret'])


class User:
    def __init__(self, username, with_info=True):
        self._img_cmd = 'convert '
        self._fav_posters_link = list()
        self._fav_posters = ''
        self.avatar_url = ''
        self.display_name = ''
        self.username = username.lower()
        self.url = 'https://letterboxd.com/{}'.format(username)
        self.lbxd_id = self.__check_if_fixed_search()
        fav_img_link = ''
        if not len(self.lbxd_id):
            self.lbxd_id = self.__search_profile()
        description = self.__get_user_infos(with_info)
        if not with_info:
            return
        if len(self._fav_posters_link):
            if not os.path.exists(username):
                os.popen('mkdir ' + self.username)
            fav_img_link = self.__upload_cloudinary()
            os.popen('rm -r ' + self.username)

        self.embed = create_embed(self.display_name, self.url, description,
                                  self.avatar_url, fav_img_link)

    def __check_if_fixed_search(self):
        for fixed_username, lbxd_id in config.fixed_user_search.items():
            if fixed_username.lower() == self.username:
                api_path = 'member/{}'.format(lbxd_id)
                member_json = api.api_call(api_path).json()
                self.display_name = member_json['displayName']
                return lbxd_id
        return ''

    def __search_profile(self):
        username = self.username.replace('_', ' ')
        params = {
            'input': username,
            'include': 'MemberSearchItem',
            'perPage': '100'
        }
        while True:
            response = api.api_call('search', params).json()
            if not len(response['items']):
                break
            for result in response['items']:
                if result['member']['username'].lower() == self.username:
                    self.display_name = result['member']['displayName']
                    return result['member']['id']
            if response.get('next'):
                cursor = response['next']
                params['cursor'] = cursor
            else:
                break
        raise LbxdNotFound('The user **' + self.username + '** wasn\'t found.')

    def __get_user_infos(self, with_info):
        member_response = api.api_call('member/{}'.format(self.lbxd_id))
        if member_response == '':
            raise LbxdNotFound(
                'The user **' + self.username +
                '** wasn\'t found. They may have refused to be reachable via the API.'
            )
        member_json = member_response.json()
        self.avatar_url = member_json['avatar']['sizes'][-1]['url']
        if not with_info:
            return
        description = '**'
        if member_json.get('location'):
            description += member_json['location'] + '** -- **'
        stats_path = 'member/{}/statistics'.format(self.lbxd_id)
        stats_json = api.api_call(stats_path).json()
        description += str(stats_json['counts']['watches']) + ' films**\n'

        for fav_film in member_json['favoriteFilms']:
            fav_name = fav_film['name']
            if fav_film.get('poster'):
                for poster in fav_film['poster']['sizes']:
                    if 150 < poster['width'] < 250:
                        self._fav_posters_link.append(poster['url'])
            if fav_film.get('releaseYear'):
                fav_name += ' (' + str(fav_film['releaseYear']) + ')'
            for link in fav_film['links']:
                if link['type'] == 'letterboxd':
                    fav_url = link['url']
                    temp_url = fav_url.replace('https://letterboxd.com', '')
                    self._fav_posters += temp_url[:-1]
            description += '[{0}]({1})\n'.format(fav_name, fav_url)
        return description

    def __download_fav_posters(self):
        for index, fav_poster in enumerate(self._fav_posters_link):
            img_data = api.session.get(fav_poster).content
            temp_fav = '{0}/fav{1}.jpg'.format(self.username, index)
            self._img_cmd += temp_fav + ' '
            with open(temp_fav, 'wb') as handler:
                handler.write(img_data)

    def __upload_cloudinary(self):
        check_album = self.__update_favs()
        if len(check_album):
            return check_album
        else:
            self.__download_fav_posters()
            self._img_cmd += '+append {}/fav.jpg'.format(self.username)
            subprocess.call(self._img_cmd, shell=True)
            with open('{}/fav.jpg'.format(self.username), 'rb') as pic:
                bin_pic = pic.read()
            result = cloudinary.uploader.upload(
                bin_pic,
                public_id=self.username,
                folder='bot favs',
                tags=self._fav_posters)
            return result['url']

    def __update_favs(self):
        details_id = urllib.parse.quote(
            ('bot favs/' + self.username).encode('utf-8'), '')
        try:
            details = cloudinary.api.resource(details_id)
            if details['tags'][0] == self._fav_posters:
                return details['url']
        except cloudinary.api.NotFound:
            pass
        return ''
