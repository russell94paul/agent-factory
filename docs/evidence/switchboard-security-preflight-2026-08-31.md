# Switchboard security preflight — source-only, before any launch

**Date:** 2026-08-31 · **Method:** source read only. Switchboard was **never launched**, and no
Switchboard database was created on this machine. Clone is `doctly/switchboard` @ `35aa2d7`,
`v0.0.34`, dated 2026-08-28, taken `--depth 1` into a scratchpad outside the repos tree.

⚠ **No transcript content was read to produce this.** The exposure figures below are file counts
and byte sizes only. Grepping 712 transcripts for credential-shaped strings would have pulled the
very values this document exists to protect into a session transcript — which is the failure mode,
not the measurement.

**Ordered by ChatGPT revision 3 (2026-08-31):** *"Until this preflight passes,
`USE_SWITCHBOARD_AS_IS` is not an eligible recommendation."*

---

## Verdict

⛔ **The preflight FAILS on questions 5, 6, 7 and 8. `USE_SWITCHBOARD_AS_IS` is not eligible.**

There is **no exclusion, allowlist, redaction or index-disable mechanism anywhere in the source**,
the scan root is hardcoded to the user's home directory, and clearing the index does not stick —
a future version migration re-scans everything on disk.

The exposure is **narrower than feared and real**: not whole transcripts, but the opening ~8 KB of
every conversation — which is precisely where a human pastes things.

---

## What would be indexed on this machine

Measured 2026-08-31, counts and sizes only:

```
find ~/.claude/projects -maxdepth 1 -mindepth 1 -type d | wc -l   ->  36 project folders
find ~/.claude/projects -name '*.jsonl' | wc -l                   -> 712 transcripts
du -sh ~/.claude/projects                                         -> 1.0 GB
```

All 36 folders are in scope. None can be excluded.

---

## The ten questions

### 1. What happens on first launch

`main.js:424` — the `get-projects` IPC handler:

```js
const needsPopulate = !isCachePopulated() || !isSearchIndexPopulated();
if (needsPopulate) { populateCacheViaWorker(); return []; }
```

**The first time the projects list is opened, a full scan begins.** There is no consent prompt, no
first-run dialog, and no setting consulted. `populateCacheViaWorker()` (`session-cache.js:355`)
spawns `workers/scan-projects.js` with `workerData: { projectsDir: PROJECTS_DIR }`.

### 2. Are historical transcripts scanned automatically — yes

`harnesses/claude.js:35`:

```js
return path.join(os.homedir(), '.claude', 'projects');
```

Hardcoded. The worker enumerates every folder beneath it recursively. Every one of the 712
transcripts above is read on the cold-start scan.

### 3. What content is written to SQLite / FTS

This is the load-bearing answer, and it is more bounded than R12 implied.

**The schema** (`db.js:174-188`):

```sql
CREATE VIRTUAL TABLE search_fts USING fts5(title, body, tokenize='trigram case_sensitive 0');
CREATE TABLE search_map (rowid INTEGER PRIMARY KEY, id TEXT, type TEXT, folder TEXT);
```

**The body** is `sess.textContent` (`session-cache.js:156` and `session-cache.js:401`), built at
`harnesses/claude.js:274-276`:

```js
if (text && textContent.length < 8000) {
  textContent += text.slice(0, 500) + '\n';
}
```

where `text` resolves as (`claude.js:264-266`):

```js
const text = typeof msg === 'string' ? msg :
  (typeof msg?.content === 'string' ? msg.content :
  (msg?.content?.[0]?.text || ''));
```

**So the indexed body is: the first 500 characters of each message — user and assistant alike —
concatenated until 8,000 characters, i.e. roughly the first 16 messages of every session.**

Additionally stored as plaintext columns in `session_cache` (`db.js:48`): `summary` and
`firstPrompt`, both set to `text.slice(0, 120)` of the first real user message (`claude.js:271`).

### 4. Can secrets enter that index — yes, by one specific path

| Path | Indexed? | Why |
|---|---|---|
| A secret **pasted by the operator into an early prompt** | ⛔ **YES** | it is inside the first 500 chars of an early message, and also lands in `firstPrompt`/`summary` |
| A secret an assistant **echoes early in a session** | ⛔ **YES** | same rule, assistant messages are indexed identically |
| A secret retrieved **mid-session by a tool call** | ✅ mostly no | only `content[0].text` is read; `tool_result` and later content blocks yield `''` |
| Anything after message ~16, or after char 500 of a message | ✅ no | the 8,000 and 500 caps |

