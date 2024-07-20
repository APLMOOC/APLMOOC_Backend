import unittest
from backend import create_app

class TestBasics(unittest.TestCase):
    def setUp(self):
        self.app = create_app(True)
        self.client = self.app.test_client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
