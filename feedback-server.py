#!/usr/bin/env python3
"""Tiny local feedback server. Receives votes, saves to feedback.json, auto-commits."""
import json, os, http.server, subprocess, threading

FEEDBACK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feedback.json")
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def auto_commit():
    """Git commit+push feedback.json in background"""
    try:
        subprocess.run(["git", "add", "feedback.json"], cwd=REPO_DIR, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Update feedback"], cwd=REPO_DIR, capture_output=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, capture_output=True)
    except: pass

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        existing = {}
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE) as f:
                existing = json.load(f)
        page = body.get("page", "unknown")
        votes = body.get("votes", {})
        if page not in existing:
            existing[page] = {}
        existing[page].update(votes)
        # Remove entries where vote was toggled off
        existing[page] = {k: v for k, v in existing[page].items() if v}
        with open(FEEDBACK_FILE, "w") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        # Auto-commit in background
        threading.Thread(target=auto_commit, daemon=True).start()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, *a): pass

if __name__ == "__main__":
    s = http.server.HTTPServer(("127.0.0.1", 8765), Handler)
    print("Feedback server on :8765")
    s.serve_forever()
