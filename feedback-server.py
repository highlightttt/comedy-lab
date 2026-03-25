#!/usr/bin/env python3
"""Comedy Lab Feedback Server v3 - saves votes + comments, readable by Bob"""
import json, os, time, socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_FILE = os.path.join(DIR, 'feedback.json')
FEEDBACK_LOG = os.path.join(DIR, 'feedback-log.md')  # Human/AI readable log

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE) as f:
            return json.load(f)
    return {}

def save_feedback(data):
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_log(entry):
    """Append a vote to the markdown log that Bob reads"""
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
        if os.path.getsize(FEEDBACK_LOG) == 0 if os.path.exists(FEEDBACK_LOG) else True:
            f.write("# Comedy Lab Feedback Log\n\nJesse's votes and comments on jokes. Bob reads this to improve.\n\n")
        f.write(line + "\n")

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
        if self.path == '/feedback-log':
            # Return the markdown log
            log = ''
            if os.path.exists(FEEDBACK_LOG):
                with open(FEEDBACK_LOG) as f:
                    log = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(log.encode())
        else:
            data = load_feedback()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode())

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        
        if self.path == '/vote':
            # Single vote with comment
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
        else:
            # Bulk sync
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
    server = HTTPServer(('127.0.0.1', 8765), Handler)
    server.allow_reuse_address = True
    print('Feedback server v3 on http://127.0.0.1:8765')
    server.serve_forever()
