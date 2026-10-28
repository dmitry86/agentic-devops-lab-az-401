import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

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
        with urlopen(self.base_url + "/", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"CloudOps Status Service", response.read())

    def test_health(self):
        with urlopen(self.base_url + "/health", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(
                json.load(response),
                {"status": "healthy"},
            )

    def test_unknown_page(self):
        with self.assertRaises(HTTPError) as result:
            urlopen(self.base_url + "/missing", timeout=5)
        self.assertEqual(result.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
