#!/usr/bin/env python3
"""Local server for The Morning Brief.

Serves the repo at http://localhost:8899 and accepts votes.

Why a server at all: the issues are static HTML, so a thumbs-up has
nowhere to go. localStorage would keep the vote inside one browser where
the next morning's run can never read it. This keeps everything on disk,
local, with no account and nothing leaving the machine.

  GET  /                      -> latest.html
  GET  /<path>                -> file from the repo
  GET  /fb/state?issue=<day>  -> {id: "up"|"down"} already voted
  POST /fb                    -> record one vote (JSONL, append-only)
"""
import json, os, sys, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTES = os.path.join(REPO, "feedback", "votes.jsonl")
PORT = int(os.environ.get("BRIEF_PORT", "8899"))


def read_votes():
    """Last write wins, so a changed mind replaces the earlier vote."""
    out = {}
    if not os.path.exists(VOTES):
        return out
    with open(VOTES, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                v = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[v["id"]] = v
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=REPO, **kw)

    def log_message(self, *a):
        pass                                    # quiet; launchd keeps the log

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            self.path = "/latest.html"
            return super().do_GET()
        if u.path == "/fb/state":
            day = (parse_qs(u.query).get("issue") or [""])[0]
            votes = read_votes()
            return self._json({k: v["vote"] for k, v in votes.items()
                               if not day or v.get("issue") == day})
        if u.path == "/fb/all":
            return self._json(list(read_votes().values()))
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/fb":
            return self._json({"error": "not found"}, 404)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            v = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self._json({"error": "bad json"}, 400)
        if not v.get("id") or v.get("vote") not in ("up", "down", "clear"):
            return self._json({"error": "need id and vote"}, 400)
        v["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        os.makedirs(os.path.dirname(VOTES), exist_ok=True)
        with open(VOTES, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(v, ensure_ascii=False) + "\n")
        return self._json({"ok": True, "id": v["id"], "vote": v["vote"]})


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"brief server on http://localhost:{PORT} (repo: {REPO})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
