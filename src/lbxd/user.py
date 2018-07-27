from .core import *
import subprocess
import os
import cloudinary
import cloudinary.uploader


with open('Cloudinary') as cloudinary_file:
    lines = cloudinary_file.readlines()
    cloudinary.config(
        cloud_name=lines[0].strip(),
        api_key=lines[1].strip(),
        api_secret=lines[2].strip()
    )


class User(object):

    def __init__(self, username, with_info=True):
        self.img_cmd = 'convert '
        self.fav_posters_link = list()
        self.fav_posters = ''
        self.user = username.lower()
        self.url = "https://letterboxd.com/{}".format(username)
        self.lbxd_id = self.search_profile()
        if not with_info:
            return
        self.description = self.get_user_infos()
        if not len(self.fav_posters_link):
            return
        if not os.path.exists(username):
            os.popen('mkdir ' + self.user)
        self.fav_img_link = self.upload_cloudinary()
        os.popen('rm -r ' + self.user)

    def search_profile(self):
        params = {'input': self.user,
                  'include': 'MemberSearchItem'}
        response = api.api_call('search', params).json()
        if not len(response['items']):
            raise LbxdNotFound("The user **" + self.user + "** wasn't found.")
        for result in response['items']:
            if result['member']['username'].lower() == self.user:
                self.display_name = result['member']['displayName']
                return result['member']['id']
        raise LbxdNotFound("The user **" + self.user + "** wasn't found.")

    def get_user_infos(self):
        member_json = api.api_call('member/{}'.format(self.lbxd_id)).json()
        self.avatar_url = member_json['avatar']['sizes'][-1]['url']
        description = '**'
        if member_json.get('location'):
            description += member_json['location'] + '** -- **'
        stats_path = 'member/{}/statistics'.format(self.lbxd_id)
        stats_json = api.api_call(stats_path).json()
        description += str(stats_json['counts']['watches']) + ' films**\n'

        for fav_film in member_json['favoriteFilms']:
            fav_name = fav_film['name']
            for poster in fav_film['poster']['sizes']:
                if 150 < poster['width'] < 250:
                    self.fav_posters_link.append(poster['url'])
            if fav_film.get('releaseYear'):
                fav_name += ' (' + str(fav_film['releaseYear']) + ')'
            for link in fav_film['links']:
                if link['type'] == 'letterboxd':
                    fav_url = link['url']
                    temp_url = fav_url.replace('https://letterboxd.com', '')
                    self.fav_posters += temp_url[:-1]
            description += '[{0}]({1})\n'.format(fav_name, fav_url)
        return description

    def download_fav_posters(self):
        for index, fav_poster in enumerate(self.fav_posters_link):
            img_data = s.get(fav_poster).content
            temp_fav = '{0}/fav{1}.jpg'.format(self.user, index)
            self.img_cmd += temp_fav + ' '
            with open(temp_fav, 'wb') as handler:
                handler.write(img_data)

    def upload_cloudinary(self):
        check_album = self.update_favs()
        if len(check_album):
            return check_album
        else:
            self.download_fav_posters()
            self.img_cmd += "+append {}/fav.jpg".format(self.user)
            subprocess.call(self.img_cmd, shell=True)
            with open('{}/fav.jpg'.format(self.user), 'rb') as pic:
                bin_pic = pic.read()
            result = cloudinary.uploader.upload(bin_pic, public_id=self.user,
                                                folder='bot favs',
                                                tags=self.fav_posters)
            return result['url']

    def update_favs(self):
        details_id = urllib.parse.quote(('bot favs/' + self.user)
                                        .encode('utf-8'), '')
        try:
            details = cloudinary.api.resource(details_id)
            if details['tags'][0] == self.fav_posters:
                return details['url']
        except cloudinary.api.NotFound:
            pass
        return ''

    def create_embed(self):
        user_embed = discord.Embed(title=self.display_name, url=self.url,
                                   description=self.description,
                                   colour=0xd8b437)
        user_embed.set_thumbnail(url=self.avatar_url)
        if len(self.fav_posters_link):
            user_embed.set_image(url=self.fav_img_link)

        return user_embed
