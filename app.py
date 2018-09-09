# -*- coding: utf-8 -*-
"""
flask app

Copyright (C) 2018 Keisuke Tsuji
"""
import os
import json
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
from infrastructure import mongo_service


app = Flask(__name__)

upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload")
app.config["UPLOAD_FOLDER"] = upload_dir
app.config['JSON_AS_ASCII'] = False
CORS(app)
_ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png"]


@app.route('/')
def index():
    return redirect(url_for("channels"))


# channel end points
@app.route('/channels', methods=["GET"])
def get_channels():
    response = []
    for result in mongo_service.db()["channel"].find():
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


@app.route('/channels/<string:channel>/review-target', methods=["POST"])
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
    db = mongo_service.db()
    for review_target in request.files.values():
        filename = secure_filename(review_target.filename)
        if filename.split(".")[-1] not in _ALLOWED_EXTENSIONS:
            abort(400)
        file_path = os.path.join(save_dir, filename)
        if os.path.exists(file_path):
            abort(403)
        review_target.save(file_path)
        review_target_collection = db["review_target"]
        document = {"channel": channel,
                    "name": filename}
        review_target_collection.insert_one(document)
    return request.data


# review_target end points
@app.route('/channels/<string:channel>/review-target', methods=["GET"])
def get_review_target(channel):
    collection = mongo_service.db()["review_target"]
    query = {"channel": channel}
    review_target_data = collection.find_one(query)
    if not review_target_data.get("name"):
        abort(404)
    saved_dir = os.path.join(app.config["UPLOAD_FOLDER"],
                             review_target_data["channel"])
    # now, one file only. multi file will be supported in the future.
    result = send_from_directory(saved_dir, review_target_data["name"])
    return result


@app.route('/channels/<string:channel>/review-target/layer', methods=["POST", "PUT"])
def post_layer(channel):
    data = json.loads(request.data)
    data["channel"] = channel
    db = mongo_service.db()
    collection = db["review_target"]
    if request.method == "POST":
        collection.insert_one(data)
        return request.data
    # in PUT case
    collection.update_one(filter={"channel": channel},
                          update=data)
    return jsonify(data)



@app.route('/channels/<string:channel>/review-target/layer', methods=["GET"])
def get_layer(channel):
    db = mongo_service.db()
    collection = db["review_target"]
    document = list(collection.find({"channel": channel}))
    if not document:
        return jsonify([])
    for doc_element in document:
        doc_element["_id"] = str(doc_element["_id"])
    return jsonify(document)


# message end points
@app.route('/channels/<string:channel>/messages', methods=["POST"])
def post_messages(channel):
    if request.method == "POST":
        data = json.loads(request.data)
        data["channel"] = channel
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
    return jsonify(document)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
