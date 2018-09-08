# -*- coding: utf-8 -*-
import os
import yaml

_CONFIG_DATA = None

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "config",
                           "handgun_config.yml")
with open(config_path) as config_data:
    _CONFIG_DATA = yaml.load(config_data)

def mongo_host():
    pass

def mongo_port():
    pass
