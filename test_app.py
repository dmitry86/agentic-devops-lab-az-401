import json
import os
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen
from unittest.mock import patch

from app import StatusService


class StatusServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), StatusService)
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_homepage(self):
        with patch.dict(os.environ, {}, clear=True):
            with urlopen(self.base_url + "/", timeout=5) as response:
                self.assertEqual(response.status, 200)
                page = response.read()

        self.assertIn(b"<title>CloudOps Status</title>", page)
        self.assertIn(b"<h1>CloudOps Status</h1>", page)
        self.assertIn(b"Learning lab", page)
        self.assertIn(b"development", page)
        self.assertIn(b'fetch("/ready"', page)
        self.assertIn(b'readiness.status === "not_ready"', page)
        self.assertIn(b"window.setInterval(updateReadiness, 30000)", page)

    def test_homepage_uses_app_version(self):
        with patch.dict(os.environ, {"APP_VERSION": "release-42"}):
            with urlopen(self.base_url + "/", timeout=5) as response:
                page = response.read()

        self.assertIn(b"release-42", page)

    def test_health(self):
        with urlopen(self.base_url + "/health", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(
                json.load(response),
                {"status": "healthy"},
            )

    def test_ready(self):
        with patch.dict(os.environ, {}, clear=True):
            with urlopen(self.base_url + "/ready", timeout=5) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(
                    json.load(response),
                    {"status": "ready"},
                )

    def test_not_ready_during_maintenance(self):
        with patch.dict(os.environ, {"MAINTENANCE_MODE": "true"}):
            with self.assertRaises(HTTPError) as result:
                urlopen(self.base_url + "/ready", timeout=5)

            self.assertEqual(result.exception.code, 503)
            self.assertEqual(
                json.load(result.exception),
                {"status": "not_ready"},
            )

    def test_unknown_page(self):
        with self.assertRaises(HTTPError) as result:
            urlopen(self.base_url + "/missing", timeout=5)
        self.assertEqual(result.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
