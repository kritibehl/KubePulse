import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(
                500,
                {
                    "status": "unhealthy",
                    "http_health": 500,
                    "reason": "intentional_bad_release"
                },
            )
            return

        if self.path == "/dependency":
            self.send_json(
                503,
                {
                    "dependency": "postgresql",
                    "dependency_ready": False,
                    "reason": "intentional_bad_release"
                },
            )
            return

        self.send_json(404, {"error": "not_found"})

print("KubePulse BAD candidate API listening on :8080", flush=True)
HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
