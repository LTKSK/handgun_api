# -*- coding: utf-8 -*-
"""
define users endpoint

Copyright (C) 2018 Keisuke Tsuji
"""
import os
import re
import json
from flask import Blueprint, request, jsonify, abort, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from infrastructure import mongo_service
from auth import authorization


_ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png"]
upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload")
blueprint = Blueprint("users", __name__)


@blueprint.route('/users', methods=["GET"])
def users():
    response = []
    for user in list(mongo_service.db()["user"].find()):
        # remove values that doesnt needed.
        user.pop("_id", None)
        user.pop("password", None)
        response.append(user)
    return jsonify(response)


@blueprint.route('/users', methods=["POST"])
def register_user():
    collection = mongo_service.db()["user"]
    data = json.loads(request.data)
    if not re.search(r"^[a-zA-Z0-9]\w*[a-zA-Z0-9]$", data["username"]):
        abort(400)
    if collection.find_one({"name": data["username"]}):
        abort(409)
    document = {"name": data["username"],
                "password": generate_password_hash(data["password"],
                                                   method="sha256")}
    collection.insert_one(document)
    return request.data


@blueprint.route('/users/icons/<string:username>', methods=["POST", "GET"])
def user_icon(username):
    save_dir = os.path.join(upload_dir, "user_icons", username)
    if request.method == "POST":
        if len(request.files) == 0:
            abort(400)
        try:
            os.makedirs(save_dir)
        except FileExistsError:
            pass
        for icon_data in request.files.values():
            extension = icon_data.content_type.split("/")[-1]
            if extension not in _ALLOWED_EXTENSIONS:
                abort(400)
            file_path = os.path.join(save_dir, "icon."+extension)
            icon_data.save(file_path)
        return request.data
    if request.method == "GET":
        saved_dir = os.path.join(upload_dir, "user_icons", username)
        files = os.listdir(save_dir)
        if not files:
            abort(403)
        return send_from_directory(saved_dir, files[0])
