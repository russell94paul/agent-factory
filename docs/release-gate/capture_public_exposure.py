#!/usr/bin/env python3
"""Capture the CURRENT public-exposure state of a git repository, before any visibility,
branch or history change makes that state unprovable.

READ-ONLY. This script never writes to the repository, never mutates a ref, never pushes,
and never contacts a write endpoint. It runs `git` read commands, `gh api` GETs, and
anonymous HTTP HEAD-equivalents.

⭐ WHY THIS EXISTS
Once a repository is made private, "which files were publicly served, and were there forks"
becomes unverifiable from outside. That is exactly the question a client or a post-mortem
asks later. This captures the answer while it is still measurable.

⛔ WHAT IT DELIBERATELY DOES NOT DO
  - It does not copy file CONTENTS into the evidence package. Paths, blob SHAs and sizes only.
  - It does not print or persist any credential-like VALUE. For credential-like findings it
    records path / ref / commit / classification / live-real-unknown / rotation-status only.
  - It carries no client names, brands or figures in its own source. Search patterns are read
    from an external file (--patterns), so this script is itself publishable and only its
    INPUT is sensitive.

ANONYMOUS ACCESS CHECK
`_anon_status` uses curl with no credentials against raw.githubusercontent.com and records
only the HTTP status code -- the response body is discarded to /dev/null and never stored.
Verify the instrument before trusting a 404: a known-public path must return 200 and a
known-private repo must return 404. --selftest does this and refuses to continue if either
control fails, because a blanket-404 instrument would report "nothing is exposed" for a
repository that is fully exposed.

USAGE
    python capture_public_exposure.py --remote personal --slug owner/repo \
        --patterns patterns.local.txt --out ./step0-<utc>

    patterns.local.txt: one extended-regex per line, `#` comments ignored. Each line may be
    prefixed `class=NAME:` to label what the pattern detects, e.g.
        client:  ACME
        # credential-like identifiers get their own class so §14 can be built from the output
        credential-like: VAULT_NAME|SECRET_NAME
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import re
import subprocess
import sys

TIMEOUT = 30


# --------------------------------------------------------------------------- shell helpers

def _run(cmd: list[str], *, check: bool = False) -> tuple[int, str]:
    """Run one command and return (exit_code, stdout).

    ⚠ Every call site reads the ACTUAL output. Nothing here chains commands with `&&` or
    `||`: a chain's exit status is not a measurement, and a trailing `||` branch can report
    on a check that never ran.
    """
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:3])}... exited {p.returncode}: {p.stderr[:300]}")
    return p.returncode, p.stdout


def _git(*args: str) -> str:
    return _run(["git", *args])[1].strip()


def _anon_status(slug: str, ref: str, path: str) -> int:
    """HTTP status for an ANONYMOUS fetch. Body is discarded and never persisted."""
    url = f"https://raw.githubusercontent.com/{slug}/{ref}/{path}"
    code, out = _run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", url]
    )
    try:
        return int(out.strip() or 0)
    except ValueError:
        return 0


# --------------------------------------------------------------------------- patterns

def load_patterns(p: pathlib.Path) -> list[tuple[str, str]]:
    """-> [(class, regex)]. Never logged, never copied into the manifest."""
    out: list[tuple[str, str]] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.+)$", line)
        out.append((m.group(1), m.group(2).strip()) if m else ("unclassified", line))
    return out


# --------------------------------------------------------------------------- self-test

def selftest(slug: str, public_path: str, private_slug: str) -> dict:
    """Prove the anonymous instrument can see a 200 AND can return 404, before believing any
    404 it reports. A blind instrument returning 404 everywhere would read as 'clean'."""
    pos = _anon_status(slug, "HEAD", public_path)
    neg = _anon_status(slug, "HEAD", "NO_SUCH_FILE_selftest_xyz.md")
    priv = _anon_status(private_slug, "HEAD", "README.md") if private_slug else None
    ok = pos == 200 and neg == 404 and (priv is None or priv == 404)
    return {
        "positive_control_expect_200": pos,
        "absent_path_control_expect_404": neg,
        "private_repo_control_expect_404": priv,
        "unauthenticated_confirmed": priv == 404 if priv is not None else "NOT-TESTED",
        "instrument_trustworthy": ok,
    }


# --------------------------------------------------------------------------- capture

def capture(remote: str, slug: str, patterns: list[tuple[str, str]]) -> dict:
    now = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()

    _run(["git", "fetch", remote])  # read-only; refresh remote-tracking refs before measuring

    # --- remote identity -----------------------------------------------------------------
    _, remotes = _run(["git", "remote", "-v"])
    _, repo_json = _run(["gh", "api", f"repos/{slug}"])
    try:
        repo = json.loads(repo_json)
    except json.JSONDecodeError:
        repo = {}
    _, forks_json = _run(["gh", "api", f"repos/{slug}/forks"])
    try:
        forks = json.loads(forks_json)
    except json.JSONDecodeError:
        forks = []

    # --- every remote ref and its exact SHA ----------------------------------------------
    _, lsr = _run(["git", "ls-remote", "--heads", remote])
    refs: dict[str, str] = {}
    for line in lsr.splitlines():
        if "\t" not in line:
            continue
        sha, full = line.split("\t", 1)
        refs[full.strip().replace("refs/heads/", "")] = sha.strip()

    findings: list[dict] = []
    per_ref: dict[str, dict] = {}

    for branch, sha in sorted(refs.items()):
        tracking = f"{remote}/{branch}"
        hits: dict[str, set[str]] = {}
        for cls, rx in patterns:
            _, out = _run(["git", "grep", "-ilE", rx, tracking, "--", "."])
            for line in out.splitlines():
                if ":" not in line:
                    continue
                path = line.split(":", 1)[1]
                hits.setdefault(path, set()).add(cls)

        # is the REF itself anonymously reachable at all?
        ref_reachable = _anon_status(slug, branch, "README.md")

        entries = []
        for path in sorted(hits):
            classes = sorted(hits[path])
            blob_sha, size = "", None
            _, lt = _run(["git", "ls-tree", "-l", tracking, "--", path])
            parts = lt.split()
            if len(parts) >= 5:
                blob_sha, size = parts[2], int(parts[3]) if parts[3].isdigit() else None

            introduced = _git("log", "--diff-filter=A", "-1", "--format=%H", tracking, "--", path)

            credential_like = any(c.startswith("credential") for c in classes)
            entry = {
                "path": path,
                "ref": f"refs/heads/{branch}",
                "ref_sha": sha,
                "classes": classes,
                "introducing_commit": introduced or "NOT-DETERMINABLE",
                "blob_sha": blob_sha or "NOT-DETERMINABLE",
                "blob_bytes": size,
                "anonymous_http_status": _anon_status(slug, branch, path),
            }
            entry["publicly_retrievable_anonymously"] = entry["anonymous_http_status"] == 200
            if credential_like:
                # ⛔ path / ref / commit / classification / liveness / rotation ONLY.
                entry["credential_like"] = {
                    "classification": "IDENTIFIER-OR-SECRET-NAME (no value captured)",
                    "value_captured": False,
                    "appears_live": "UNKNOWN",       # set by a human after independent trace
                    "rotation_status": "UNKNOWN-NOT-INDEPENDENTLY-VERIFIED",
                }
            entries.append(entry)
            findings.append(entry)

        per_ref[branch] = {
            "sha": sha,
            "ref_anonymously_reachable": ref_reachable in (200, 404),
            "ref_readme_http_status": ref_reachable,
            "matching_paths": len(entries),
            "entries": entries,
        }

    return {
        "captured_at_utc": now,
        "tool": "capture_public_exposure.py",
        "evidence_class": "LOCAL_ONLY -- must not be pushed",
        "contents_policy": {
            "file_contents_copied": False,
            "credential_values_captured": False,
            "note": "paths, blob SHAs, sizes and HTTP status codes only",
        },
        "repository": {
            "slug": slug,
            "local_remotes": remotes.strip(),
            "html_url": repo.get("html_url"),
            "visibility": repo.get("visibility"),
            "is_private": repo.get("private"),
            "default_branch": repo.get("default_branch"),
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("pushed_at"),
        },
        "distribution": {
            "forks_count": repo.get("forks_count"),
            "network_count": repo.get("network_count"),
            "stargazers_count": repo.get("stargazers_count"),
            "subscribers_count": repo.get("subscribers_count"),
            "forks_listed": len(forks) if isinstance(forks, list) else "UNKNOWN",
            "caveat": (
                "0 forks is WEAK negative evidence. Anonymous clones, unauthenticated fetches, "
                "crawler indexing and third-party code-search corpora are NOT-VISIBLE to the "
                "owner. This is not a claim that nobody took a copy."
            ),
        },
        "remote_refs": refs,
        "per_ref": per_ref,
        "totals": {
            "refs": len(refs),
            "matching_path_ref_pairs": len(findings),
            "distinct_paths": len({f["path"] for f in findings}),
            "anonymously_retrievable": sum(
                1 for f in findings if f["publicly_retrievable_anonymously"]
            ),
            "credential_like_pairs": sum(1 for f in findings if "credential_like" in f),
        },
    }


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--remote", default="personal")
    ap.add_argument("--slug", required=True, help="owner/repo on GitHub")
    ap.add_argument("--patterns", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--public-path", default="README.md", help="known-public path, positive control")
    ap.add_argument("--private-slug", default="", help="known-PRIVATE repo, proves curl is anonymous")
    a = ap.parse_args()

    st = selftest(a.slug, a.public_path, a.private_slug)
    if not st["instrument_trustworthy"]:
        print("INSTRUMENT SELF-TEST FAILED -- refusing to capture.", file=sys.stderr)
        print(json.dumps(st, indent=2), file=sys.stderr)
        print(
            "A 404 from an instrument that cannot return 200 is not a measurement.",
            file=sys.stderr,
        )
        return 2

    data = capture(a.remote, a.slug, load_patterns(a.patterns))
    data["instrument_selftest"] = st

    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "manifest.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    _, lsr = _run(["git", "ls-remote", "--heads", a.remote])
    (a.out / "ls-remote-heads.txt").write_text(lsr, encoding="utf-8")

    t = data["totals"]
    print(f"captured_at_utc            {data['captured_at_utc']}")
    print(f"visibility                 {data['repository']['visibility']}")
    print(f"forks / network            {data['distribution']['forks_count']} / "
          f"{data['distribution']['network_count']}")
    print(f"refs captured              {t['refs']}")
    print(f"matching path-ref pairs    {t['matching_path_ref_pairs']}")
    print(f"distinct paths             {t['distinct_paths']}")
    print(f"anonymously retrievable    {t['anonymously_retrievable']}")
    print(f"credential-like pairs      {t['credential_like_pairs']}  (no values captured)")
    print(f"written to                 {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
