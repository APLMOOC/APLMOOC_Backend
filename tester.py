import asyncio
import msgpack
from websockets import connect

async def run_apl(code: str) -> str:
    """
    Safely runs arbitrary APL code using the dyalog.run service
    """
    async with connect("wss://dyalog.run/api/v0/ws/execute") as websocket:
        payload = msgpack.packb({
            "language" : "dyalog_apl",
            "code" : code,
            "timeout" : 15
        })
        await websocket.send(payload)

        response_raw = await websocket.recv()
        response = msgpack.unpackb(response_raw, raw=False, use_list=False)
        return response["stdout"].decode()


async def run_tests(code: str, tests: list) -> bool:
    """
    Run a set of tests on APL code

    Arguments:
    code - the APL code to run
    tests - a list of tuples. The first and second element of the tuple
    are the left and right arguments of the function, while the third is
    the expected output.
    """
    for test in tests:
        assert(len(test)==3)
        actual = await run_apl("⎕←" + test[0] + code + test[1])
        expected = test[2]
        if not actual == expected:
            return f"Error! Expected value\n{expected}\ngot\n{actual}"
    
    return "All tests passed!"
        

# Tests
if __name__ == "__main__":
    #print(asyncio.run(run_apl("⎕←3 3⍴9?9")))
    asyncio.run(run_tests("⍴", [("2 2","⍳4","1 2\n3 4\n"),
                                ("⍴ 0","0","0\n"),
                                ("3 3","1","1 1 1\n1 1 1\n1 1 1\n")
                                ]))
