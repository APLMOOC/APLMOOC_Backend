"""Helper functions for the grader and database tests."""

import base64


def submit_code(client, path: str, id_user: str = "1", id_problem: str = "ch0_p0_example1"):
    """
    Helper function used to submit a piece of APL code to the grader
    and return the response.

    Args:
        path (str): A path to the APL code file to read
    
    Returns:
        A response object from the test client
    """

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    response = client.post("/submit", json={
        "id_user": id_user,
        "id_problem": id_problem,
        "code_encoded": base64.b64encode(code.encode()).decode("utf-8"),
    })

    return response


def submit_repeated_correct(client, user_problems: tuple):
    """
    Helper function used to repeatedly submit correct code
    to the grader with different user and problem IDs.

    Args:
        path (str): A path to the APL code file to read
    
    Returns:
        A response object from the test client
    """

    for id_user, id_problem in user_problems:
        submit_code(client, "tests/grader/RankingFull.aplf", id_user, id_problem)
