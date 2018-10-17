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
    return _CONFIG_DATA["MONGODB"]["HOST"]


def mongo_port():
    return int(_CONFIG_DATA["MONGODB"]["PORT"])


def debug_mode():
    return _CONFIG_DATA["APPLICATION"]["DEBUG_MODE"]


def jwt_secret_key():
    return _CONFIG_DATA["APPLICATION"]["AUTHORIZATION"]["SECRET_KEY"]
