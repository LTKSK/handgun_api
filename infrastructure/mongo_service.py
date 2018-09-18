# -*- coding: utf-8 -*-
"""
Service module for mongodb

Copyright (C) 2018 Keisuke Tsuji
"""
import pymongo
import handgun_config


_CLIENT = None
_DB_NAME = "handgun"


def _get_client():
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    _CLIENT = pymongo.MongoClient(host=handgun_config.mongo_host(),
                                  port=handgun_config.mongo_port())
    return _CLIENT


def db():
    return _get_client()[_DB_NAME]
