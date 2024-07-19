import json
import asyncio
import msgpack
from websockets import connect
from test_framework.test_namespace import setup_framework


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
            "language" : "dyalog_apl",
            "code" : code,
            "timeout" : 5
        })
        await websocket.send(payload)

        response_raw = await websocket.recv()
        response = msgpack.unpackb(response_raw, raw=False, use_list=False)
        response.update({"stdout" : response["stdout"].decode(), "stderr" : response["stderr"].decode()})
        return response


async def run_tests(code: str, tests: dict) -> dict:
    """
    Run a set of tests on APL code

    Args:
        code (str): The APL code to run
        tests (dict): A dictionary of options as described in test_framework/README.md

    Returns:
        bool: Whether the code run succeeded or not. A value of `True` indicates that no errors were encountered, and not that all tests have been passed.
        dict: Information about the test run
    """

    # Wrap user code in text definition
    code_aplstring = code.replace("'", "''")
    tests_aplstring = json.dumps(tests).replace("'", "''")
    user_code = f"\nuser_code←0⎕JSON'{code_aplstring}'\n"
    test_opts = f"\nopts←0⎕JSON'{tests_aplstring}'\n"
    
    # Bundle test framework, user code and execution expression as a string
    test = setup_framework + user_code + test_opts + "⎕←1⎕JSON opts ⎕SE.Test.Run user_code"

    # Test the code using dyalog.run
    response = await run_apl(test)

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


# Tests
if __name__ == "__main__":
    with open("test_framework/example.json", encoding="utf-8") as f:
        eg_test = json.load(f)
    for test in ["Ranking.aplf", "RankingProh.aplf", "RankingFull.aplf"]:
        with open("test_framework/" + test, encoding="utf-8") as f:
            user_sub = f.read()
        print(asyncio.run(run_tests(user_sub, eg_test)))
