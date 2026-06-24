# img-drop

A tiny, **zero-dependency** file dropbox. Run the server, open the page in any
browser, then **drag-and-drop**, **choose**, or **paste** a file — it's saved on
the machine running the server.

## Run

```sh
python3 server.py
```

Then open <http://localhost:8153> (or `http://<server-ip>:8153` from another
machine on the same network).

Standard library only — **no `pip install`**, works on Linux, macOS, and Windows
with any Python 3.7+.

## Why three ways to add a file

- **Drag & drop** and the **file picker** work reliably for real files in every
  browser/OS (including dragging from Windows Explorer).
- **Paste** (`Ctrl+V`) is great for screenshots; pasting a file copied in a file
  manager is browser-dependent, which is why drop/picker exist.

## Configuration (optional env vars)

| Var          | Default           | Meaning                                       |
|--------------|-------------------|-----------------------------------------------|
| `PASTE_DIR`  | `~/pasted_images` | where uploaded files are saved                |
| `PASTE_PORT` | `8153`            | port to listen on                             |
| `PASTE_HOST` | `0.0.0.0`         | bind address (`127.0.0.1` for localhost-only) |

Files keep their original name (timestamp-prefixed to avoid collisions); a
pasted screenshot gets a type-derived name like `<ts>.png`. Filenames are
sanitized so an upload can't escape the save directory.