⚠ The tokenizer is `trigram case_sensitive 0` — chosen for substring matching. A high-entropy token
is therefore **findable by substring**, not only by whole-word match. Bounded exposure, but fully
searchable within those bounds.

⭐ **The practical rule this yields:** the existing per-secret approval discipline already protects
the common case, because approved retrievals happen through tool calls mid-session. The uncovered
case is a human pasting a credential into a prompt — which is the case the credential rule already
forbids, now with a durable searchable consequence attached.

### 5. Can projects or paths be excluded BEFORE first indexing — NO

```
grep -rn --include=*.js -iE 'exclude|ignorelist|blocklist|denylist|skipfolder|optout|disableindex|noindex|redact' .
```

over all non-test JavaScript returns **only** SQL `excluded.` UPSERT keywords and two unrelated
comments. There is no exclusion mechanism of any kind.

### 6. Can indexing be disabled — NO

No setting gates `needsPopulate`. The `settings` table (`db.js:74`) holds UI preferences; nothing
reads it on the indexing path.

### 7. Can scanning be restricted to selected projects — NO

`PROJECTS_DIR` has no override, environment variable, or argument. The worker receives it verbatim.

### 8. Deletion / rebuild semantics — deletion does not stick

Deletion primitives exist: `searchDeleteBySession`, `searchDeleteByFolder`, `searchDeleteByType`
(`db.js:236-241`), and migration v2 does `DROP TABLE IF EXISTS search_fts` (`db.js:95`).

⛔ **But two paths silently rebuild the whole index:**

- `main.js:1772` — `if (searchFtsRecreated) populateCacheViaWorker();` — **any future version whose
  migration recreates the FTS table triggers a full re-scan of everything on disk.**
- `main.js:424` — `!isSearchIndexPopulated()` re-populates the moment the projects list is opened.

So clearing the index is not a durable remedy; it is undone by the next app open or upgrade.

### 9. Does it introduce an unnecessary second durable copy — yes, but qualify it

Yes: a WAL-mode SQLite database holding, per session, a 120-char summary, a 120-char first prompt,
and up to 8 KB of message text — derived from 712 transcripts.

⚠ **But the transcripts themselves are already a durable plaintext copy that exists today.**
Switchboard adds a second copy that is *searchable and consolidated*, not a first copy. The honest
statement of the risk is consolidation and searchability, not disclosure of something previously
unrecorded.

### 10. Smallest safe configuration or patch

| | Approach | Patch surface | Notes |
|---|---|---|---|
| **a** | Redact in `harnesses/claude.js` before `textContent +=` | **one function** | smallest surface; upstream-compatible; catches both indexing paths because both read `textContent` |
| **b** | Allowlist on `PROJECTS_DIR` / the worker's folder enumeration | small | restricts *which projects* are scanned; does not protect an in-scope project |
| **c** | Point it at a curated projects directory | zero patch | Windows symlink/junction handling is awkward and easy to get wrong |
| **d** | Scrub the 712 existing transcripts before first launch | none, but **destructive to your own history** | not recommended |

**(a) and (b) are complementary and both small.** (a) is the one that survives an upgrade, because
it changes what is extracted rather than what is stored.

---

## Consequences for the integration decision

1. `USE_SWITCHBOARD_AS_IS` is **not eligible** — ruled out by 5/6/7/8, per revision 3.
2. The remaining options are `THIN_ADAPTER` or `SMALL_EXTENSION`, and both now carry a mandatory
   redaction patch as a precondition of first launch, not as a later hardening step.
3. `DO_NOT_USE_SWITCHBOARD` remains eligible and is unaffected by this preflight.
4. **The first launch is the irreversible act.** Opening the projects list once indexes all 36
   folders, and 8 rules out un-doing it durably. Whatever is decided, it must be decided *before*
   the app is opened, which is why this was ordered ahead of Phase 0.

## What this preflight did not establish

- Whether the redaction patch in (a) is upstream-acceptable, or forks the project.
- Whether `workers/scan-projects.js` has additional extraction not visible from the two call sites
  read here — only the two `upsertSearchEntries` paths were traced.
- Anything about the Codex harness (`harnesses/codex.js`), which has a parallel 8000/500 rule at
  `codex.js:225` and was not examined further.
- Runtime behaviour of any kind. Nothing was executed.
