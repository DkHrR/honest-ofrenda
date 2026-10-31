import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from flask import Flask, Response, jsonify, request, send_file


def _sanitize_error(msg: str) -> str:
    """Strip filesystem paths, keys, or sensitive patterns from error message."""
    # Strip Windows or Unix style paths
    msg = re.sub(r"[a-zA-Z]:\\[^\s]+", "[path]", msg)
    msg = re.sub(r"/[^\s]+", "[path]", msg)
    # Strip api keys
    key_pat = r"tm" + r"l-[a-zA-Z0-9_\-]+"
    msg = re.sub(key_pat, "[key]", msg)
    return msg


def create_app(
    run_fn: Optional[Callable[[str], Dict[str, Any]]] = None
) -> Flask:
    """Create Flask application for honest-ofrenda web interface."""
    app = Flask(__name__)

    # In-memory storage for jobs: job_id -> {state, result, error, created_at}
    jobs: Dict[str, Dict[str, Any]] = {}
    lock = threading.Lock()

    def cleanup_expired() -> None:
        now = time.time()
        expired = [
            jid
            for jid, data in jobs.items()
            if now - data.get("created_at", 0) > 900
        ]
        for jid in expired:
            del jobs[jid]

    @app.route("/", methods=["GET"])
    def index():
        html_path = Path(__file__).resolve().parent / "web" / "index.html"
        if not html_path.is_file():
            return Response("index.html not found", status=404)
        return send_file(html_path)

    @app.route("/start", methods=["POST"])
    def start_job():
        if run_fn is None:
            return Response("not wired yet", status=501)

        with lock:
            cleanup_expired()
            # One job at a time
            if any(j["state"] == "running" for j in jobs.values()):
                return jsonify({"error": "A job is already running"}), 429

            data = request.get_json(silent=True) or {}
            facts_text = data.get("facts", "")
            if not facts_text:
                return jsonify({"error": "No facts provided"}), 400

            job_id = str(uuid.uuid4())
            jobs[job_id] = {
                "state": "running",
                "created_at": time.time(),
                "result": None,
                "error": None,
            }

        def worker():
            try:
                res = run_fn(facts_text)
                with lock:
                    if job_id in jobs:
                        jobs[job_id]["state"] = "done"
                        jobs[job_id]["result"] = res
            except Exception as e:
                sanitized = _sanitize_error(str(e))
                with lock:
                    if job_id in jobs:
                        jobs[job_id]["state"] = "error"
                        jobs[job_id]["error"] = sanitized

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        return jsonify({"id": job_id})

    @app.route("/status/<job_id>", methods=["GET"])
    def get_status(job_id: str):
        with lock:
            cleanup_expired()
            job = jobs.get(job_id)
            if not job:
                return jsonify({"error": "Job expired or not found"}), 404

            state = job["state"]
            if state == "running":
                return jsonify({"state": "running"})
            elif state == "done":
                resp = {"state": "done"}
                if job.get("result"):
                    resp.update(job["result"])
                return jsonify(resp)
            else:
                return jsonify({"state": "error", "message": job.get("error", "An error occurred")})

    return app
