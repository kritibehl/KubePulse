from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/auth")
def auth():
    return jsonify({"service": "auth-service", "status": "ok"}), 200

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

app.run(host="0.0.0.0", port=8080)
