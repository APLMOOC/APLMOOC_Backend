"""This file contains the tests for the basic functionality of the APL MOOC backend.

Basic functionality includes everything that does not have code evaluation
or complex database functionality.
"""

import unittest
import json
from backend import create_app

class TestBasics(unittest.TestCase):
    """Test class for the basic backend functionalities."""

    def setUp(self):
        self.app = create_app(True)
        self.client = self.app.test_client()

    def test_index(self):
        """
        Test that the index endpoint responds with a 200 OK response.
        """

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_error_400(self):
        """
        Test that malformed expressions return an HTTP 400 response with JSON data.
        """

        response = self.client.post("/submit", json={"test": "test"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.is_json, True)

    def test_error_404(self):
        """
        Test that unknown paths return an HTTP 404 response with JSON data.
        """

        response = self.client.get("/aybabtu")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.is_json, True)

    def test_error_405(self):
        """
        Test that invalid methods return an HTTP 405 response with JSON data.
        """

        response = self.client.get("/submit")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.is_json, True)

    def test_error_415(self):
        """
        Test that sending a request with an incorrect MIME type
        returns an HTTP 415 response with JSON data.
        """

        response = self.client.post("/submit", data=json.dumps({
            "id_user": 1,
            "id_problem": 1,
            "code_encoded": "4o20Cg=="
        }))
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.is_json, True)
