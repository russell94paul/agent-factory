#!/usr/bin/env python
"""Replay the recorded event stream through the preflight, and report what each run WOULD see.

    python scripts/replay_recurrence.py            # every ticket in the stream
    python scripts/replay_recurrence.py GP-327     # one ticket

⛔ **READ-ONLY. This writes nothing.** It opens `.data/events.jsonl` for reading and prints. It is
the shadow-mode instrument: it answers *"which historical starts would have emitted a warning, and
which would have been marked would_refuse"* without any of them having been affected.

⚠ It reads the LIVE stream in the primary worktree, so its output is a measurement of the estate
as it is right now, not a fixture. The fixture — frozen, committed, and independent of what
another session ran an hour ago — is `tests/test_recurrence_preflight.py`. If the two disagree,
the stream has moved; that is information, not a failure.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from factory import events, preflight, presets          # noqa: E402
from factory.contract import Verdict                    # noqa: E402


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    want = argv[0] if argv else None

    run_ids = events.runs()
    if not run_ids:
        print(f"no runs recorded in {events.path()}")
        print("NOT-RECORDED, not zero: nothing has executed through factory.control here.")
        return 0

    print(f"{len(run_ids)} run(s) in {events.path()}\n")
    words_total = words_n = 0
    warned = would_refuse = 0

    for run_id in run_ids:
        fold = events.fold(run_id)
        ticket = fold.get("ticket")
        if want and ticket != want:
            continue
        preset = presets.by_id(fold.get("chosen")) if fold.get("chosen") else None
        m = preflight.check(ticket, {"preset": preset}, before=run_id)
        ev = m.as_event()
        actual = fold.get("verdict") or "no verdict recorded"
        fam = fold.get("failure_family")
        derived = ""
        if not fam and actual not in (None, Verdict.PASS.value):
            derived = f"  (family re-derived: {preflight.classify_recorded(fold).family})"

        print(f"attempt {ev['attempt_number']}  {run_id}  ticket={ticket}")
        print(f"   actually ended  {actual}{derived}")
        print(f"   would be told   {'WARNING' if ev['warning_emitted'] else '(nothing)'}"
              f"   prior={ev['prior_attempt_count']}"
              f"   family={ev['prior_failure_family']}"
              f"   same_as_prior={ev['same_family_as_prior']}")
        print(f"   prevention      {ev['prevention_check_result']} — {ev['prevention_detail']}")
        print(f"   would_refuse    {ev['would_refuse']}   [{ev['policy']}]"
              f"   packet={ev['context_packet_words']} words")
        if m.packet:
            words_total += ev["context_packet_words"]
            words_n += 1
            warned += 1
            if ev["would_refuse"]:
                would_refuse += 1
            print("   ----- packet as the agent would receive it -----")
            for line in m.packet.splitlines():
                print(f"   | {line}")
        print()

    print("=" * 78)
    print(f"warnings that would have been emitted   {warned} of {len(run_ids)} run(s)")
    print(f"marked would_refuse (shadow, not acted) {would_refuse}")
    if words_n:
        print(f"packet size                             mean {words_total / words_n:.1f} words, "
              f"max budget {preflight.MAX_PACKET_WORDS}")
    print()
    print("classification of the recorded failures:")
    print(f"  {preflight.unclassified_share()}")
    print()
    print("⛔ Every number above is shadow. No historical run was affected, and in V0 no future "
          "run is refused.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
