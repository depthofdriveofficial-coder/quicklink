from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
from urllib.parse import urlparse, parse_qs

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

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            code = params.get('code', [None])[0]

            if not code:
                return self._send(400, {"error": "Code nahi diya!"})

            result = supabase_request("GET", f"links?code=eq.{code}&select=*")

            if not result:
                return self._send(404, {"error": "Ye link nahi mila!"})

            link = result[0]
            supabase_request("PATCH", f"links?code=eq.{code}", {"clicks": link['clicks'] + 1})
            self._send(200, {"url": link['original_url']})

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
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
