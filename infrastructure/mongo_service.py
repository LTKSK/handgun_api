# -*- coding: utf-8 -*-
"""
Service module for mongodb

Copyright (C) 2018 Keisuke Tsuji
"""
import pymongo
import config


_CLIENT = None
_DB_NAME = "handgun"


def _get_client():
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    _CLIENT = pymongo.MongoClient(host=config.mongo_host(),
                                  port=config.mongo_port())
    return _CLIENT


def db():
    return _get_client()[_DB_NAME]
