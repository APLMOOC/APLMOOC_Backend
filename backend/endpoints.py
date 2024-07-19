from flask import (
    Blueprint, render_template, request, abort
)
import asyncio
import json
import base64

from . import tester
from . import database

bp = Blueprint("endpoints", __name__, url_prefix="/")


@bp.route("/", methods=("GET",))
def index():
    return {"message": "success"}, 200


@bp.route("/get", methods=("GET",))
def get():
    points = database.get_all_points()
    return {"points": points}, 200


@bp.route("/submit", methods=("POST",))
def submit():
    id_problem = request.json.get("id_problem")
    id_user = request.json.get("id_user")
    code_encoded = request.json.get("code_encoded")

    if not all((id_problem, id_user, code_encoded)):
        abort(400)

    # Run demo tests

    code = base64.b64decode(code_encoded).decode("utf-8")
    with open("test_framework/example.json", "r") as f:
        demo_config = json.load(f)
    
    result, feedback = asyncio.run(tester.run_tests(code, demo_config))
    print(result, feedback)

    if result:
        database.insert_points(id_user, id_problem, 1)
        return {"message": "Code successfully executed!", "feedback": feedback}, 200
    else:
        database.insert_points(id_user, id_problem, 0)
        return {"message": "Tests failed!", "feedback": feedback}, 200
