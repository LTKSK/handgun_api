# -*- coding: utf-8 -*-
"""
authorization functions

Copyright (C) 2018 Keisuke Tsuji
"""
import functools
import jwt
from flask import request, abort
from werkzeug.security import check_password_hash
import handgun_config
from infrastructure import mongo_service


def encode_jwt(payload):
    return jwt.encode(payload,
                      handgun_config.jwt_secret_key(),
                      algorithm="HS256")


def decode_jwt(token):
    try:
        return jwt.decode(token,
                          handgun_config.jwt_secret_key(),
                          algorithm="HS256")
    except jwt.exceptions.DecodeError:
        abort(400, {"message": "Invalid token"})


def require_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth_data = request.headers.get("Authorization")
        if auth_data is None:
            abort(400, {"message": "Authorization header is required"})
        if len(auth_data.split()) != 2:
            abort(401, {"message": "Invalid header data"})
        # collect auth_data is 'Bearer {token}'
        scheme, token = auth_data.split()
        if scheme.lower() != "bearer":
            abort(401,
                  {"message": "Authorization header must start with Bearer"})
        # decode and find user
        data = decode_jwt(token)
        document_filter = {"name": data["name"]}
        document = mongo_service.db()["user"].find_one(document_filter)
        if document is None:
            abort(401, {"message": "Invalid user"})
        # password check
        if not check_password_hash(document["password"], data["password"]):
            abort(400)
        # add user_name for filtering for find
        return func(*args, autholized_user=data["name"], **kwargs)
    return wrapper
