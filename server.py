#!/usr/bin/env python3
import os, time, uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

DIR = os.path.expanduser("~/pasted_images")
os.makedirs(DIR, exist_ok=True)
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def idx():
    return '''<body style="font:1em sans-serif;text-align:center;padding:50px">
    <h2>Paste Image Here (Ctrl+V)</h2><div id="l"></div>
    <script>
    document.onpaste = async e => {
      let f = [...e.clipboardData.items].find(i => i.type.startsWith('image/'))?.getAsFile();
      if (!f) return;
      let res = await fetch('/save', {method: 'POST', body: f});
      let j = await res.json();
      document.getElementById('l').innerHTML = `✅ ${j.path}<br>` + document.getElementById('l').innerHTML;
    }
    </script>'''

@app.post("/save")
async def save(req: Request):
    path = os.path.join(DIR, f"{int(time.time()*1000)}.png")
    with open(path, 'wb') as f:
        f.write(await req.body())
    return {"path": path}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8153)
