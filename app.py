from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import random
import string
import os
import urllib.request
import json

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rmbkorfoktkmxkbydlvu.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtYmtvcmZva3RrbXhrYnlkbHZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4ODU3NjMsImV4cCI6MjA5NzQ2MTc2M30.CIXXNIfmxVfIwH2ZIDnkQ-mI3nxJ6JLfgW7T1WMR-QY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def supabase_req(method, path, data=None):
    url = SUPABASE_URL + "/rest/v1/" + path
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": "Bearer " + SUPABASE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise HTTPException(status_code=e.code, detail=error_body)

def gen_code(length=6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

@app.get("/", response_class=HTMLResponse)
def home():
    path = os.path.join(BASE_DIR, "index.html")
    with open(path, "r") as f:
        return f.read()

@app.get("/s/{code}", response_class=HTMLResponse)
def short_redirect(code: str):
    # Direct redirect without file reading
    result = supabase_req("GET", f"links?code=eq.{code}&select=*")
    if not result:
        return HTMLResponse("<h2>Link nahi mila!</h2><a href='/'>Home</a>", status_code=404)
    link = result[0]
    supabase_req("PATCH", f"links?code=eq.{code}", {"clicks": link['clicks'] + 1})
    original_url = link['original_url']
    return HTMLResponse(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<title>Redirecting...</title>
<style>
body{{background:#0a0a0f;color:#e2e2f0;font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;}}
.box{{background:#16161f;border:1px solid #1e1e2e;border-radius:16px;padding:40px 30px;max-width:400px;width:100%;}}
.spinner{{width:40px;height:40px;border:3px solid #1e1e2e;border-top-color:#a78bfa;border-radius:50%;animation:spin 0.7s linear infinite;margin:0 auto 20px;}}
@keyframes spin{{to{{transform:rotate(360deg);}}}}
p{{color:#6b6b8a;font-size:0.9rem;word-break:break-all;}}
</style>
<meta http-equiv="refresh" content="1;url={original_url}"/>
</head>
<body>
<div class="box">
<div class="spinner"></div>
<h2>Redirect ho rahe hain...</h2>
<p>{original_url}</p>
</div>
<script>setTimeout(function(){{window.location.href="{original_url}";}},800);</script>
</body>
</html>""")

@app.post("/api/shorten")
async def shorten(request: Request):
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON parse error!")

    url = body.get("url", "").strip()
    custom_code = body.get("custom_code") or None

    if not url:
        raise HTTPException(status_code=400, detail="URL daalna zaroori hai!")
    if not url.startswith("http"):
        url = "https://" + url

    if custom_code:
        existing = supabase_req("GET", f"links?code=eq.{custom_code}&select=code")
        if existing:
            raise HTTPException(status_code=400, detail="Ye custom code pehle se use ho raha hai!")
        code = custom_code
    else:
        for _ in range(5):
            code = gen_code()
            existing = supabase_req("GET", f"links?code=eq.{code}&select=code")
            if not existing:
                break

    supabase_req("POST", "links", {"code": code, "original_url": url, "clicks": 0})
    return {"code": code}

@app.get("/api/links")
def get_links():
    result = supabase_req("GET", "links?select=*&order=created_at.desc&limit=50")
    return {"links": result}

@app.get("/api/redirect")
def api_redirect(code: str):
    result = supabase_req("GET", f"links?code=eq.{code}&select=*")
    if not result:
        raise HTTPException(status_code=404, detail="Link nahi mila!")
    link = result[0]
    supabase_req("PATCH", f"links?code=eq.{code}", {"clicks": link['clicks'] + 1})
    return {"url": link['original_url']}
