#!/usr/bin/env python3
"""Local dev server for editing photo framing directly on the page.

Serves this directory like `python3 -m http.server`, plus a PUT handler
for `.image-slots.state.json` — the sidecar file the page's built-in
<image-slot> editor writes to when you double-click a photo to drag/resize
it (pan + zoom), matching the Claude Design canvas' bridge contract.

Usage:
    python3 dev_server.py [port]   # default port 8000

Then open http://localhost:8000/index.html, double-click any photo in the
"A sport that gives kids somewhere to belong" section, and drag to reposition
or grab a corner to resize/zoom. Click outside the photo (or press Esc) to
save — the crop is written to .image-slots.state.json in this folder.
"""
import http.server
import socketserver
import sys

STATE_FILE_BASENAME = ".image-slots.state.json"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_PUT(self):
        path = self.path.split("?", 1)[0].lstrip("/")
        if path != STATE_FILE_BASENAME:
            self.send_error(403, "Only %s may be written" % STATE_FILE_BASENAME)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        with open(STATE_FILE_BASENAME, "wb") as f:
            f.write(body)
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        # Keep the default stdout logging; nothing to customize for now.
        super().log_message(fmt, *args)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving {__file__.rsplit('/', 1)[0] or '.'} at http://localhost:{port}/index.html")
        print("Double-click a photo in the about section to drag/resize it.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
