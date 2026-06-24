#!/usr/bin/env python3
"""Zero-dependency paste/drag/drop file dropbox. Stdlib only — runs on any
machine with Python 3 (Windows / macOS / Linux), nothing to pip install.

    python server.py            # then open http://localhost:8153

Env overrides: PASTE_DIR (default ~/pasted_images), PASTE_PORT (8153),
PASTE_HOST (0.0.0.0; set to 127.0.0.1 for localhost-only).
"""
import json, mimetypes, os, re, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

DIR = os.path.expanduser(os.environ.get("PASTE_DIR", "~/pasted_images"))
PORT = int(os.environ.get("PASTE_PORT", "8153"))
HOST = os.environ.get("PASTE_HOST", "0.0.0.0")
os.makedirs(DIR, exist_ok=True)

PAGE = '''<!doctype html><meta charset="utf-8">
<body style="font:1em sans-serif;text-align:center;padding:50px">
<h2>Drop, choose, or paste a file</h2>
<p style="color:#666">Drag &amp; drop a file anywhere, click to choose, or Ctrl+V a screenshot.</p>
<input type="file" multiple id="fi">
<div id="l" style="margin-top:1em"></div>
<script>
async function upload(f) {
  let res = await fetch('/save', {
    method: 'POST',
    headers: {'X-Filename': encodeURIComponent(f.name || ''), 'X-Filetype': f.type || ''},
    body: f
  });
  let j = await res.json();
  document.getElementById('l').innerHTML = `✅ ${j.path}<br>` + document.getElementById('l').innerHTML;
}
function send(files) { for (const f of files) upload(f); }
// 1) Paste (screenshots everywhere; pasted files where the browser allows)
document.onpaste = e => {
  const dt = e.clipboardData;
  let files = [...(dt.files || [])];
  if (!files.length)
    files = [...dt.items].filter(i => i.kind === 'file').map(i => i.getAsFile()).filter(Boolean);
  if (files.length) send(files);
};
// 2) Drag & drop (reliable for real files on every OS, incl. Windows Explorer)
const b = document.body;
b.ondragover = e => { e.preventDefault(); b.style.background = '#eef'; };
b.ondragleave = e => { b.style.background = ''; };
b.ondrop = e => { e.preventDefault(); b.style.background = ''; if (e.dataTransfer.files.length) send(e.dataTransfer.files); };
// 3) File picker (works in every browser/OS)
document.getElementById('fi').onchange = e => { send(e.target.files); e.target.value = ''; };
</script>'''


def save_bytes(data, filename, ctype):
    name = os.path.basename(unquote(filename or "").replace("\\", "/"))
    ts = int(time.time() * 1000)
    if name:
        name = f"{ts}_{name}"
    else:
        ct = (ctype or "").split(";")[0].strip()
        ext = mimetypes.guess_extension(ct) or ".bin"
        if ext == ".jpe":
            ext = ".jpg"
        name = f"{ts}{ext}"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name) or f"{ts}.bin"
    path = os.path.join(DIR, name)
    with open(path, "wb") as fh:
        fh.write(data)
    return path


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self._reply(200, PAGE)
        else:
            self._reply(404, "not found", "text/plain; charset=utf-8")

    def do_POST(self):
        if self.path != "/save":
            self._reply(404, "not found", "text/plain; charset=utf-8")
            return
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length) if length else b""
        path = save_bytes(data, self.headers.get("X-Filename", ""),
                          self.headers.get("X-Filetype") or self.headers.get("Content-Type", ""))
        self._reply(200, json.dumps({"path": path}), "application/json")

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    print(f"[paste-drop] saving files to: {DIR}")
    print(f"[paste-drop] open http://localhost:{PORT} in a browser on this machine (host={HOST})")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
