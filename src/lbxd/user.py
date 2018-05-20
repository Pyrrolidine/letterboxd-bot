from .core import *
import subprocess
import os


class User(object):

    def __init__(self, username):
        self.img_cmd = 'convert '
        self.user = username.lower()
        self.url = "https://letterboxd.com/{}".format(username)
        self.profile_html = self.load_profile()
        self.display_name = self.get_display_name()
        self.description = self.get_metadata()
        self.description += self.get_nb_films_viewed()
        self.avatar_url = self.get_avatar()
        if not os.path.exists(username):
            os.popen('mkdir ' + self.user)
        self.description += self.get_favourites()
        if len(self.fav_posters_link):
            self.fav_img_link = self.upload_imgur()
        os.popen('rm -r ' + self.user)

    def load_profile(self):
        try:
            page = s.get(self.url)
            page.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if page.status_code == 404:
                raise LbxdNotFound('Could not find this user.')
            print(err)
            raise LbxdServerError('There was a problem trying to access'
                                  + ' Letterboxd.com')

        contents_only = SoupStrainer('div', class_='content-wrap')
        return BeautifulSoup(page.text, "lxml", parse_only=contents_only)

    def get_display_name(self):
        name_div_html = self.profile_html.find('div',
                                               class_='profile-person-info')
        return name_div_html.find('h1', class_='title-1').contents[0]

    def get_metadata(self):
        metadata_html = self.profile_html.find('ul', class_='person-metadata')
        if metadata_html is not None:
            location_html = metadata_html.find('li', class_='icon-location')
            if location_html is not None:
                location = location_html.get_text()
                if isinstance(location, str):
                    return '**' + location + '** -- '
        return ''

    def get_nb_films_viewed(self):
        nbfilms_html = self.profile_html.find('ul', class_='stats')
        nbfilms = nbfilms_html.find('a').contents[0].contents[0]
        return "**" + nbfilms + " films**\n"

    def get_favourites(self):
        fav_text = ''
        fav_html = self.profile_html.find(id="favourites")
        a_html = fav_html.find_all('a')
        self.fav_posters = ''
        self.fav_posters_link = list()

        if a_html[0].get('title') is not None:
            fav_text += '**Favourite Films**:\n'
            for fav in a_html:
                fav_text += '[' + fav['title'] + ']'
                fav_link = 'https://letterboxd.com{}'.format(fav['href'][:-1])
                page = s.get(fav_link + '/image-150')
                fav_pic_html = BeautifulSoup(page.text, 'lxml')
                temp_link = fav_pic_html.find('img')['src']
                if 'empty-poster' not in temp_link:
                    self.fav_posters_link.append(temp_link)
                    self.fav_posters += fav['href'][:-1]
                fav_text += "(https://letterboxd.com{})"\
                            .format(fav['href'][:-1]) + '\n'

        return fav_text

    def download_fav_posters(self):
        for index, fav_poster in enumerate(self.fav_posters_link):
            img_data = s.get(fav_poster).content
            temp_fav = '{0}/fav{1}.jpg'.format(self.user, index)
            self.img_cmd += temp_fav + ' '
            with open(temp_fav, 'wb') as handler:
                handler.write(img_data)

    def upload_imgur(self):
        check_album = self.update_favs()
        if len(check_album):
            return check_album
        else:
            self.download_fav_posters()
            self.img_cmd += "+append {}/fav.jpg".format(self.user)
            subprocess.call(self.img_cmd, shell=True)
            pic = open('{}/fav.jpg'.format(self.user), 'rb')
            bin_pic = pic.read()
            data_img = {'image': bin_pic, 'album': 'UkyHMMy'}
            data_img['title'] = self.user
            data_img['description'] = self.fav_posters
            api_upload = 'https://api.imgur.com/3/image'
            imgur_upload = s.post(api_upload, headers=token_header,
                                  data=data_img)
            return imgur_upload.json()['data']['link']

    def update_favs(self):
        album_api = 'https://api.imgur.com/3/album/UkyHMMy/images'
        fav_album = s.get(album_api, headers=token_header)
        for fav_set in fav_album.json()['data']:
            if fav_set['title'] == self.user:
                if not fav_set['description'] == self.fav_posters:
                    delete_imgur = 'https://api.imgur.com/3/image/'
                    s.delete(delete_imgur + fav_set['deletehash'],
                             headers=token_header)
                    return ''
                else:
                    return fav_set['link']
        return ''

    def get_avatar(self):
        img_div_html = self.profile_html.find('div', class_='profile-avatar')
        return img_div_html.find('img')['src']

    def create_embed(self):
        user_embed = discord.Embed(title=self.display_name, url=self.url,
                                   description=self.description,
                                   colour=0xd8b437)
        user_embed.set_thumbnail(url=self.avatar_url)
        if len(self.fav_posters_link):
            user_embed.set_image(url=self.fav_img_link)

        return user_embed
