"""This file contains the tests for the database functionality of the APL MOOC backend.

These tests include calls to the code evaluation endpoint;
however, output from this endpoint is tested separately in the grader tests.
"""

import unittest
from backend import create_app
from . import helper

class TestDatabase(unittest.TestCase):
    """Test class for the database backend functionalities."""

    def setUp(self):
        self.app = create_app(True)
        self.client = self.app.test_client()

    def test_point_totals_awarded_correctly(self):
        """
        Test that point totals are correctly returned from the database.
        """

        helper.submit_repeated_correct(self.client, (
            ("1", "ch0_p0_example1"),
            ("1", "ch0_p0_example2"),
            ("1", "ch0_p0_example3"),
            ("2", "ch0_p0_example1"),
            ("2", "ch0_p0_example3"),
            ("3", "ch0_p0_example3"),
        ))

        response = self.client.get("/get")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)
        self.assertListEqual(response.json.get("points"), [
            {"id_user": "1", "points": 6},
            {"id_user": "2", "points": 4},
            {"id_user": "3", "points": 2},
        ])

    def test_repeated_points_awarded_correctly(self):
        """Test that repeatedly adding points only awards them once."""

        helper.submit_repeated_correct(self.client, (
            ("1", "ch0_p0_example1"),
            ("1", "ch0_p0_example1"),
            ("1", "ch0_p0_example1"),
            ("1", "ch0_p0_example1"),
            ("1", "ch0_p0_example2"),
            ("2", "ch0_p0_example1"),
            ("2", "ch0_p0_example3"),
            ("3", "ch0_p0_example3"),
        ))

        response = self.client.get("/get")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)
        self.assertListEqual(response.json.get("points"), [
            {"id_user": "1", "points": 4},
            {"id_user": "2", "points": 4},
            {"id_user": "3", "points": 2},
        ])

    def test_increasing_points_works_correctly(self):
        """Test that students can increase their points correctly."""

        helper.submit_code(self.client, "tests/grader/RankingError.aplf")
        helper.submit_code(self.client, "tests/grader/RankingFull.aplf")
        helper.submit_code(self.client, "tests/grader/RankingError.aplf")

        response = self.client.get("/get")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)
        self.assertListEqual(response.json.get("points"), [
            {"id_user": "1", "points": 2},
        ])
