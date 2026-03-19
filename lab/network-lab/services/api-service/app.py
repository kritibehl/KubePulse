import os
import requests
from flask import Flask, jsonify

AUTH_URL = os.getenv("AUTH_URL", "http://auth-service:8080/auth")
app = Flask(__name__)

@app.get("/api")
def api():
    try:
        r = requests.get(AUTH_URL, timeout=1.5)
        return jsonify({
            "service": "api-service",
            "auth_status": r.status_code,
            "auth_body": r.json()
        }), 200
    except Exception as e:
        return jsonify({
            "service": "api-service",
            "error": str(e)
        }), 503

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

app.run(host="0.0.0.0", port=8080)
