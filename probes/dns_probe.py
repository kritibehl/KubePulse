import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"

try:
    result = socket.gethostbyname(host)
    print({"probe": "dns", "host": host, "resolved": True, "address": result})
    raise SystemExit(0)
except Exception as exc:
    print({"probe": "dns", "host": host, "resolved": False, "error": str(exc)})
    raise SystemExit(1)
