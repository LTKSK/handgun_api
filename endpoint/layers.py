# -*- coding: utf-8 -*-
"""
define layers endpoint

Copyright (C) 2018 Keisuke Tsuji
"""
import os
import json
from flask import Blueprint, request, jsonify, make_response
from pymongo.operations import DeleteMany
from infrastructure import mongo_service


blueprint = Blueprint("layers", __name__)


@blueprint.route('/layers/<string:channel>', methods=["GET"])
def layers(channel):
    collection = mongo_service.db()["layer"]
    response = collection.find_one({"channel": channel})
    if response is None:
        return jsonify([])
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


@blueprint.route('/layers/<string:channel>/<string:layer_id>', methods=["PUT"])
def update_layer(channel, layer_id):
    data = json.loads(request.data)
    collection = mongo_service.db()["layer"]
    collection.update_one(filter={"channel": channel},
                          update={"$set": {"layers": data}})
    return '', 204


@blueprint.route('/layers/<string:channel>/<string:layer_id>',
                 methods=["DELETE"])
def delete_layer(channel, layer_id):
    collection = mongo_service.db()["layer"]
    layer_data = collection.find_one({"channel": channel})
    layer_data["layers"] = [layer for layer in layer_data["layers"]
                            if layer["id"] != layer_id]
    collection.update_one(filter={"channel": channel},
                          update={"$set": layer_data})

    collection = mongo_service.db()["message"]
    delete_operation = DeleteMany({"channel": channel,
                                   "layer_id": layer_id})
    collection.bulk_write([delete_operation])
    response = make_response()
    response.status_code = 204
    return response
