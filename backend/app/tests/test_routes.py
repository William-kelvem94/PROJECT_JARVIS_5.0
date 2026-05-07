import os
import unittest
from fastapi.testclient import TestClient

from app.main import app

class RoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json().get("status"), {"online", "ok"})

    def test_chat_endpoint_fallback(self):
        response = self.client.post("/chat", json={"message": "Teste rápido", "user_name": "Chefe"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.json())
        self.assertIsInstance(response.json()["reply"], str)

    def test_memory_endpoint(self):
        response = self.client.get("/memory")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json().get("memories"), list)

if __name__ == "__main__":
    unittest.main()
