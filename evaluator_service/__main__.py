"""Run the evaluator service.

    python -m evaluator_service                       # 127.0.0.1:8787
    python -m evaluator_service --host 0.0.0.0 --port 8787 --identity evaluator-aci

``--identity`` is a convenience for local work only. In a real deployment the identity is the
managed identity the container runs as, and the agent sandbox does not hold it; a flag the agent
could pass is not an identity, which is why it is named here as a convenience rather than sold as
a control.
"""
from __future__ import annotations

import argparse
import os
import sys

from . import service
from .app import make_server


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="evaluator_service")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--identity", default=None, help="local convenience; see module docstring")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.identity:
        os.environ["AGENT_FACTORY_EVALUATOR_IDENTITY"] = args.identity

    srv = make_server(args.host, args.port, quiet=args.quiet)
    host, port = srv.server_address[0], srv.server_address[1]
    d = service.describe()
    print(f"evaluator listening on http://{host}:{port}")
    print(f"  identity      {d['identity']}")
    print(f"  bundle        {d['bundle_sha256'][:16]}")
    print(f"  corpus        {d['corpus_id']}  <- resolved here, never from a submission")
    print(f"  verdict store {d['verdict_store']}  (write-once)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("stopped")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
