from http.server import BaseHTTPRequestHandler
import json
import random
import string
import os
import urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rmbkorfoktkmxkbydlvu.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtYmtvcmZva3RrbXhrYnlkbHZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4ODU3NjMsImV4cCI6MjA5NzQ2MTc2M30.CIXXNIfmxVfIwH2ZIDnkQ-mI3nxJ6JLfgW7T1WMR-QY")

def supabase_request(method, path, data=None):
    url = SUPABASE_URL + "/rest/v1/" + path
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": "Bearer " + SUPABASE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

def gen_code(length=6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            url = body.get('url', '').strip()
            custom_code = body.get('custom_code') or None

            if not url:
                return self._send(400, {"error": "URL daalna zaroori hai!"})

            if not url.startswith('http'):
                url = 'https://' + url

            if custom_code:
                existing = supabase_request("GET", f"links?code=eq.{custom_code}&select=code")
                if existing:
                    return self._send(400, {"error": "Ye custom code pehle se use ho raha hai!"})
                code = custom_code
            else:
                for _ in range(5):
                    code = gen_code()
                    existing = supabase_request("GET", f"links?code=eq.{code}&select=code")
                    if not existing:
                        break

            supabase_request("POST", "links", {"code": code, "original_url": url, "clicks": 0})
            self._send(200, {"code": code})

        except Exception as e:
            self._send(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _send(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
