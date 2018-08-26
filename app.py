# -*- coding: utf-8 -*-
"""
flask app

Copyright (C) 2018 Keisuke Tsuji
"""
from flask import (
    Flask,
    jsonify,
    request,
    redirect,
    url_for)
from flask_cors import CORS
from infrastructure import mongo_service
app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return redirect(url_for("chats"))


@app.route('/chats', methods=["GET"])
def get_chats():
    db = mongo_service.db()
    response = []
    for result in db["chat"].find():
        result["_id"] = str(result["_id"])
        response.append(result)
    return jsonify(response)


@app.route('/chats/<string:name>', methods=["POST"])
def post_chats(name):
    db = mongo_service.db()
    collection = db["chat"]
    document = {"name": name,
                "messages": []}
    collection.insert_one(document)
    return request.data


@app.route('/review-targets/<string:chatname>', methods=["GET", "POST", "PUT"])
def review_targets(chatname):
    pass


@app.route('/messages/<string:chatname>', methods=["GET", "PUT"])
def messages(chatname):
    pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
