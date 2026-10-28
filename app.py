from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class StatusService(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status = 200
            content_type = "application/json"
            body = json.dumps({"status": "broken"}).encode()

        elif self.path == "/":
            status = 200
            content_type = "text/html; charset=utf-8"
            body = """
                <h1>CloudOps Status Service</h1>
                <p>Application: running</p>
                <p>Environment: training</p>
                <p><a href="/health">Check health endpoint</a></p>
            """.encode()

        else:
            status = 404
            content_type = "text/plain"
            body = b"Not found"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8080), StatusService)
    print("Open http://localhost:8080")
    server.serve_forever()
