# -*- coding: utf-8 -*-

import logging
from lib.util import read_config_file, get_value

# Choose log level here
# TODO: add this to config file
level=logging.DEBUG


config = read_config_file()
logging.basicConfig(filename=get_value(config, "log_file"), level=level, format='%(asctime)s %(message)s')

# This is due the "file_cache is unavailable when using oauth2client >= 4.0.0" issue
# https://github.com/google/google-api-python-client/issues/299
logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)