import json

with open('config.json') as config_file:
    config_dict = json.load(config_file)

cloudinary = config_dict['cloudinary']
letterboxd = config_dict['letterboxd']
mkdb_servers = config_dict['mkdb_servers']
keys = config_dict['keys']
test_server = config_dict['test_server']
fixed_film_search = config_dict['fixed_film_search']
help_text = config_dict['help']
