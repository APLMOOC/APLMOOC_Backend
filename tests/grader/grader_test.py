"""This file contains the tests for the grader functionality of the APL MOOC backend.

Grader funtionality includes code submission and the awarding of points.
"""

import unittest
import base64
from backend import create_app
from . import helper

class TestGrader(unittest.TestCase):
    """Test class for the grader endpoints."""

    def setUp(self):
        self.app = create_app(True)
        self.client = self.app.test_client()

    def test_ranking_partial(self):
        """
        Test the partially correct submission, which passes basic test cases but not edge cases.
        """

        response = helper.submit_code(self.client, "tests/grader/Ranking.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json, {
            "points": 1,
            "feedback": "Passed basic tests, well done! Failed test: 'weights' as left argument and 'table.csv' as right argument.",  # pylint: disable=line-too-long
        })

    def test_ranking_full(self):
        """
        Test the fully correct submission, which passes all test cases.
        """

        response = helper.submit_code(self.client, "tests/grader/RankingFull.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json, {
            "points": 2,
            "feedback": "All tests passed!",
        })

    def test_ranking_prohibited(self):
        """
        Test an incorrect submission, which fails due to having prohibited characters.
        """

        response = helper.submit_code(self.client, "tests/grader/RankingProh.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json, {
            "points": 0,
            "feedback": "⌸ found in source, which is prohibited for this problem.",
        })

    def test_ranking_timeout(self):
        """
        Test an incorrect submission, which fails due to timing out (infinite loop).
        """

        response = helper.submit_code(self.client, "tests/grader/RankingTimeout.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json, {
            "points": 0,
            "feedback": "Execution timed out (>5s)",
        })

    def test_ranking_error(self):
        """
        Test an incorrect submission, which fails due to a value error.
        """

        response = helper.submit_code(self.client, "tests/grader/RankingError.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["points"], 0)
        self.assertIn("VALUE ERROR", response.json["feedback"])

    def test_problem_does_not_exist(self):
        """
        Test a submission where the problem does not exist and a HTTP 400 response is returned.
        """

        response = helper.submit_code(
            self.client,
            "tests/grader/RankingFull.aplf",
            id_problem="INVALID_PROBLEM",
        )
        self.assertEqual(response.status_code, 400)

    def test_p1(self):
        """
        Test the fully correct submission, which passes all test cases.
        """

        code = "A←{13.7×206.55}"
        response = self.client.post("/submit", json={
            "id_user": "1",
            "id_problem": "ch1_p1",
            "code_encoded": base64.b64encode(code.encode()).decode("utf-8"),
        })
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json, {
            "points": 2,
            "feedback": "All tests passed!",
        })
