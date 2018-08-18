from .core import api
from .exceptions import LbxdNotFound
import discord


class Diary(object):
    def __init__(self, user):
        pass

    def create_embed(self):
        diary_embed = discord.Embed(title='', colour=0xd8b437, description='')
        return diary_embed
