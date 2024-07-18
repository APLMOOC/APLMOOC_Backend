from flask import (
    Blueprint, render_template, request
)
import asyncio
from . import tester
from . import database

bp = Blueprint("endpoints", __name__, url_prefix="/")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/get")
def get():
    return "\n".join([str(a) for a in database.query_db("SELECT uid, SUM(points) FROM Points GROUP BY uid")])


@bp.route("/submit", methods=["POST"])
def submit():
    pid = request.form.get("pid")
    uid = request.form.get("uid")
    code = request.form.get("code")
    print(pid,uid,code)

    if not all((pid,uid,code)):
        return "Bad request", 400

    # Run demo test for the ⍴ function
    result, value = asyncio.run(tester.run_tests(code, 
                                [("2 2","⍳4","1 2\n3 4\n"),
                                ("⍴ 0","0","0\n"),
                                ("3 3","1","1 1 1\n1 1 1\n1 1 1\n")
                                ]))
    
    if result:
        database.insert_db("INSERT OR IGNORE INTO Points (uid, pid, points) VALUES (?, ?, ?)", (uid,pid,1))
        database.insert_db("UPDATE Points SET points=? WHERE uid=? AND pid=?", (1,uid,pid))
        return "All tests passed! Points have been awarded on the server.\n"
    else:
        return f"Tests failed!\n{value}"
