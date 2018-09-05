# -*- coding: utf-8 -*-
"""
Service module for mongodb

Copyright (C) 2018 Keisuke Tsuji
"""
import pymongo


_CLIENT = None
_DB_NAME = "handgun"


def _get_client():
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    _CLIENT = pymongo.MongoClient('localhost', 27017)
    return _CLIENT


def db():
    return _get_client()[_DB_NAME]
