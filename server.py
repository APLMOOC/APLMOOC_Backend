from flask import Flask
from flask import request
from flask import render_template
from flask import g
import asyncio
import tester
import database

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get")
def get():
    for row in database.query_db("SELECT * FROM Points"):
        print(row)
    return "ok"


@app.route("/submit", methods=["POST"])
def submit():
    pid = request.form.get("pid")
    uid = request.form.get("uid")
    code = request.form.get("code")

    if not all((pid,uid,code)):
        return "Bad request", 400

    # Run demo test for the ⍴ function
    result = asyncio.run(tester.run_tests(code, 
                                [("2 2","⍳4","1 2\n3 4\n"),
                                ("⍴ 0","0","0\n"),
                                ("3 3","1","1 1 1\n1 1 1\n1 1 1\n")
                                ]))
    
    if result:
        database.insert_db("INSERT INTO Points (uid, pid, points) VALUES (?, ?, ?)", (uid,pid,1))
        return "All tests passed!\n"
    else:
        return "Tests failed\n"

if __name__ == "__main__":
    database.init_db()
    app.run(debug=True, port=5000)