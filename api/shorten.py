import json
import random
import string
import os
from http.server import BaseHTTPRequestHandler
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rmbkorfoktkmxkbydlvu.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtYmtvcmZva3RrbXhrYnlkbHZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4ODU3NjMsImV4cCI6MjA5NzQ2MTc2M30.CIXXNIfmxVfIwH2ZIDnkQ-mI3nxJ6JLfgW7T1WMR-QY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def gen_code(length=6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            url = body.get('url', '').strip()
            custom_code = body.get('custom_code', None)

            if not url:
                self._send(400, {"error": "URL daalna zaroori hai!"})
                return

            # Custom code check
            if custom_code:
                exists = supabase.table('links').select('code').eq('code', custom_code).execute()
                if exists.data:
                    self._send(400, {"error": "Ye custom code pehle se use ho raha hai!"})
                    return
                code = custom_code
            else:
                # Auto generate unique code
                for _ in range(5):
                    code = gen_code()
                    exists = supabase.table('links').select('code').eq('code', code).execute()
                    if not exists.data:
                        break

            # Save to Supabase
            supabase.table('links').insert({
                "code": code,
                "original_url": url,
                "clicks": 0
            }).execute()

            self._send(200, {"code": code})

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
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

