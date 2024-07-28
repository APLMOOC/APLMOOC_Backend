"""This file provides the grading logic for the APL MOOC backend.

The functions here are responsible for running APL code using dyalog.run,
as well as encoding submitted user code into the APL workspace
used by dyalog.run during testing.
"""

import json
from enum import Enum
import msgpack
import requests
from websockets import connect
from grader.grader_namespace import setup_framework

MOOC_API = "https://www.mooc.fi/api/v8"


class GradingStatus(Enum):
    """An enum for the outcome of grading operations."""
    FAILED = 0
    PASSED_BASIC = 1
    PASSED_ALL = 2
    ERROR = 3


async def run_apl(code: str) -> dict:
    """
    Safely runs arbitrary APL code using the dyalog.run service.

    Args:
        code (str): The APL code to run
    
    Returns:
        dict: The parsed response from the dyalog.run service
    """

    async with connect("wss://dyalog.run/api/v0/ws/execute") as websocket:
        payload = msgpack.packb({
            "language": "dyalog_apl",
            "code": code,
            "timeout": 5,
        })
        await websocket.send(payload)

        response_raw = await websocket.recv()
        response = msgpack.unpackb(response_raw, raw=False, use_list=False)
        response.update({
            "stdout": response["stdout"].decode(),
            "stderr": response["stderr"].decode(),
        })
        return response


async def evaluate(code: str, options: dict) -> tuple[GradingStatus, str]:
    """
    Evaluate an APL code submission

    Args:
        code (str): The APL code to run
        options (dict): A dictionary of options as described in grader/README.md

    Returns:
        GradingStatus:
            A value describing whether tests passed fully, passed partially,
            failed, or errors were encountered.
        str:
            Information about the evaluation
    """

    # Wrap user code in text definition
    code_aplstring = json.dumps(code.replace("'", "''"))
    options_aplstring = json.dumps(options).replace("'", "''")
    code_aplcode = f"\nuser_code←0⎕JSON'{code_aplstring}'\n"
    options_aplcode = f"\nopts←0⎕JSON'{options_aplstring}'\n"

    # Bundle grader framework, user code and execution options as a string
    epilogue = "⎕←1⎕JSON opts ⎕SE.Test.Run user_code"
    submission = f"{setup_framework}{code_aplcode}{options_aplcode}{epilogue}"

    # Evaluate the code using dyalog.run
    response = await run_apl(submission)

    # Parse the response data
    if response["timed_out"]:
        return GradingStatus.ERROR, "Execution timed out (>5s)"

    if response["status_value"] != 0:  # pragma: no cover
        return GradingStatus.ERROR, response["stderr"]

    output = json.loads(response["stdout"])

    if "error" in output:
        return GradingStatus.ERROR, output["report"]

    if output["status"] == 2:
        return GradingStatus.PASSED_ALL, ""

    return (
        GradingStatus(output["status"]),
        "Failed test: " +
        (f"{output['larg']} as left argument and " if "larg" in output else "") +
        (f"{output['rarg']} as right argument." if "rarg" in output else "")
    )


def get_user_details(mooc_token: str) -> dict | None:
    """
    Get details for a user based on their mooc.fi token.

    Args:
        mooc_token (str): The user's mooc.fi token
    
    Returns:
        dict:
            All of the user's information retrieved from mooc.fi,
            or None if the user does not exist
    """

    body = {
        "operationName": "UserInfo",
        "variables": {"search": None},
        "query": \
"""
query UserInfo($search: String) {
  currentUser(search: $search) {
    id
    full_name
    email
    student_number
    username
  }
}
"""
    }

    response = requests.post(MOOC_API, json=body, timeout=5, headers={
        "Authorization": f"Bearer {mooc_token}",
    })

    if response.status_code != 200:
        return None

    return response.json()["data"]["currentUser"]


def get_user_id(mooc_token: str) -> str | None:
    """
    Get a user's ID based on their mooc.fi token.

    Args:
        mooc_token (str): The user's mooc.fi token
    
    Returns:
        str:
            The user's mooc.fi user ID,
            or None if the user does not exist
    """

    user_details = get_user_details(mooc_token)

    if not user_details:
        return None

    return user_details.get("id")
