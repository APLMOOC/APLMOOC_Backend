"""This file contains the tests for the grader functionality of the APL MOOC backend.

Grader funtionality includes code submission and the awarding of points.
"""

import unittest
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
        self.assertEqual(response.json, {
            "feedback": "Passed basic tests, well done! For extra points, consider cases like 'weights' as left argument and 'table.csv' as right argument.",  # pylint: disable=line-too-long
            "message": "Code successfully executed!"
        })

    def test_ranking_full(self):
        """
        Test the fully correct submission, which passes all test cases.
        """

        response = helper.submit_code(self.client, "tests/grader/RankingFull.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "feedback": "Congratulations! All tests passed. ",
            "message": "Code successfully executed!"
        })

    def test_ranking_prohibited(self):
        """
        Test an incorrect submission, which fails due to having prohibited characters.
        """

        response = helper.submit_code(self.client, "tests/grader/RankingProh.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "feedback": "Basic test failed. An error occured. ⌸ found in source, which is prohibited for this problem.",  # pylint: disable=line-too-long
            "message": "Code successfully executed!"
        })
