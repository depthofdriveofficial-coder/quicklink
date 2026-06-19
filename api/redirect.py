import json
import os
from http.server import BaseHTTPRequestHandler
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rmbkorfoktkmxkbydlvu.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtYmtvcmZva3RrbXhrYnlkbHZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4ODU3NjMsImV4cCI6MjA5NzQ2MTc2M30.CIXXNIfmxVfIwH2ZIDnkQ-mI3nxJ6JLfgW7T1WMR-QY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Path: /api/redirect?code=abc123
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            code = params.get('code', [None])[0]

            if not code:
                self._send(400, {"error": "Code nahi diya!"})
                return

            result = supabase.table('links').select('*').eq('code', code).execute()

            if not result.data:
                self._send(404, {"error": "Ye link nahi mila! Shayad delete ho gaya."})
                return

            link = result.data[0]

            # Clicks update karo
            supabase.table('links').update({"clicks": link['clicks'] + 1}).eq('code', code).execute()

            self._send(200, {"url": link['original_url']})

        except Exception as e:
            self._send(500, {"error": str(e)})

    def _send(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
