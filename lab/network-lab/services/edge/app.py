import os
import requests
from flask import Flask, jsonify

API_URL = os.getenv("API_URL", "http://api-service:8080/api")
app = Flask(__name__)

@app.get("/")
def root():
    try:
        r = requests.get(API_URL, timeout=2.0)
        return jsonify({
            "service": "edge",
            "upstream_status": r.status_code,
            "upstream_body": r.json()
        }), r.status_code
    except Exception as e:
        return jsonify({
            "service": "edge",
            "error": str(e)
        }), 503

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

app.run(host="0.0.0.0", port=8080)
