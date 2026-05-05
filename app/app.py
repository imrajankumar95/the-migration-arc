from flask import Flask, jsonify
import platform
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "service": "migration-arc-app",
        "status": "running",
        "message": "Multi-cloud deployment pipeline — The Migration Arc"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route("/info")
def info():
    return jsonify({
        "hostname": platform.node(),
        "os": platform.system(),
        "python_version": platform.python_version(),
        "app_version": "1.0.0"
    })

@app.route("/metrics/custom")
def custom_metrics():
    return jsonify({
        "requests_total": 1,
        "uptime_seconds": 0,
        "environment": "production"
    })

@app.route("/ping")
def ping():
    return jsonify({"pong": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
