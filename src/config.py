import json

with open('data_bot.json') as data_file:
    data_dict = json.load(data_file)

cloudinary = data_dict['cloudinary']
letterboxd = data_dict['letterboxd']
mkdb_servers = data_dict['mkdb_servers']
keys = data_dict['keys']
commands = data_dict['commands']
