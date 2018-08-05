import json

with open('config.json') as config_file:
    config_dict = json.load(config_file)

cloudinary = config_dict['cloudinary']
letterboxd = config_dict['letterboxd']
mkdb_servers = config_dict['mkdb_servers']
keys = config_dict['keys']
