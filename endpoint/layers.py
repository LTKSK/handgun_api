# -*- coding: utf-8 -*-
"""
define layers endpoint

Copyright (C) 2018 Keisuke Tsuji
"""
import os
import json
from flask import Blueprint, request, jsonify
from infrastructure import mongo_service


blueprint = Blueprint("layers", __name__)


@blueprint.route('/layers/<string:channel>', methods=["GET"])
def layers(channel):
    collection = mongo_service.db()["layer"]
    response = collection.find_one({"channel": channel})
    response.pop("_id", None)
    return jsonify(response)


@blueprint.route('/layers/<string:channel>', methods=["PUT"])
def update_layers(channel):
    data = json.loads(request.data)
    collection = mongo_service.db()["layer"]
    collection.update_one(filter={"channel": channel},
                          update={"$set": {"channel": channel,
                                           "layers": data}},
                          upsert=True)
    return '', 204


@blueprint.route('/layers/<string:channel>/<int:id>', methods=["PUT"])
def update_layer(channel, id):
    data = json.loads(request.data)
    collection = mongo_service.db()["layer"]
    collection.update_one(filter={"channel": channel},
                          update={"$set": {"layers": data}})
    return '', 204
