import sys
import urllib.request

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/health"

try:
    with urllib.request.urlopen(url, timeout=3) as response:
        print({
            "probe": "http",
            "url": url,
            "status": response.status,
            "healthy": 200 <= response.status < 300
        })
        raise SystemExit(0 if 200 <= response.status < 300 else 1)
except Exception as exc:
    print({"probe": "http", "url": url, "healthy": False, "error": str(exc)})
    raise SystemExit(1)
