import os
import requests
from flask import Flask, jsonify

ROUTER_URL = os.getenv("ROUTER_URL", "http://router-hop:8080/route")
app = Flask(__name__)

@app.get("/auth")
def auth():
    try:
        r = requests.get(ROUTER_URL, timeout=1.5)
        return jsonify({
            "service": "auth-service",
            "status": "ok",
            "downstream_status": r.status_code,
            "downstream_body": r.json()
        }), 200
    except Exception as e:
        return jsonify({
            "service": "auth-service",
            "status": "fail",
            "error": str(e)
        }), 503

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

app.run(host="0.0.0.0", port=8080)
