#!/usr/bin/env python3
"""Comedy Lab Server v5 - serves pages + collects feedback + updates taste profile"""
import json, os, time, socketserver, mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path

DIR = Path(__file__).parent.resolve()
FEEDBACK_FILE = DIR / 'feedback.json'
FEEDBACK_LOG = DIR / 'feedback-log.md'
TASTE_PROFILE = DIR / 'taste-profile.md'

def load_feedback():
    if FEEDBACK_FILE.exists():
        return json.loads(FEEDBACK_FILE.read_text())
    return {}

def save_feedback(data):
    FEEDBACK_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def append_log(entry):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    vote_emoji = '👍' if entry.get('vote') == 'up' else '👎'
    page = entry.get('page', '?')
    jid = entry.get('jid', '?')
    text = entry.get('text', '')[:150]
    comment = entry.get('comment', '')
    
    line = f"\n- [{ts}] {vote_emoji} **{jid}** ({page}): {text}"
    if comment:
        line += f"\n  - 💬 Jesse: {comment}"
    
    with open(FEEDBACK_LOG, 'a') as f:
        if not FEEDBACK_LOG.exists() or FEEDBACK_LOG.stat().st_size == 0:
            f.write("# Comedy Lab Feedback Log\n\nJesse's votes and comments on jokes. Bob reads this to improve.\n")
        f.write(line + "\n")

def update_taste_profile(entry):
    """Append vote to taste profile immediately"""
    vote_emoji = '👍' if entry.get('vote') == 'up' else '👎'
    text = entry.get('text', '')[:150]
    comment = entry.get('comment', '')
    section = "What Works" if entry.get('vote') == 'up' else "What Doesn't Work"
    
    if not TASTE_PROFILE.exists():
        TASTE_PROFILE.write_text("# Jesse's Comedy Taste Profile\n\n## What Works (from 👍 votes)\n\n## What Doesn't Work (from 👎 votes)\n\n## Emerging Patterns\n\n## Creative Rules\n")
    
    content = TASTE_PROFILE.read_text()
    ts = datetime.now().strftime('%m/%d')
    new_entry = f"- [{ts}] {vote_emoji} {text}"
    if comment:
        new_entry += f" — *\"{comment}\"*"
    new_entry += "\n"
    
    # Insert after the right section header
    marker = f"## {section}"
    if marker in content:
        parts = content.split(marker, 1)
        # Find the next ## or end
        rest = parts[1]
        # Insert right after the header line
        newline_pos = rest.index('\n') + 1
        rest = rest[:newline_pos] + new_entry + rest[newline_pos:]
        content = parts[0] + marker + rest
        TASTE_PROFILE.write_text(content)

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        # Serve static files from comedy directory
        path = self.path.split('?')[0].lstrip('/')
        if not path:
            path = 'index.html'
        
        filepath = DIR / path
        
        # Security: no directory traversal
        try:
            filepath.resolve().relative_to(DIR)
        except ValueError:
            self.send_response(403)
            self.end_headers()
            return
        
        if filepath.is_file():
            mime, _ = mimetypes.guess_type(str(filepath))
            if not mime:
                mime = 'application/octet-stream'
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self._cors()
            self.end_headers()
            self.wfile.write(filepath.read_bytes())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        
        if self.path == '/vote':
            page = body.get('page', 'unknown')
            jid = body.get('jid', 'unknown')
            
            all_data = load_feedback()
            if page not in all_data:
                all_data[page] = {}
            all_data[page][jid] = {
                'vote': body.get('vote'),
                'text': body.get('text', ''),
                'comment': body.get('comment', ''),
                'time': body.get('time', int(time.time() * 1000))
            }
            save_feedback(all_data)
            append_log(body)
            update_taste_profile(body)
        else:
            page = body.get('page', 'unknown')
            feedback = body.get('feedback', body.get('votes', {}))
            all_data = load_feedback()
            if page not in all_data:
                all_data[page] = {}
            for jid, info in feedback.items():
                all_data[page][jid] = info
            save_feedback(all_data)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, fmt, *args): pass

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    server = HTTPServer(('0.0.0.0', 8765), Handler)
    server.allow_reuse_address = True
    print('Comedy Lab server v5 on http://127.0.0.1:8765')
    server.serve_forever()
