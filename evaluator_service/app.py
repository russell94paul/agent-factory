"""HTTP transport for the evaluator. Stdlib only — the boundary is the point, not the framework.

Three routes, and no fourth:

    GET  /health          what this evaluator is: identity, bundle hash, corpus, store
    POST /evaluate        {artifact_uri, artifact_sha256, run_id} -> a verdict
    GET  /verdict/<id>    read back a recorded verdict

There is no route that writes a verdict without scoring one, and no route that accepts a corpus,
a manifest or an assertion set. That absence is the security property; everything else here is
plumbing.
"""
from __future__ import annotations

import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, Tuple

from . import service, store

MAX_BODY = 64 * 1024


class Handler(BaseHTTPRequestHandler):
    server_version = "agent-factory-evaluator/1"
    quiet = False

    # ------------------------------------------------------------------ helpers
    def _send(self, status: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt: str, *args) -> None:       # noqa: A003 - stdlib signature
        if not self.quiet:
            super().log_message(fmt, *args)

    def _body(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None, "unreadable Content-Length"
        if length <= 0:
            return None, "empty body"
        if length > MAX_BODY:
            return None, f"body too large ({length} bytes)"
        try:
            return json.loads(self.rfile.read(length).decode("utf-8")), None
        except Exception as exc:                                   # noqa: BLE001
            return None, f"body will not parse: {exc}"

    # ------------------------------------------------------------------ routes
    def do_GET(self) -> None:                             # noqa: N802 - stdlib signature
        path = urllib.parse.urlparse(self.path).path
        if path == "/health":
            return self._send(200, {"ok": True, **service.describe(),
                                    "verdicts_recorded": len(store.recorded())})
        if path.startswith("/verdict/"):
            run_id = urllib.parse.unquote(path[len("/verdict/"):])
            try:
                return self._send(200, store.read(run_id))
            except store.StoreError as exc:
                return self._send(404, {"error": str(exc)})
        return self._send(404, {"error": f"no route {path}"})

    def do_POST(self) -> None:                            # noqa: N802 - stdlib signature
        path = urllib.parse.urlparse(self.path).path
        if path != "/evaluate":
            return self._send(404, {"error": f"no route {path}"})
        body, err = self._body()
        if err:
            return self._send(400, {"error": err})
        try:
            verdict = service.evaluate(body or {})
        except service.Refused as exc:
            # Refusals raised before an artefact was even identified: no run id, so no verdict
            # was recorded and there is nothing to read back. Still a 400, not a 500.
            return self._send(400, {"error": str(exc)})
        except Exception as exc:                                   # noqa: BLE001
            # A crashed evaluator has not observed a pass. Say what broke; never synthesise one.
            return self._send(500, {"error": f"evaluator raised {type(exc).__name__}: {exc}"})
        return self._send(200, verdict)


def make_server(host: str = "127.0.0.1", port: int = 8787, quiet: bool = False) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {"quiet": quiet})
    return ThreadingHTTPServer((host, port), handler)
