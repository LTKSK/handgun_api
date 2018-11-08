# -*- coding: utf-8 -*-
"""
define messages endpoint

Copyright (C) 2018 Keisuke Tsuji
"""
import os
import json
from datetime import datetime
from flask import (
    Blueprint,
    request,
    jsonify,
    abort,
    send_from_directory,
    make_response)
from infrastructure import mongo_service
from auth import authorization


blueprint = Blueprint("messages", __name__)


# message end points
@blueprint.route('/channels/<string:channel>/messages', methods=["POST"])
def post_messages(channel):
    data = json.loads(request.data)
    data["channel"] = channel
    data["date"] = datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
    db = mongo_service.db()
    collection = db["message"]
    collection.insert_one(data)
    return request.data


@blueprint.route('/channels/<string:channel>/messages', methods=["GET"])
def get_messages(channel):
    collection = mongo_service.db()["message"]
    document = list(collection.find({"channel": channel}).sort("index"))
    if not document:
        return jsonify([])
    for doc_element in document:
        doc_element.pop("_id", None)
        doc_element["date"] = doc_element["date"].isoformat()
    return jsonify(document)


@blueprint.route('/channels/<string:channel>/messages', methods=["PUT"])
def edit_message(channel):
    data = json.loads(request.data)
    collection = mongo_service.db()["message"]
    document_filter = {"channel": channel,
                       "index": data["index"]}
    collection.update_one(document_filter, {"$set": {"value": data["value"]}})
    response = make_response()
    response.status_code = 204
    return response


@blueprint.route('/channels/<string:channel>/messages/<int:index>',
           methods=["DELETE"])
def delete_message(channel, index):
    collection = mongo_service.db()["message"]
    collection.delete_one({"channel": channel,
                           "index": index})
    response = make_response()
    response.status_code = 204
    return response