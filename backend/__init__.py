from flask import Flask
import os
import secrets

def create_app():
    """
    Application factory for the APLMOOC_Backend application.

    Returns:
        Flask: the Flask application to run
    """
    
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
        SQLALCHEMY_DATABASE_URI="sqlite:///points.db",
    )

    from . import database
    database.db.init_app(app)
    with app.app_context():
        database.db.create_all()

    from . import endpoints
    app.register_blueprint(endpoints.bp)

    @app.errorhandler(400)
    def error_400(e):
        return {"error": "Bad Request"}, 400

    @app.errorhandler(404)
    def error_404(e):
        return {"error": "Not Found"}, 404

    @app.errorhandler(405)
    def error_405(e):
        return {"error": "Method Not Allowed"}, 405

    @app.errorhandler(415)
    def error_415(e):
        return {"error": "Unsupported Media Type"}, 415

    @app.errorhandler(500)
    def error_500(e):
        return {"error": "Interal Server Error"}, 500

    return app
