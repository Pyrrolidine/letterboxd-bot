""" Fetch the configuration values and keys from config.json
"""

import json

with open('config.json') as config_file:
    SETTINGS = json.load(config_file)
