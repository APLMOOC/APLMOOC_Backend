"""This file provides the API endpoints for the APL MOOC backend.

Endpoints receive data from the users, sanitise them,
and call the database and grader functions to perform functionality.
Swagger documentation can be generated from the function docstrings.
"""

import asyncio
import json
import base64
from flask import (
    Blueprint, request, abort
)

from . import grader
from . import database

bp = Blueprint("endpoints", __name__, url_prefix="/")


@bp.route("/", methods=("GET",))
def index():
    """
    Index endpoint.
    Returns a success message for testing purposes.
    ---
    parameters:
    responses:
        200:
            description: Application is responding
    """

    return {"message": "success"}, 200


@bp.route("/get", methods=("GET",))
def get():
    """
    Get the students' point totals from the database.
    ---
    parameters:
    definitions:
        Points:
            type: object
            properties:
                points:
                    type: array
                    items:
                        $ref: '#/definitions/UserPoints'
        UserPoints:
            type: object
            properties:
                id_user:
                    type: string
                points:
                    type: int
    responses:
        200:
            description: A JSON object containing the total number of points for each student
            schema:
                $ref: '#/definitions/Points'
            examples:
                example: [{"id_user": "1", "points": "2"}, {"id_user": "3", "points": "7"}]
    """

    points = database.get_all_points()
    return {"points": points}, 200


@bp.route("/submit", methods=("POST",))
def submit():
    """
    Submit students' APL code to the backend for evaluation.
    This endpoint will test the submitted code for a given problem,
    and award points based on the tests passed.
    ---
    parameters:
        - name: id_problem
          description: The ID of the problem to test
          in: body
          type: string
          required: true
        - name: id_user
          description: The ID of the user submitting the request
          in: body
          type: string
          required: true
        - name: code_encoded
          description: The APL code to test, encoded as a base64 string
          in: body
          type: string
          required: true
    definitions:
        Evaluation:
            type: object
            properties:
                message:
                    type: string
                    description: A message telling whether the code executed correctly or not
                feedback:
                    type: string
                    description: A description of which test(s) the user passed
    responses:
        200:
            description: A JSON object containing the status of the evaluation and feedback
            schema:
                $ref: '#/definitions/Evaluation'
            examples:
                passed_all: {"feedback": "Congratulations! All tests passed. ", "message": "Code successfully executed!"}
                passed_partial: {"feedback": "Passed basic tests, well done! For extra points, consider cases like 'weights' as left argument and 'table.csv' as right argument.", "message": "Code successfully executed!"}
                failed_prohibited: {"feedback": "Basic test failed. An error occured. ⌸ found in source, which is prohibited for this problem.", "message": "Code successfully executed!"}
    """  # pylint: disable=line-too-long

    id_problem = request.json.get("id_problem")
    id_user = request.json.get("id_user")
    code_encoded = request.json.get("code_encoded")

    if not all((id_problem, id_user, code_encoded)):
        abort(400)

    # Run demo grading

    code = base64.b64decode(code_encoded).decode("utf-8")
    with open("tests/grader/example.json", "r", encoding="utf-8") as f:
        demo_config = json.load(f)

    result, feedback = asyncio.run(grader.evaluate(code, demo_config))

    if result:
        database.insert_points(id_user, id_problem, 1)
        return {"message": "Code successfully executed!", "feedback": feedback}, 200

    database.insert_points(id_user, id_problem, 0)
    return {"message": "Tests failed!", "feedback": feedback}, 200
