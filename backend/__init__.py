"""This file initialises the APL MOOC backend server.

Please check the README.md file for deployment and running instructions.
"""

import os
import secrets
import shutil
from flask import Flask

def setup_directory(app: Flask, testing: bool) -> str:  # pragma: no cover
    """
    Setup working directory for the application.

    Args:
        app (Flask): The Flask application instance
        testing (bool): Whether this application is being tested or not

    Returns:
        str: The secret key for the Flask application
    """

    if testing:
        try:
            shutil.rmtree(app.instance_path)
        except FileNotFoundError:
            pass

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    keyfile = os.path.join(app.instance_path, ".flask_secret")
    key = ""
    try:
        with open(keyfile, "r", encoding="utf-8") as f:
            key = f.readline().strip()
    except FileNotFoundError:
        key = secrets.token_hex(64)
        with open(keyfile, "w", encoding="utf-8") as f:
            f.write(key)

    return key


def create_app(testing: bool = False) -> Flask:
    """
    Application factory for the APLMOOC_Backend application.

    Args:
        testing (bool, optional):
            Indicates whether to create a new, empty instance for testing purposes.
            Defaults to `False`.

    Returns:
        Flask: the Flask application to run
    """

    instance_folder = "instance" if not testing else "instance_test"
    app = Flask(__name__, instance_path=os.path.join(os.getcwd(), instance_folder))

    key = setup_directory(app, testing)

    app.config.from_mapping(
        TESTING=testing,
        SECRET_KEY=key,
        SQLALCHEMY_DATABASE_URI="sqlite:///points.db",
    )

    from . import database  # pylint: disable=import-outside-toplevel
    database.db.init_app(app)
    app.register_blueprint(database.bp)

    from . import endpoints  # pylint: disable=import-outside-toplevel
    app.register_blueprint(endpoints.bp)

    @app.errorhandler(400)
    def error_400(error):
        del error
        return {"error": "Bad Request"}, 400

    @app.errorhandler(404)
    def error_404(error):
        del error
        return {"error": "Not Found"}, 404

    @app.errorhandler(405)
    def error_405(error):
        del error
        return {"error": "Method Not Allowed"}, 405

    @app.errorhandler(415)
    def error_415(error):
        del error
        return {"error": "Unsupported Media Type"}, 415

    @app.errorhandler(500)
    def error_500(error):  # pragma: no cover
        del error
        return {"error": "Interal Server Error"}, 500

    return app
