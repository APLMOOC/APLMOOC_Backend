"""This file contains the tests for the grader functionality of the APL MOOC backend.

Grader funtionality includes code submission and the awarding of points.
"""

import unittest
import base64
from backend import create_app

class TestGrader(unittest.TestCase):
    """Test class for the grader endpoints."""

    def setUp(self):
        self.app = create_app(True)
        self.client = self.app.test_client()

    def submit_code(self, path: str):
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
        
        response = self.client.post("/submit", json={
            "id_user": 1,
            "id_problem": 1,
            "code_encoded": base64.b64encode(code.encode()).decode("utf-8"),
        })

        return response

    def test_ranking_partial(self):
        """
        Test the partially correct submission, which passes basic test cases but not edge cases.
        """

        response = self.submit_code("tests/grader/Ranking.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "feedback": "Passed basic tests, well done! For extra points, consider cases like 'weights' as left argument and 'table.csv' as right argument.",  # pylint: disable=line-too-long
            "message": "Code successfully executed!"
        })

    def test_ranking_full(self):
        """
        Test the fully correct submission, which passes all test cases.
        """

        response = self.submit_code("tests/grader/RankingFull.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "feedback": "Congratulations! All tests passed. ",
            "message": "Code successfully executed!"
        })

    def test_ranking_prohibited(self):
        """
        Test an incorrect submission, which fails due to having prohibited characters.
        """

        response = self.submit_code("tests/grader/RankingProh.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "feedback": "Basic test failed. An error occured. ⌸ found in source, which is prohibited for this problem.",  # pylint: disable=line-too-long
            "message": "Code successfully executed!"
        })
