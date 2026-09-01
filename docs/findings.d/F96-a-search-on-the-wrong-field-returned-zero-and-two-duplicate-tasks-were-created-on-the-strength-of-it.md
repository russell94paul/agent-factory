### F96 — a search on the wrong field returned zero, the zero was read as absence, and two duplicate tasks were created on the strength of it

Filed 2026-09-01 by the Mission Commander session, from evidence gathered by its predecessor and
re-measured here. The defect it records was committed on **2026-08-31 — the same day six
absence-green gates were fixed**, by the session that fixed them.

## What happened, in order

```
mission plan written        8 tasks intended: R1 R2 R3 D1 D2 D3 D4 D5
materialised into store     8 tasks created, correctly parented to 0d26cd2f, DAG fully wired
later session asks          "were the mission tasks ever created?"
search run                  [e for e in events if 'R1' in e.get('task')]
result                      0
read as                     the plan was never materialised
acted on                    created R1 (fbe2ea4c) and R2 (200deda2) as replacements
```

`e['task']` is the **task id** — an 8-character hex string. `"R1"` lives in
`e['data']['title']`. The search asked a question the field could not answer, and the field
answered honestly.

## It reproduces exactly

```bash
python -c "
import json
ev=[json.loads(l) for l in open('.data/tasks.jsonl',encoding='utf-8') if l.strip()]
print('filter on task id ->', len([e for e in ev if 'R1' in (e.get('task') or '')]))
print('filter on title   ->', len([e for e in ev if 'R1' in str((e.get('data') or {}).get('title') or '')]))
"
filter on task id  -> 0
filter on title    -> 14
```

Same store, same string, same instant. **0 and 14 are the same measurement run against two
different fields**, and only one of them was ever going to be non-zero.

## The cost, which is still on the books

The mission `0d26cd2f` now has **10 child tasks for 8 declared logical units**. The two extras are
annotated `SUPERSEDED` in the append-only store, which is the correct repair — the store cannot
forget — but the population is permanently over-counted for anything that enumerates children
rather than reading annotations. Session 3's Client Review pass hit this independently and
correctly reported **naive progress 40% vs defensible progress 25%**, because R1 and R2 each
appear twice among the observed children while the declared plan has one of each.

⭐ **A duplicate object created from a false negative outlives the false negative.** The search was
corrected in minutes; the extra rows are in an append-only ledger forever, and every consumer that
counts must now know to subtract them.

- **BELIEVED** — a zero-result search over the task store means the objects are absent, so the
  safe repair is to create them.

- **ACTUALLY** — the search was pointed at `task` (the id) rather than `data.title`, so it was
  structurally incapable of returning a hit for `"R1"`. The eight tasks existed the whole time,
  correctly parented, with all 25 `block` edges already wired. The zero measured the query, not
  the store.

- **MEASURED BY** — the two-line reproduction above: the same predicate against the id field and
  the title field, over the same file, printing 0 and 14. The **positive control is the whole
  test** — searching for a string that is *known* to exist and getting zero back tells you the
  instrument is blind, before you act on any negative.

- **AFFECTS** — **every lane**, and that is the literal answer rather than a shrug: every lane runs
  negative queries — a grep for a consumer, a search for a gate, a check that an object is absent —
  and this repo's own rule (*a zero from an instrument you have not shown can see is not a
  measurement*) is the one that was broken. `F84` is the same defect measured by a blind grep;
  `F86` is the same defect in the findings ledger itself. Concretely: `.data/tasks.jsonl` (10
  children for 8 logical tasks, permanently), any consumer that enumerates mission children by
  count rather than by annotation — including the Client Review progress figure — and
  `factory/tasks.py` consumers generally.

- **KIND** — INSTRUMENT

- **STATUS** — OPEN
