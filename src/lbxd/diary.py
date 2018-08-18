from .core import api
from .exceptions import LbxdNotFound
import discord


class Diary(object):
    def __init__(self, user):
        self.user = user

    def create_embed(self):
        diary_embed = discord.Embed(title='', colour=0xd8b437, description='')
        diary_embed.set_thumbnail(url=self.user.avatar_url)
        return diary_embed
