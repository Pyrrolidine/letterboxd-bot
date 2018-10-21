""" User command functions
    user_details() is used by review.py and list.py
    It uses the Cloudinary API to host the user's favourite films image
"""

import os
import subprocess

import cloudinary
import cloudinary.uploader
from config import SETTINGS

from .api import api_call, api_session
from .helpers import create_embed
from .exceptions import LbxdNotFound

cloudinary.config(
    cloud_name=SETTINGS['cloudinary']['cloud_name'],
    api_key=SETTINGS['cloudinary']['api_key'],
    api_secret=SETTINGS['cloudinary']['api_secret'])


def user_embed(username):
    username = username.lower()
    url = 'https://letterboxd.com/{}'.format(username)
    lbxd_id = __check_if_fixed_search(username)
    if not lbxd_id:
        lbxd_id = __search_profile(username)
    description, display_name, avatar_url, fav_posters_link = __get_user_infos(
        username, True, lbxd_id)
    fav_img_link = ''
    if fav_posters_link:
        fav_img_link = __upload_fav_posters(username, fav_posters_link)
    return create_embed(display_name, url, description, avatar_url,
                        fav_img_link)


def user_details(username):
    username = username.lower()
    url = 'https://letterboxd.com/{}'.format(username)
    lbxd_id = __check_if_fixed_search(username)
    if not lbxd_id:
        lbxd_id = __search_profile(username)
    display_name, avatar_url = __get_user_infos(username, False, lbxd_id)
    return username, display_name, lbxd_id, avatar_url


def __check_if_fixed_search(username):
    for fixed_username, lbxd_id in SETTINGS['fixed_user_search'].items():
        if fixed_username.lower() == username:
            return lbxd_id
    return ''


def __search_profile(username):
    params = {
        'input': username.replace('_', ' '),
        'include': 'MemberSearchItem',
        'perPage': '100'
    }
    while True:
        response = api_call('search', params).json()
        if not response['items']:
            break
        for result in response['items']:
            if result['member']['username'].lower() == username:
                return result['member']['id']
        if response.get('next'):
            params['cursor'] = response['next']
        else:
            break
    raise LbxdNotFound('The user **' + username + '** wasn\'t found.')


def __get_user_infos(username, with_extra_info, lbxd_id):
    member_response = api_call('member/{}'.format(lbxd_id))
    if member_response == '':
        raise LbxdNotFound(
            'The user **' + username + '** wasn\'t found.' +
            ' They may have refused to be reachable via the API.')
    member_json = member_response.json()
    display_name = member_json['displayName']
    avatar_url = member_json['avatar']['sizes'][-1]['url']
    if not with_extra_info:
        return display_name, avatar_url
    description = '**'
    if member_json.get('location'):
        description += member_json['location'] + '** -- **'
    stats_json = api_call('member/{}/statistics'.format(lbxd_id)).json()
    description += str(stats_json['counts']['watches']) + ' films**\n'

    fav_posters_link = list()
    for fav_film in member_json['favoriteFilms']:
        fav_name = fav_film['name']
        if fav_film.get('poster'):
            for poster in fav_film['poster']['sizes']:
                if 150 < poster['width'] < 250:
                    fav_posters_link.append(poster['url'])
        if fav_film.get('releaseYear'):
            fav_name += ' (' + str(fav_film['releaseYear']) + ')'
        for link in fav_film['links']:
            if link['type'] == 'letterboxd':
                fav_url = link['url']
        description += '[{0}]({1})\n'.format(fav_name, fav_url)
    return description, display_name, avatar_url, fav_posters_link


def __upload_fav_posters(username, fav_posters_link):
    # Download posters
    if not os.path.exists(username):
        os.popen('mkdir ' + username)
    img_cmd = 'convert '
    for index, fav_poster in enumerate(fav_posters_link):
        img_data = api_session.get(fav_poster).content
        temp_fav = '{0}/fav{1}.jpg'.format(username, index)
        img_cmd += temp_fav + ' '
        with open(temp_fav, 'wb') as handler:
            handler.write(img_data)

    # Upload to Cloudinary
    img_cmd += '+append {}/fav.jpg'.format(username)
    subprocess.call(img_cmd, shell=True)
    with open('{}/fav.jpg'.format(username), 'rb') as pic:
        bin_pic = pic.read()
    os.popen('rm -r ' + username)
    result = cloudinary.uploader.upload(
        bin_pic, public_id=username, folder='bot favs')
    return result['url']
