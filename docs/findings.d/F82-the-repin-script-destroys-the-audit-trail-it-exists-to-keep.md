### F82 — `pin_corpus.py` erases the manifest history that is the whole reason it demands a `--why`

- **BELIEVED** — `scripts/pin_corpus.py` is the sanctioned, auditable way to change the corpus pin.
  Its own docstring:

  > *"This script is the only sanctioned way to change the pin, and it refuses to run without a
  > stated reason, because **'why did the grader change' is exactly the question a silent re-pin
  > destroys**."*

  And `evals/MANIFEST.sha256` carried a superseded entry recording exactly that, in its own words:
  *"Recorded so the re-hash is auditable rather than silent."*

- **ACTUALLY** — the script **rebuilds the manifest from scratch** and drops every comment line.
  `_read_manifest()` (`pin_corpus.py:29-34`) deliberately *skips* `#` lines when reading:

  ```python
  if line and not line.startswith("#"):
      sha, _, rel = line.partition("  ")
  ```

  but `main()` writes only the freshly computed active lines:

  ```python
  lines.append(f"{sha}  {rel}")
  ...
  MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
  ```

  **The reader tolerates history; the writer destroys it.** So the `--why` is printed to stdout,
  recorded nowhere by the script, and the previous supersession record is deleted in the same
  breath. The stated reason survives only if a human remembers to paste it into the commit message
  — and the audit chain in the file does not survive at all.

  Observed 2026-08-30: a legitimate re-pin removed a four-line record of the 2026-08-29 redaction
  re-hash. Net effect on the manifest was `-5 / +1`.

  ⭐ **The mechanism is the one this repo is built to catch: a control that reports success while
  doing the opposite of its stated purpose.** `pin_corpus.py` printed *"re-pinned 1 file(s)"* and
  *"reason recorded"* — and the reason was recorded nowhere, while the previous reason was erased.

- **MEASURED BY** — discriminating check, result predicted before it ran. Predicted: if the writer
  rebuilds from `rglob` rather than editing in place, every `#` line disappears and the diff is
  larger than the one hash that changed. Observed:

  ```
  $ git diff HEAD~1 -- evals/MANIFEST.sha256
  -# c3fbfed8…  corpus/windsorai-2026-08-20.json
  -#   ^ superseded 2026-08-29: a client identifier was redacted to CLIENT-A.
  -#     Measurements unchanged; only an identifier string differs. Recorded so the
  -#     re-hash is auditable rather than silent.
  -f7cd15c2…  corpus/windsorai-2026-08-20.json
  +5c0d63ea…  corpus/windsorai-2026-08-20.json
  ```

  Restored by hand in the same commit range; `pin_corpus.py --check` and `corpus.stamp()` both still
  verify against the restored file, which confirms the comment lines are inert to the reader and the
  loss was pure history.

- **AFFECTS** — every future re-pin, and the credibility of the corpus as evidence.

  1. ⛔ **Until fixed, re-add the superseded lines by hand after every `pin_corpus.py` run.** A note
     to that effect is now at the top of `evals/MANIFEST.sha256`.
  2. **The fix is small and should be in the script, not in a habit.** Read the existing file, keep
     every `#` line, demote the outgoing active line to a comment with the date and the `--why`
     text, then append the new active line. The `--why` is already required and already validated
     for length — it just is not persisted.
  3. **A control whose evidence is discarded is not a control.** The script's own argument for
     existing is that a silent re-pin destroys the question *"why did the grader change"*. It
     answers that question to stdout, then deletes the previous answer from disk.
  4. Same family as this estate's recurring shape, but a new variant: not *written and unwired*
     (F79 and its four predecessors) — **wired, running, reporting success, and undoing its own
     purpose.** Closest sibling is the inert-control shape in
     `wiki/concepts/patterns/vacuous-verification.md`.

- **NOT MEASURED** — whether any earlier re-pin already lost history that nobody restored. The
  2026-08-29 entry survived only because it was the most recent; anything superseded before it would
  have been dropped by that run and would leave no trace to find. **`git log -p -- evals/MANIFEST.sha256`
  is the only place that history could still exist**, and it has not been read.
