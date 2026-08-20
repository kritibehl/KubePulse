import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))


def postgres_reachable() -> tuple[bool, str]:
    try:
        with socket.create_connection(
            (POSTGRES_HOST, POSTGRES_PORT),
            timeout=1.5,
        ):
            return True, "postgresql dependency reachable"
    except OSError as exc:
        return False, str(exc)


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "status": "healthy",
                    "http_health": 200,
                    "note": "Application process is alive",
                },
            )
            return

        if self.path == "/dependency":
            reachable, evidence = postgres_reachable()

            self.send_json(
                200 if reachable else 503,
                {
                    "dependency": "postgresql",
                    "dependency_ready": reachable,
                    "evidence": evidence,
                },
            )
            return

        self.send_json(404, {"error": "not found"})

    def log_message(self, format: str, *args) -> None:
        print(
            f'{self.client_address[0]} - {format % args}',
            flush=True,
        )


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("KubePulse demo API listening on :8080", flush=True)
    server.serve_forever()
