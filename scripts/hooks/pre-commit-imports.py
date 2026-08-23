#!/usr/bin/env python3
"""Refuse a commit whose tree does not import.

⭐ **This checks the INDEX, not the working tree, and that distinction is the whole point.**

On 2026-08-23 commit `fc71b6a` staged a `factory/claims.py` containing
`from . import repo as _repo` while `factory/repo.py` was still **untracked**. Every check
anyone could have run in the working directory passed — `repo.py` was sitting right there on
disk. The committed tree did not import at all. A fresh clone of that branch was broken, and
nobody would have known until someone cloned it.

So a working-directory import check would have been worse than useless here: it would have
passed, confidently, over the exact defect. This exports what git is *about to commit* into a
temporary directory and imports from there. An untracked dependency is then absent, which is
precisely what the reader of that commit would experience.

The failure mode this exists for is not carelessness. It is **two sessions editing one
checkout**: one session had `repo.py` open and unstaged, another ran `git add` across the
directory and committed a file that referenced it. No individual acted wrongly.

Install:  python scripts/hooks/pre-commit-imports.py --install
Run:      python scripts/hooks/pre-commit-imports.py           (what the hook calls)
Bypass:   git commit --no-verify                               (say why in the commit message)

Exit 0 = the tree imports. Exit 1 = it does not, and the commit is refused.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent.parent

#: Packages whose modules must all import. Kept explicit: a glob over the repo would drag in
#: one-off ticket scripts whose imports were never meant to hold, and a check that fails for
#: reasons nobody will fix is a check people learn to bypass.
PACKAGES = ("factory",)


def _git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=str(cwd or REPO), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def _export_index(dest: pathlib.Path) -> bool:
    """Write the about-to-be-committed tree into `dest`.

    `git checkout-index` reads the INDEX, so for a partial commit it yields staged versions of
    staged files and HEAD versions of everything else — exactly the tree the commit will create.

    ⚠ Exports the WHOLE index, not just the .py files. A first cut exported only `factory/*.py`
    and two modules failed for the wrong reason: `calibration` reads `evals/MANIFEST.sha256` at
    import and `dispatch` validates its map against `docs/research/*.md`, and neither was in the
    narrowed tree. Both files are tracked, so a real clone has them. The check is only meaningful
    if the tree it builds is the tree a reader would actually get — 164 files and 9.3 MB, which
    is cheap enough that narrowing it bought nothing but false positives.
    """
    prefix = str(dest) + os.sep
    proc = subprocess.run(["git", "checkout-index", "--all", "--force", f"--prefix={prefix}"],
                          cwd=str(REPO), capture_output=True, text=True)
    return proc.returncode == 0


def check() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="agent-factory-precommit-"))
    try:
        if not _export_index(tmp):
            # Cannot look is not the same as broken. Say so and let the commit through, rather
            # than blocking work on an instrument failure — but never call that a pass.
            print("pre-commit: UNMEASURABLE — could not export the index; commit allowed",
                  file=sys.stderr)
            return 0

        mods = []
        for pkg in PACKAGES:
            d = tmp / pkg
            if not d.is_dir():
                continue
            for f in sorted(d.rglob("*.py")):
                if "__pycache__" in f.parts:
                    continue
                rel = f.relative_to(tmp).with_suffix("")
                parts = list(rel.parts)
                if parts[-1] == "__init__":
                    parts = parts[:-1]
                if parts:
                    mods.append(".".join(parts))

        if not mods:
            print("pre-commit: UNMEASURABLE — no modules found in the exported tree",
                  file=sys.stderr)
            return 0

        script = "import importlib, sys\n"
        script += "bad = []\n"
        script += f"for m in {mods!r}:\n"
        script += "    try:\n        importlib.import_module(m)\n"
        script += "    except Exception as exc:\n"
        script += "        bad.append((m, type(exc).__name__, str(exc)[:200]))\n"
        script += "for m, k, e in bad:\n    print(f'{m}: {k}: {e}')\n"
        script += "sys.exit(1 if bad else 0)\n"

        # Empty PYTHONPATH and cwd=tmp so the exported tree is the ONLY thing importable. Without
        # this the real checkout on sys.path would satisfy the very import we are testing for.
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        r = subprocess.run([sys.executable, "-c", script], cwd=str(tmp),
                           capture_output=True, text=True, env=env, timeout=120)
        if r.returncode == 0:
            return 0

        print("", file=sys.stderr)
        print("COMMIT REFUSED — the tree you are about to commit does not import.", file=sys.stderr)
        print("", file=sys.stderr)
        for line in (r.stdout or "").strip().splitlines():
            print("  " + line, file=sys.stderr)
        print("", file=sys.stderr)
        print("  The working directory may well import fine. That is the point: this checked", file=sys.stderr)
        print("  the INDEX. The usual cause is a staged file importing something that is still", file=sys.stderr)
        print("  untracked — run `git status` and look for a `??` the staged code depends on.", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Stage it, or `git commit --no-verify` and say why.", file=sys.stderr)
        print("", file=sys.stderr)
        return 1
    except Exception as exc:                                       # noqa: BLE001
        print(f"pre-commit: UNMEASURABLE — {type(exc).__name__}: {exc}; commit allowed",
              file=sys.stderr)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def install() -> int:
    code, out, _ = _git("rev-parse", "--git-common-dir")
    if code != 0:
        print("not a git repository", file=sys.stderr)
        return 1
    gitdir = pathlib.Path(out.strip())
    if not gitdir.is_absolute():
        gitdir = REPO / gitdir
    hooks = gitdir / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-commit"
    # --git-common-dir, not --git-dir: a linked worktree has its own gitdir but SHARES hooks/
    # with the primary, so installing once covers every lane worktree.
    # POSIX forward slashes, not the native Windows form. Inside sh double-quotes a backslash
    # only escapes a few characters, so a Windows path happens to survive — but that is a
    # property of which letters follow the backslashes, not a guarantee. Windows Python accepts
    # forward slashes everywhere, so this removes the coincidence.
    body = ("#!/bin/sh\n"
            "# installed by scripts/hooks/pre-commit-imports.py\n"
            f'exec "{pathlib.Path(sys.executable).as_posix()}" '
            f'"{pathlib.Path(__file__).resolve().as_posix()}"\n')
    if hook.exists() and "pre-commit-imports.py" not in hook.read_text(encoding="utf-8"):
        print(f"refusing to overwrite an existing hook at {hook}", file=sys.stderr)
        print("merge it by hand, or move it aside first", file=sys.stderr)
        return 1
    hook.write_text(body, encoding="utf-8")
    os.chmod(hook, 0o755)
    print(f"installed {hook}")
    print("shared with every lane worktree (git hooks live in the common dir)")
    return 0


if __name__ == "__main__":
    raise SystemExit(install() if "--install" in sys.argv else check())
