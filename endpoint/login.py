# -*- coding: utf-8 -*-
"""
define login endpoint

Copyright (C) 2018 Keisuke Tsuji
"""
import json
from flask import Blueprint, request, jsonify, abort
from werkzeug.security import check_password_hash
from infrastructure import mongo_service
from auth import authorization


blueprint = Blueprint("login", __name__)


@blueprint.route('/login', methods=["POST"])
def login():
    data = json.loads(request.data)
    if not isinstance(data["username"], str):
        abort(400)
    if not isinstance(data["password"], str):
        abort(400)
    document_filter = {"name": data["username"]}
    document = mongo_service.db()["user"].find_one(document_filter)
    if document is None:
        abort(400)
    if not check_password_hash(document["password"], data["password"]):
        abort(400)
    return jsonify({"token":
                    authorization.encode_jwt({
                        "name": data["username"],
                        "password": data["password"]}).decode()
                   })
