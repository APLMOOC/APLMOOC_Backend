from flask import Flask
from flask import request
from flask import render_template
import asyncio
import tester

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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
    return result


if __name__ == "__main__":
    app.run(debug=True, port=5000)