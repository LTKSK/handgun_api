# -*- coding: utf-8 -*-
"""
flask app

Copyright (C) 2018 Keisuke Tsuji
"""
import os
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
app.config["UPLOAD_FOLDER"] = os.environ["HUNDGUN_UPLOAD_FOLDER"]
CORS(app)
_ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png"]


@app.route('/')
def index():
    return redirect(url_for("channels"))


@app.route('/channels', methods=["GET"])
def get_channels():
    db = mongo_service.db()
    response = []
    for result in db["channel"].find():
        result["_id"] = str(result["_id"])
        response.append(result)
    return jsonify(response)


@app.route('/channels/<string:name>', methods=["POST"])
def post_channels(name):
    if len(request.files) == 0:
        abort(400)
    # save files
    save_dir = os.path.join(app.config["UPLOAD_FOLDER"], name)
    try:
        os.mkdir(save_dir)
    except FileExistsError:
        pass
    # upload files (but now, there is one file in files)
    for review_target in request.files.values():
        filename = secure_filename(review_target.filename)
        if filename.split(".")[-1] not in _ALLOWED_EXTENSIONS:
            abort(400)
        file_path = os.path.join(save_dir, filename)
        if request.method == "POST" and os.path.exists(file_path):
            abort(403)
        review_target.save(file_path)

    db = mongo_service.db()
    collection = db["channel"]
    document = {"name": name, "messages": []}
    collection.insert_one(document)
    return request.data


@app.route('/review-targets/<string:channelname>', methods=["GET"])
def get_review_target(channelname):
    saved_dir = os.path.join(app.config["UPLOAD_FOLDER"], channelname)
    file_names = os.listdir(saved_dir)
    if not file_names:
        abort(404)
    # now, one file only. multi file will be supported in the future.
    return send_from_directory(saved_dir, file_names[0])


@app.route('/messages/<string:channelname>', methods=["GET", "PUT"])
def get_messages(channelname):
    pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
