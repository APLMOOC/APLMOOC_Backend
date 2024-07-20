"""This file contains the tests for the basic functionality of the APL MOOC backend.

Basic functionality includes everything that does not have code evaluation
or complex database functionality.
"""

import unittest
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
