"""Web server: serves the website and runs every simulation in Python.
Local:   python app.py    then open http://127.0.0.1:5000
Render:  gunicorn app:app (see README)
"""
import os
from flask import Flask, jsonify, request, send_from_directory
from simulator import run_from_payload

app = Flask(__name__, static_folder="static")


@app.after_request
def add_cors(resp):
    # lets the Vercel-hosted page call this API from another domain
    resp.headers["Access-Control-Allow-Origin"] = os.environ.get("ALLOWED_ORIGIN", "*")
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp

HERE = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return send_from_directory(os.path.join(HERE, "static"), "index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/simulate", methods=["POST", "OPTIONS"])
def simulate():
    if request.method == "OPTIONS":  # browser pre-flight check
        return ("", 204)
    try:
        return jsonify(run_from_payload(request.get_json(force=True)))
    except Exception as e:  # show the real error in the page instead of a silent failure
        return jsonify({"ok": False, "error": str(e),
                        "checks": [{"ok": False, "label": "Server error", "detail": str(e)}]}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Quantum Noise Simulator running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0" if "PORT" in os.environ else "127.0.0.1", port=port, debug=False)
