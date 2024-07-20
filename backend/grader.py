"""This file provides the grading logic for the APL MOOC backend.

The functions here are responsible for running APL code using dyalog.run,
as well as encoding submitted user code into the APL workspace
used by dyalog.run during testing.
"""

import json
import msgpack
from websockets import connect
from grader.grader_namespace import setup_framework


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


async def evaluate(code: str, options: dict) -> tuple[bool, dict]:
    """
    Evaluate an APL code submission

    Args:
        code (str): The APL code to run
        options (dict): A dictionary of options as described in grader/README.md

    Returns:
        bool:
            Whether the code run succeeded or not.
            A value of `True` indicates that no errors were encountered,
            and not that all tests have been passed.
        dict:
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
        return False, "Execution timed out (5s)"

    if response["status_value"] != 0:
        return False, response["stderr"]

    output = json.loads(response["stdout"])
    feedback = ["Basic test failed. ",
                "Passed basic tests, well done! For extra points, consider cases like ",
                "Congratulations! All tests passed. "]

    msg = feedback[output["status"]]
    if output["status"] < 2:
        if "error" in output:
            msg += "An error occured. " + output["report"]
        if "larg" in output:
            msg += output["larg"] + " as left argument and "
        if "rarg" in output:
            msg += output["rarg"] + " as right argument."

    return True, msg
