#!/usr/bin/env python3
"""Comedy Lab Feedback Server v2 - saves votes + comments to feedback.json"""
import json, os, time
from http.server import HTTPServer, BaseHTTPRequestHandler

FEEDBACK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback.json')

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE) as f:
            return json.load(f)
    return {}

def save_feedback(data):
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        data = load_feedback()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode())

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        page = body.get('page', 'unknown')
        votes = body.get('feedback', body.get('votes', {}))
        
        all_data = load_feedback()
        if page not in all_data:
            all_data[page] = {}
        
        for jid, info in votes.items():
            all_data[page][jid] = {
                'vote': info.get('vote'),
                'text': info.get('text', ''),
                'comment': info.get('comment', ''),
                'time': info.get('time', int(time.time() * 1000))
            }
        
        save_feedback(all_data)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, format, *args): pass

if __name__ == '__main__':
    import socketserver
    socketserver.TCPServer.allow_reuse_address = True
    server = HTTPServer(('127.0.0.1', 8765), Handler)
    server.allow_reuse_address = True
    print('Feedback server v2 running on http://127.0.0.1:8765')
    server.serve_forever()
