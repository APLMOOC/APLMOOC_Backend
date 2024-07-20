import unittest
from backend import create_app

class TestGrader(unittest.TestCase):
    def setUp(self):
        self.app = create_app(True)
        self.client = self.app.test_client()

    def test_ranking_normal(self):
        pass
