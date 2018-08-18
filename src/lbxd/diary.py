from .core import api
from .exceptions import LbxdNotFound
import discord


class Diary(object):
    def __init__(self, user):
        self.user = user

    def create_embed(self):
        title = 'Recent diary activity from {}'.format(self.user.display_name)
        diary_embed = discord.Embed(
            title=title, url=self.user.url, colour=0xd8b437, description='')
        diary_embed.set_thumbnail(url=self.user.avatar_url)
        return diary_embed
