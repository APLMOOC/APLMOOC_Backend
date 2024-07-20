import unittest
import base64

from backend import create_app

class TestGrader(unittest.TestCase):
    def setUp(self):
        self.app = create_app(True)
        self.client = self.app.test_client()

    def submit_code(self, path):
        with open(path) as f:
            code = f.read()
        
        response = self.client.post("/submit", json={
            "id_user": 1,
            "id_problem": 1,
            "code_encoded": base64.b64encode(code.encode()).decode("utf-8"),
        })

        return response

    def test_ranking_normal(self):
        response = self.submit_code("tests/grader/Ranking.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "feedback": "Passed basic tests, well done! For extra points, consider cases like 'weights' as left argument and 'table.csv' as right argument.",
            "message": "Code successfully executed!"
        })

    def test_ranking_full(self):
        response = self.submit_code("tests/grader/RankingFull.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "feedback": "Congratulations! All tests passed. ",
            "message": "Code successfully executed!"
        })

    def test_ranking_prohibited(self):
        response = self.submit_code("tests/grader/RankingProh.aplf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "feedback": "Basic test failed. An error occured. ⌸ found in source, which is prohibited for this problem.",
            "message": "Code successfully executed!"
        })
        
