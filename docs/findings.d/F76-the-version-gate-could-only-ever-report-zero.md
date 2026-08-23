<!-- session: 2026-08-23 · spec + R13 review -->

### F76 — The version-hash gate could only ever report zero, and the zero travelled everywhere as MEASURED

- **KIND** — INSTRUMENT
- **STATUS** — ADOPTED
- **BELIEVED** — "Our version hash covers **0 of 15** dimensions. `[M]`" Stated in
  `ui-surface-inventory.md` §9, in the agent-factory wiki page, in `SYNTHESIS.md` §3.4's framing,
  and — until today — twice in the R13 research prompt, where it was the headline figure of the
  primary question.
- **ACTUALLY** — six dimensions are present. The gate could not have reported anything else:

      as shipped   re.search(rf"\x08{d}\x08", body)   ->  0 of 15, unconditionally
      corrected    re.search(rf"\b{d}\b",     body)   ->  6 of 15

  In an f-string `\b` is the **backspace escape**, not the regex word-boundary token. The pattern
  searched `blueprint.py` for a literal BACKSPACE byte either side of each dimension name, which no
  source file contains. `cat -A` renders it `^H{d}^H`.

  Present: `prompt`, `model`, `effort`, `tools`, `max_turns`, `budget_usd`. Genuinely absent:
  `tool_implementation`, `sandbox_image`, `model_routing`, `context_policy`, `external_knowledge`,
  `permissions`, `contract_version`, `harness_version`, `side_effect_replay`. **The verdict does not
  change** — the gate FAILs either way — only the number becomes honest, and the headline goes from
  *"15 dimensions absent"* to *"9 dimensions absent"*.

  ⭐ **This is the self-matching evaluator probe with the sign flipped.** That one grepped for
  strings that appeared in its own source and could therefore only ever PASS. This one could only
  ever FAIL. **A gate that cannot pass has stopped measuring exactly as completely as one that
  cannot fail** — and it is *harder* to catch, because a red gate on admittedly-unfinished work
  looks like the truth. Nobody re-derives a number that already agrees with them.

  ⚠ **A second, smaller caveat that survives the fix.** The probe greps **source text** for each
  name, so an occurrence in a docstring counts. `6` is an upper bound on *fields present*, not a
  proof the digest covers them. In practice `AgentSpec.version` hashes `asdict(self)`, so every
  field that exists **is** hashed and the nine are absent **as fields** rather than excluded from
  the digest — but the probe does not establish that, and a future field added only to a docstring
  would inflate it.

- **MEASURED BY** — `sed -n '705p' factory/readiness.py | cat -A` shows `^H` either side of `{d}`.
  Then, against the unmodified `factory/blueprint.py`:

      python -c "import re,pathlib; b=pathlib.Path('factory/blueprint.py').read_text();
                 V=['prompt','model','effort','tools','max_turns','budget_usd', ...];
                 print(len([d for d in V if re.search(rf'\x08{d}\x08',b)]),
                       len([d for d in V if re.search(rf'\b{d}\b',b)]))"
      -> 0 6

  After the fix, `python -m factory.readiness` reports
  `version  FAIL  9 dimensions absent from the version` with evidence `6 of 15`.

- **CHANGES** — regex corrected in `factory/readiness.py`, with the reason recorded in the probe's
  own docstring next to the sibling probe that already carries this lesson. **Every downstream
  quotation of "0 of 15" must be corrected to "6 of 15", including
  `ui-surface-inventory.md` §9, the wiki page, and any published artifact.** ⭐ The durable change
  is a rule, not a patch: **a probe that has never returned a non-zero value has not been shown to
  work.** The mutation discipline already applied to contract assertions — prove it can fail —
  applies to readiness gates in the other direction: **prove it can pass.** A gate whose PASS branch
  has never executed deserves a negative control of its own.

- **AFFECTS** — **every lane**, via the rule in CHANGES: any gate whose PASS branch has never
  executed is unverified, and each lane owns gates in that condition. Directly: the `version` gate
  — which ⚠ **belongs to no lane at all** (`lanes.py` assigns `cap/reaper/concurrency/bounded/
  truthful/from-history` to control-plane, `certified/breadth/corpus` to certify,
  `refuses/checks/attributable/honest/general/ceiling/cost` to judgement, `chain` to artifact,
  `grain` to grain — `version` appears in none of them), so nobody was assigned to look at it and
  nobody did. `certify` inherits it, because certification is what the hash is for. Then
  `docs/research/R13-platform-and-manufacturing.md` (D2 was
  dispatching from a false baseline and asking the researcher to correct a number we had wrong);
  `docs/specs/agent-factory-technical-and-business-spec.md` §3.2 and §7;
  `docs/research/ui-surface-inventory.md` §9; the agent-factory wiki page; and `SYNTHESIS.md` §3.4,
  which records R2's finding that nine dimensions are missing — that count is now the *measured*
  one, which is a coincidence worth noticing rather than trusting.
