from flask import Flask
import os
import secrets

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    keyfile = os.path.join(app.instance_path, ".flask_secret")
    key = ""
    try:
        with open(keyfile, "r") as f:
            key = f.readline().strip()
    except FileNotFoundError:
        key = secrets.token_hex(64)
        with open(keyfile, "w") as f:
            f.write(key)

    app.config.from_mapping(
        SECRET_KEY=key,
        DATABASE=os.path.join(app.instance_path, "points.sqlite"),
    )

    from . import database
    database.init_app(app)

    from . import endpoints
    app.register_blueprint(endpoints.bp)

    return app
