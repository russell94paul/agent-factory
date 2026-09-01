#!/usr/bin/env python
"""Append-only record of which secret was used, when, by which task, and for what.

    python scripts/credential_use.py --secret prod-dg1-core-admin --source azure-kv:aldc-vault-prod \
        --task R3 --access READ --purpose "marketing model cartography — grain of ad spend fact"

    python scripts/credential_use.py --list

⭐ **This exists because a standing grant without a record is unauditable.** On 2026-08-31 Paul
replaced ask-every-time with a standing licence for work driven from this repo. That moves the human
gate from *before* the retrieval to *after* it — which is only a control if the "after" is real.
Without this file the grant is indistinguishable from no policy at all.

⛔ **The VALUE is never accepted, never stored, never logged.** This records that secret *named* X
from source Y was used — nothing more. `--secret` takes a name; if you find yourself wanting to pass
a value, the calling code is already wrong: capture it in a subshell so it never becomes a variable
this process could see.

Lives in `.data/`, which is gitignored on purpose — the same reasoning `claims.py` gives for not
committing claims: "a session is running on this machine" is a local fact, and committing it would
make every clone claim to be busy. Which secret *this machine* used is the same kind of fact.

Follows the `.data/research-dispatch.jsonl` precedent rather than `factory.events`: `events.KINDS` is
a closed set and every record is bound to a run id, but a manually-launched mission has no run.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import sys

LOG = pathlib.Path(__file__).resolve().parent.parent / ".data" / "credential-use.jsonl"

#: A value is never a valid `--secret`. These are the shapes that mean somebody passed one by
#: mistake, and the refusal is louder than a silent log entry containing a live credential.
def _looks_like_a_value(name: str) -> str | None:
    if len(name) > 64:
        return "longer than any secret NAME needs to be"
    if any(c.isspace() for c in name):
        return "contains whitespace"
    if name.count("=") or name.startswith(("eyJ", "-----BEGIN")):
        return "looks like an encoded token or key material"
    return None


def record(secret: str, source: str, task: str, access: str, purpose: str) -> dict:
    why = _looks_like_a_value(secret)
    if why:
        raise SystemExit(
            f"refusing to log {secret[:8]}… — {why}.\n"
            "--secret takes the secret's NAME, never its value. If a value reached this argument, "
            "capture it in a subshell instead so no process here can see it.")
    if access not in {"READ", "WRITE"}:
        raise SystemExit(f"--access must be READ or WRITE, got {access!r}")
    rec = {"at": _dt.datetime.now(_dt.timezone.utc).isoformat(), "secret": secret,
           "source": source, "task": task, "access": access, "purpose": purpose}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def read() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(ln) for ln in LOG.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--secret", help="the secret's NAME — never its value")
    ap.add_argument("--source", help="e.g. azure-kv:aldc-vault-prod, wiki-vault")
    ap.add_argument("--task", default="", help="task id this use belongs to")
    ap.add_argument("--access", default="READ", help="READ | WRITE")
    ap.add_argument("--purpose", default="", help="what it was needed for")
    ap.add_argument("--list", action="store_true", help="print the log")
    a = ap.parse_args(argv)

    if a.list:
        rows = read()
        if not rows:
            # NOT-RECORDED, not zero. An empty log means nothing was written here — it does not
            # mean no credential was used, and saying otherwise would be the collapse this estate
            # keeps paying for.
            print(f"no rows in {LOG} — NOT-RECORDED, which is not the same as 'no credential used'")
            return 0
        for r in rows:
            print(f"{r['at']}  {r['access']:<5} {r['secret']:<32} {r['source']:<28} "
                  f"{r['task']:<6} {r['purpose']}")
        print(f"\n{len(rows)} use(s)  <- {LOG}")
        return 0

    if not (a.secret and a.source):
        ap.error("--secret and --source are required unless --list")
    r = record(a.secret, a.source, a.task, a.access, a.purpose)
    print(f"recorded: {r['access']} {r['secret']} from {r['source']} for {r['task'] or '(no task)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
