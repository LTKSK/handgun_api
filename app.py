# -*- coding: utf-8 -*-
"""
flask app

Copyright (C) 2018 Keisuke Tsuji
"""
from flask import Flask
from flask_cors import CORS
from endpoint import login
from endpoint import users
from endpoint import channels
from endpoint import review_targets
from endpoint import messages
from endpoint import layers
import handgun_config


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)


app.register_blueprint(login.blueprint)
app.register_blueprint(users.blueprint)
app.register_blueprint(channels.blueprint)
app.register_blueprint(review_targets.blueprint)
app.register_blueprint(messages.blueprint)
app.register_blueprint(layers.blueprint)


if __name__ == "__main__":
    app.run(host=handgun_config.server_host(),
            port=handgun_config.server_port(),
            debug=handgun_config.debug_mode())
