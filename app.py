"""
SarkariJob MH — Flask Backend API
/api/jobs  → job list return karta hai
Auto scrape every 6 hours
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import json, os, threading
from scraper import scrape_jobs, save_to_json

app = Flask(__name__)
CORS(app)  # Frontend ko allow karta hai

JOBS_FILE = "jobs.json"
_lock = threading.Lock()


# ── Helpers ──────────────────────────────────────────────
def load_jobs() -> list[dict]:
    if not os.path.exists(JOBS_FILE):
        return []
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def refresh_jobs():
    print("[API] Refreshing jobs from scraper...")
    jobs = scrape_jobs(max_pages=3)
    with _lock:
        save_to_json(jobs, JOBS_FILE)
    print("[API] Refresh complete.")


# ── Routes ───────────────────────────────────────────────
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/api/jobs")
def get_jobs():
    category = request.args.get("category", "all")
    search   = request.args.get("q", "").lower()
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    with _lock:
        jobs = load_jobs()

    # Filter by category
    if category != "all":
        jobs = [j for j in jobs if j.get("category") == category]

    # Search filter
    if search:
        jobs = [j for j in jobs if search in j["title"].lower() or search in j.get("desc", "").lower()]

    # Pagination
    total   = len(jobs)
    start   = (page - 1) * per_page
    end     = start + per_page
    paged   = jobs[start:end]

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "jobs": paged,
    })


@app.route("/api/refresh", methods=["GET", "POST"])
def manual_refresh():
    """Manual refresh trigger (admin use)"""
    threading.Thread(target=refresh_jobs, daemon=True).start()
    return jsonify({"status": "refresh started"})


# ── Scheduler (auto refresh every 6 hours) ───────────────
scheduler = BackgroundScheduler()
scheduler.add_job(refresh_jobs, "interval", hours=6, id="auto_refresh")
scheduler.start()


# ── Start ─────────────────────────────────────────────────
if __name__ == "__main__":
    # First run pe scrape karo agar file nahi hai
    if not os.path.exists(JOBS_FILE):
        refresh_jobs()
    app.run(host="0.0.0.0", port=5000, debug=False)
