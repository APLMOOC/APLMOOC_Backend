from flask import (
    Blueprint, render_template, request, abort
)
import asyncio

from . import tester
from . import database

bp = Blueprint("endpoints", __name__, url_prefix="/")


@bp.route("/", methods=("GET",))
def index():
    return {"message": "success"}, 200


@bp.route("/get", methods=("GET",))
def get():
    res = database.get_all_points()
    return {"points": res}, 200


@bp.route("/submit", methods=("POST",))
def submit():
    id_problem = request.json.get("id_problem")
    id_user = request.json.get("id_user")
    code = request.json.get("code")

    if not all((id_problem, id_user, code)):
        abort(400)
    
    # Run demo test for the ⍴ function
    result, value = asyncio.run(tester.run_tests(code, 
                                [("2 2","⍳4","1 2\n3 4\n"),
                                ("⍴ 0","0","0\n"),
                                ("3 3","1","1 1 1\n1 1 1\n1 1 1\n")
                                ]))
    
    if result:
        database.insert_points(id_user, id_problem, 1)
        return {"message": "All tests passed! Points have been awarded on the server."}, 200
    else:
        return {"message": "Tests failed!", "result": value}, 200
