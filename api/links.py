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
            result = supabase.table('links').select('*').order('created_at', desc=True).limit(50).execute()
            self._send(200, {"links": result.data})
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
