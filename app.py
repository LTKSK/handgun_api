from flask import Flask, redirect, url_for


app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for("chats"))


@app.route('/chats', methods=["GET", "POST"])
def chats():
    return "Hello Chats"


@app.route('/review-targets/<int:chatid>', methods=["GET", "POST", "PUT"])
def review_targets():
    pass


@app.route('/messages/<int:chatid>', methods=["GET", "PUT"])
def messages():
    pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
