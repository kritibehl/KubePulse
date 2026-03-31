import os
import time
import requests
from flask import Flask, jsonify

PRIMARY_URL = os.getenv("PRIMARY_URL", "http://datastore-primary:8080/data")
SECONDARY_URL = os.getenv("SECONDARY_URL", "http://datastore-secondary:8080/data")
FAILOVER_MODE = os.getenv("FAILOVER_MODE", "primary_first")

app = Flask(__name__)

def try_fetch(url: str, timeout: float = 1.0):
    start = time.time()
    r = requests.get(url, timeout=timeout)
    elapsed = time.time() - start
    return r, elapsed

@app.get("/route")
def route():
    attempts = []
    targets = [PRIMARY_URL, SECONDARY_URL] if FAILOVER_MODE == "primary_first" else [SECONDARY_URL, PRIMARY_URL]

    for target in targets:
        try:
            r, elapsed = try_fetch(target)
            return jsonify({
                "service": "router-hop",
                "selected_target": target,
                "elapsed_seconds": elapsed,
                "attempts": attempts + [{"target": target, "status": r.status_code}],
                "payload": r.json()
            }), 200
        except Exception as e:
            attempts.append({"target": target, "error": str(e)})

    return jsonify({
        "service": "router-hop",
        "status": "fail",
        "attempts": attempts
    }), 503

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

app.run(host="0.0.0.0", port=8080)
