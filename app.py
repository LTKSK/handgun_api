# -*- coding: utf-8 -*-
"""
flask app

Copyright (C) 2018 Keisuke Tsuji
"""
import os
import re
import json
from datetime import datetime
from flask import (
    Flask,
    jsonify,
    request,
    redirect,
    url_for,
    send_from_directory,
    abort)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from infrastructure import mongo_service
from auth import authorization
import handgun_config


app = Flask(__name__)


upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload")
app.config["UPLOAD_FOLDER"] = upload_dir
app.config['JSON_AS_ASCII'] = False
CORS(app)
_ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png"]


@app.route('/')
def index():
    return redirect(url_for("channels"))


@app.route('/users', methods=["POST"])
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


@app.route('/users/<string:username>/icon', methods=["POST", "GET"])
def user_icon(username):
    if request.method == "POST":
        if len(request.files) == 0:
            abort(400)
        # save files
        save_dir = os.path.join(app.config["UPLOAD_FOLDER"], channel)
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
                        "layer": {}}
            review_target_collection.insert_one(document)
        return request.data


@app.route('/login', methods=["POST"])
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


@app.route('/logout', methods=["POST"])
def logout():
    pass


# channel end points
@app.route('/channels', methods=["GET"])
@authorization.require_auth
def get_channels(user_name):
    response = []
    for result in mongo_service.db()["channel"].find():
        # convert _id(bytes) > _id(str). Because bytes date can not jsonify
        result["_id"] = str(result["_id"])
        response.append(result)
    return jsonify(response)


@app.route('/channels', methods=["POST"])
def post_channel():
    collection = mongo_service.db()["channel"]
    data = json.loads(request.data)
    document = {"name": data["name"]}
    collection.insert_one(document)
    return request.data


@app.route('/channels/<string:channel>/review-targets', methods=["POST"])
def post_review_target(channel):
    if len(request.files) == 0:
        abort(400)
    # save files
    save_dir = os.path.join(app.config["UPLOAD_FOLDER"], channel)
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
                    "layer": {}}
        review_target_collection.insert_one(document)
    return request.data


# review_target end points
@app.route('/channels/<string:channel>/review-targets', methods=["GET"])
def get_review_target(channel):
    collection = mongo_service.db()["review_target"]
    review_target_data = collection.find_one({"channel": channel})
    if not review_target_data.get("name"):
        abort(404)
    saved_dir = os.path.join(app.config["UPLOAD_FOLDER"],
                             review_target_data["channel"])
    # now, one file only. multi file will be supported in the future.
    return send_from_directory(saved_dir, review_target_data["name"])


@app.route('/channels/<string:channel>/review-targets/layer', methods=["PUT"])
def update_layer(channel):
    data = json.loads(request.data)
    collection = mongo_service.db()["review_target"]
    collection.update_one(filter={"channel": channel},
                          update={"$set": {"layer": data}})
    return '', 204


@app.route('/channels/<string:channel>/review-targets/layer', methods=["GET"])
def get_layer(channel):
    collection = mongo_service.db()["review_target"]
    document = collection.find_one({"channel": channel})
    if not document:
        return jsonify({})
    return jsonify(document["layer"])


# message end points
@app.route('/channels/<string:channel>/messages', methods=["POST"])
def post_messages(channel):
    data = json.loads(request.data)
    data["channel"] = channel
    data["date"] = datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
    db = mongo_service.db()
    collection = db["message"]
    collection.insert_one(data)
    return request.data


@app.route('/channels/<string:channel>/messages', methods=["GET"])
def get_messages(channel):
    db = mongo_service.db()
    collection = db["message"]
    document = list(collection.find({"channel": channel}).sort("index"))
    if not document:
        return jsonify([])
    for doc_element in document:
        doc_element["_id"] = str(doc_element["_id"])
        doc_element["date"] = doc_element["date"].isoformat()
    return jsonify(document)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=handgun_config.debug_mode())
