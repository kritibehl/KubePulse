import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)

try:
    sock.connect((host, port))
    print({"probe": "tcp", "host": host, "port": port, "reachable": True})
    raise SystemExit(0)
except Exception as exc:
    print({"probe": "tcp", "host": host, "port": port, "reachable": False, "error": str(exc)})
    raise SystemExit(1)
finally:
    sock.close()
