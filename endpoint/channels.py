# -*- coding: utf-8 -*-
"""
define channels endpoint

Copyright (C) 2018 Keisuke Tsuji
"""
import json
from flask import Blueprint, request, jsonify, abort, make_response
from infrastructure import mongo_service
from auth import authorization


blueprint = Blueprint("channels", __name__)


# channel end points
@blueprint.route('/channels', methods=["GET"])
@authorization.require_auth
def get_channels(authorized_user):
    response = []
    for result in mongo_service.db()["channel"].find():
        # pop _id(bytes) > _id(str). Because bytes date can not jsonify
        result.pop("_id", None)
        response.append(result)
    return jsonify(response)


@blueprint.route('/channels', methods=["POST"])
@authorization.require_auth
def post_channel(authorized_user):
    collection = mongo_service.db()["channel"]
    data = json.loads(request.data)
    document = {"name": data["name"],
                "users": [authorized_user]}
    collection.insert_one(document)
    return request.data


@blueprint.route('/channels/<string:channel>', methods=["DELETE"])
@authorization.require_auth
def delete_channel(channel, authorized_user):
    collection = mongo_service.db()["channel"]
    result = collection.delete_one({"name": channel,
                                    "users": {"$in": [authorized_user]}})
    # if delete_count 0, authorized_user does not delete the channel
    if result.deleted_count == 0:
        abort(403)
    collection = mongo_service.db()["message"]
    collection.delete_many({"channel": channel})
    response = make_response()
    response.status_code = 204
    return response


@blueprint.route('/channels/<string:channel>/users', methods=["PUT"])
@authorization.require_auth
def put_channel_users(channel, authorized_user):
    collection = mongo_service.db()["channel"]
    data = json.loads(request.data)
    update = {"$set": {"users": data["users"]}}
    collection.update_one(filter={"channel": channel,
                                  "users": {"$in": [authorized_user]}},
                          update=update,
                          upsert=True)
    return request.data
