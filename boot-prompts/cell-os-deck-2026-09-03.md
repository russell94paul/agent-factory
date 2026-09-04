# Boot — CELL//OS Command Deck, and the revenue primitives it is missing

`main` @ `48fae74` + 3 uncommitted paths · written 2026-09-03 · supersedes nothing

**next:** add the three-way agency comparison tab, then design the seven revenue entities in
§3 as a spec under `docs/specs/`. Do not build them into the deck until the spec exists — the
deck is a *presentation* of the object model and the object model does not yet contain money.

---

## 1. State — what exists right now

| Artifact | Where | Status |
|---|---|---|
| **Command Deck** — 7 tabs, the product artifact | `docs/marketing/cell-os-launch-v1/cell-os-deck.html` | published, render-checked PASS, ⛔ **uncommitted** |
| Launch film package — 10 files | `docs/marketing/cell-os-launch-v1/` | committed `48fae74`, pushed |
| Previz bay — watchable 90s timeline | `docs/marketing/cell-os-launch-v1/previz.html` | committed, published |
| Deck render check | `scripts/render_check_deck.py` | ⛔ **uncommitted** |
| Deck evidence — 6 screenshots + JSON | `docs/evidence/cell-os-deck-2026-09-02/` | ⛔ **uncommitted** |
| Skills — `launch-narrative`, `launch-film` | `~/.claude/skills/` | live, routed in `INDEX.md` |

