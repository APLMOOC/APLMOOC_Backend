import json
import asyncio
import msgpack
from websockets import connect
from enum import Enum, auto
from test_framework.test_namespace import setup_framework

async def run_apl(code: str) -> str:
    """
    Safely runs arbitrary APL code using the dyalog.run service
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

    Arguments:
    code - the APL code to run
    tests - dict of options as described in test_framework/README.md

    Outputs:
    A dict containing information about the test run
    """
    # Wrap user code in text definition
    APLString = lambda s: json.dumps("''".join(s.split("'")))
    user_code = f"\nuser_code←0⎕JSON' + APLString(code) + "'\n"
    test_opts = "\nopts←0⎕JSON'" + "''".join(json.dumps(tests).split("'")) + "'\n"
    
    # Bundle test framework, user code and execution expression as a string
    test = setup_framework + user_code + test_opts + "⎕←1⎕JSON opts ⎕SE.Test.Run user_code"
    # Response → dict
    base = await run_apl(test)
    #print(base)
    if base["timed_out"]:
        return False, "Execution timed out (5s)"
    if base["status_value"] != 0:
        print(base["stderr"])
        return False, base["stderr"]

    #print("\n\n"+base["stdout"])
    #print("\n\n"+base["stderr"])
    output = json.loads(base["stdout"])
    feedback = ["Basic test failed. ",
                "Passed basic tests, well done. For extra points, consider cases like ",
                "Congratulations! All tests passed. "]
    msg = feedback[output["status"]]
    if output["status"] < 2:
        if "error" in output:
            msg += "An error occured. " + output["report"]
        if "larg" in output:
            msg += output["larg"] + " as left argument and "
        if "rarg" in output:
            msg += output["rarg"] + " as right argument."
    return True, msg + "\n"

# Tests
if __name__ == "__main__":
    with open("test_framework/example.json", encoding="utf-8") as f:
        eg_test = json.load(f)
    for test in ["Ranking.aplf", "RankingProh.aplf", "RankingFull.aplf"]:
        with open("test_framework/" + test, encoding="utf-8") as f:
            user_sub = f.read()
        print(asyncio.run(run_tests(user_sub, eg_test)))
