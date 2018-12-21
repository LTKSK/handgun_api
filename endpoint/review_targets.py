# -*- coding: utf-8 -*-
"""
define login endpoint

Copyright (C) 2018 Keisuke Tsuji
"""
import os
import json
from flask import Blueprint, request, jsonify, abort, send_from_directory
from werkzeug.utils import secure_filename
from infrastructure import mongo_service
from auth import authorization


_ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png"]
upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload")
blueprint = Blueprint("review_targets", __name__)


@blueprint.route('/channels/<string:channel>/review-targets', methods=["POST"])
@authorization.require_auth
def post_review_target(channel, authorized_user):
    if len(request.files) == 0:
        abort(400)
    # save files
    save_dir = os.path.join(upload_dir, channel)
    try:
        os.mkdir(save_dir)
    except FileExistsError:
        pass
    # upload files (but now, there is one file in files)
    review_target_collection = mongo_service.db()["review_target"]
    for review_target in request.files.values():
        filename = secure_filename(review_target.filename)
        if filename.split(".")[-1] not in _ALLOWED_EXTENSIONS:
            abort(400)
        file_path = os.path.join(save_dir, filename)
        if os.path.exists(file_path):
            abort(403)
        review_target.save(file_path)
        document = {"channel": channel,
                    "name": filename,
                    "users": [authorized_user]}
        review_target_collection.insert_one(document)
    return request.data


# review_target end points
@blueprint.route('/channels/<string:channel>/review-targets', methods=["GET"])
# @authorization.require_auth
def get_review_target(channel):
    collection = mongo_service.db()["review_target"]
    review_target_data = collection.find_one({"channel": channel})
    if not review_target_data.get("name"):
        abort(404)
    saved_dir = os.path.join(upload_dir, review_target_data["channel"])
    # now, one file only. multi file will be supported in the future.
    return send_from_directory(saved_dir, review_target_data["name"])