Published URLs (private artifacts, Paul's account):
- Command Deck — `https://claude.ai/code/artifact/761ebd4f-1c5c-4c9a-bcd2-ba6109969ca4`
- Previz bay — `https://claude.ai/code/artifact/db289afc-5bde-44e6-b79f-5827513a1d75`

**Sources the deck was built from, all four read in full:** `docs/diagrams/CELL OS - Architecture
Overview.png`, `docs/diagrams/CELL OS - Building your first OPC.png`,
`docs/design/CELL_OS_Product_Technical_Design_v0.1.docx`,
`docs/raw_research/CELL_OS_Master_Research_Design_Development_Operations_User_Guide_v0.2.docx`.
Convert docx with `python scripts/docx_to_md.py <in> <out>` — it works and preserves tables.

⛔ **No Jira ticket exists for this workstream.** It is venture product work, not ALDC client
delivery. The `GP-319` / `gp318` drafts in `boot-prompts/drafts/` belong to other sessions and are
unrelated. Do not attach this to a client ticket.

---

## 2. Paul's steer, 2026-09-03 — verbatim intent

> *"I feel people don't understand the power of it. maybe a comparison of a guy runs a marketing
> agency with regular software and AI tools, vs CELL OS. I would prioritize features concepts
> entities or frameworks that will enable the tool to create autonomous revenue-generating agentic
> businesses/services."*

Two asks, and the second outranks the first.

### 2.1 The comprehension gap, diagnosed

The deck explains *architecture*. Nobody buys architecture. The reason the power does not land is
that every tab answers **"how is it built?"** and none answers **"what changes on Monday?"**

⭐ **The insight the comparison must land, and it is not "faster":** AI tools compress
**production** and leave **coordination and verification** untouched. So verification becomes the
new bottleneck, and quality becomes *unprovable* at volume. Column B is genuinely faster **and less
trustworthy than Column A.** CELL OS's claim is that it moves the constraint rather than tightening
it — the organization becomes the artifact, and proof is a by-product of running.

Second, quieter insight: in A and B the agency's knowledge lives *in Dave*. In C it lives in Cell
Images and HyperMESH. That is the difference between owning a **job** and owning an **asset you can
sell** — and for an agency owner that is the whole argument.

### 2.2 Spec for the comparison tab

Persona: **Dave, 6 staff, 12 retainer clients, ~£45k/mo revenue.** Three columns:

- **A — Regular software.** Asana, Google Sheets, Drive, Canva, GA4, Slack.
- **B — Plus AI tools.** A + ChatGPT, Jasper, Midjourney, Zapier, Gamma.
- **C — CELL OS.**

Rows are jobs-to-be-done, not features. Each cell states **who does it · elapsed time · what breaks
· what evidence survives afterwards**. That fourth field is where C wins and it is the one a
competitor's comparison table never has.

| Job | Why it discriminates |
|---|---|
| Onboard a new client | A/B: tribal setup, 2 weeks. C: compile from an Offer + Counterparty. |
| Monthly reporting × 12 | The volume job. B makes it faster and unverifiable. |
| Content production | B looks strongest here — concede it honestly. |
| Campaign QA before spend | B has no mechanism at all. C refuses at the Kernel. |
| New-business pitch | C can show an Attestation from comparable work. |
| *"Which of last quarter actually worked?"* | ⭐ A and B genuinely cannot answer this. |
| A senior leaves on Friday | A/B lose the knowledge. C does not. |

⚠ **Concede where B wins.** A comparison that has CELL OS winning all seven rows reads as
marketing and gets discounted entirely. Content production and time-to-first-draft should go to B.

---

## 3. ⭐ The priority work — the object model has no money in it

This is the finding worth carrying forward. CELL OS models **cost** (budgets, resource envelopes,
token ceilings) and does not model **revenue, price, customer, or settlement** anywhere. Its object
model is Mission · AI Operative · Worker · Cell · Organism · Federation. An autonomous
revenue-generating business is not expressible in those six nouns.

So it cannot currently *create* a business. It can only staff one someone else defined.

Seven additions, ordered by leverage-per-unit-of-build. **All are `PLANNED` at best — nothing below
exists.**

### E1 · Unit Economics Contract — *highest leverage, smallest build*
A sibling of the Mission Contract, declared **before** the mission runs: price floor, cost ceiling,
target margin, and the evidence required to invoice. The Kernel already checks `budget?` on every
capability call — this makes it check **margin**, and refuse a mission whose projected economics
cannot clear the floor. Reuses the existing gate machinery almost entirely.
> A mission that cannot state its unit economics is a hobby, and the Kernel should say so.

### E2 · Offer — *what the organism sells*
A first-class entity: scope, price, SLA, the **evidence promise**, and a pinned Cell Image that
delivers it. An Offer is a certified Cell Image plus a price plus a promise. This is what turns
"productised service" from a positioning word into a deployable object, and it is the natural unit
for the Blueprint Library to sell.

### E3 · Counterparty — *the customer as a governed object*
Identity, contracts, **data-authority boundary**, payment state, satisfaction evidence. The
authority boundary is the load-bearing part: it is what makes serving twelve clients from one
Organism safe, and it is the thing that will otherwise leak client A's context into client B's
mission.

### E4 · Treasury and Ledger — *Organism-level*
The object model already gives Organism *"capital/resources"* and *"homeostatic targets"* as
configuration. Make them real: revenue in, cost out, margin per Offer, runway, and homeostatic
targets expressed in money. Without this, "autonomous" means "spends without a P&L".

### E5 · Demand Cell — *the missing front end*
Every autonomous business needs qualified pipeline. A formation whose mission is demand, with
**hard policy against unsolicited contact** written into the genome rather than left to judgement.
⚠ This is the entity most likely to embarrass you if shipped without the policy.

### E6 · Settlement capability class — *Kernel extension*
A new capability **class**, not a new adapter: `invoice`, `charge`, `refund`, `payout`. Per-class
caps, per-Counterparty limits, a human gate above a threshold, and an **evidence prerequisite** —
delivery proof must exist before an invoice can be raised. The existing seven-check flow already
has the `evidence prerequisite?` slot; this is what it was for.

### E7 · Deliverable Attestation — *the receipt, pointed outward*
The Mission Assurance Receipt exists internally and every one of its nine sections already has a
producer. Point it at the customer. **You are not selling agent work; you are selling proven agent
work** — and that is the only durable differentiator on this list, because it is the one a
competitor cannot copy without building the evidence layer first.

### F1 · The Business Genome — *the north star*
The framework the other six imply: a versioned, diffable, forkable configuration of an entire
revenue unit — offers, pricing, ICP, channels, delivery Cell Images, treasury policy, authority
ceilings. Fork it. Shadow it. Run a tournament between two pricing models in the Evolution Chamber.
> Cell Genome compiles a team. **Business Genome compiles a company.** That is the product Paul is
> actually describing when he says "autonomous revenue-generating agentic business".

### F2 · Margin-aware Epistemic Scheduler
The scheduler allocates cognitive effort by dependency, risk, cost and uncertainty. Add **expected
value**, so effort routes to where margin is rather than where uncertainty is highest. Cheap to
state, hard to get right, and it is what stops an autonomous business over-investigating a £200 job.

### F3 · The Money Autonomy Ladder
`observe → propose → execute-with-gate → execute-within-cap → autonomous`, held **per capability
class and per Counterparty**. Without an explicit ladder, "autonomous business" is an unbounded
spend risk wearing a product name.

### F4 · Revenue-per-token as a first-class Evolution KPI
Otherwise the Evolution Chamber selects for accuracy and you evolve an expensive perfectionist that
loses money on every mission it wins.

---

## 4. Lower-priority deck features, ranked

1. **"Watch a mission run"** — a scripted replay stepping one mission down through the seven layers,
   showing capability calls allowed and **one refused**. ⭐ Probably the single best comprehension
   device available, and the deck's existing layer data already supports it.
2. **ROI / cost-of-delay calculator** — hours, rate, headcount in; where the money goes out.
   Interactive, and it makes the argument in the reader's own numbers.
3. **The failure gallery** — three real failure modes and how the Kernel catches each. Trust is
   built by showing what goes wrong, not by claiming it does not.
4. **Human org chart vs Cell org chart** for identical output.
5. Merge the previz bay into the deck's Launch Film tab (currently a link — deliberate, see §5).

---

## 5. Gotchas earned

- ⛔ **`str.replace("", new)` prepends at position 0.** `s.index("return out;")` matched the wrong
  function, the slice came back empty, and 24 lines were silently prepended onto
  `scripts/render_check_deck.py`, breaking it. An empty needle does not error — it inserts. Use the
  Edit tool with unique anchors for surgical edits.
- ⛔ **`git log --not --remotes` with no positive ref measures nothing and prints nothing.** It
  reported "0 unpushed" while two commits were genuinely unpushed. Always
  `git log --oneline HEAD --not --remotes` or `--all --not --remotes`. This produced a false clean
  bill of health on a push to a **public** repo.
- **`[hidden]` needs its own CSS rule in an artifact source file.** The publish wrapper supplies
  `[hidden]{display:none!important}`, so a locally-rendered file without a doctype leaks elements
  the published page hides. Own the reset.
- **A rounded score is not a discriminating instrument.** The prototype's overall score landed on
  76 for two different rosters, so the check "score changed" could not distinguish *not computed*
  from *computed and coincidentally equal*. Assert on the component vector.
- **The Playwright MCP browser runs in a container** on `ccx_default`, so `127.0.0.1` is not the
  host. Use `http://host.docker.internal:<port>/`. It works — two earlier sessions wrongly recorded
  rendered validation as unreachable.
- **Hair spaces collapse.** `CELL&#8202;OS` renders as "CELLOS". Use `&nbsp;`.
- **The logo is 566 KB.** Crop to bounding box, resize to 880px, quantize to **256** colours →
  23–26 KB. At 128 colours the blue→violet gradient bands. Script:
  scratchpad `logo_datauri.py`, output injected over a `__LOGO_DATAURI__` placeholder at assemble
  time so the base64 never passes through conversation context.

---

## 6. Regenerate / verify

```bash
python scripts/render_check_deck.py   --shots docs/evidence/cell-os-deck-2026-09-02/
python scripts/render_check_previz.py --shots docs/evidence/cell-os-previz-2026-09-02/
```

Both must print `PASS`. The deck check drives all 7 tabs, opens all 7 architecture layers, and
exercises the prototype (roster → mesh redraw → score recompute → topology density → clear).

⚠ The deck is assembled from 8 part-files in the session scratchpad, which **will not survive**.
`cell-os-deck.html` in the repo is the source of truth from here on — edit it directly.
