# Zeus Switchboard — redesign pack

A standalone, no-build operator console for coordinating agent armies. Open `index.html`
directly, or serve the folder with any static server.

```bash
python -m http.server 8080 --directory zeus-switchboard-pack
```

Then open `http://localhost:8080`.

## What is implemented

- Mission queue with health, progress, priority, recency, cost and agent presence.
- Living formation view with explicit resolved, executing and waiting states.
- Synchronized activity, node inspection hooks, pause/resume and focus mode.
- Unified communications for human, agent, squad, mission and broadcast targets.
- Context-linked messages, inline approval, artifact and handoff surfaces.
- Command palette (`Cmd/Ctrl K`) plus `N` deploy, `F` focus and `B` broadcast.
- Mission deployment sheet with formation, budget, gates and success contract.
- Obsidian, Blueprint and Signal themes; compact/comfortable density.
- Local preference persistence, reduced-motion support and JSON config export.
- Responsive desktop/tablet/mobile layouts and keyboard-visible focus states.
- A transport-independent adapter boundary for the current tracker APIs.

All displayed mission data is illustrative because the original tracker source was not
available in the workspace. The UI says this directly in the formation legend.

## Product model

The interface uses a stable hierarchy:

| Level | UI meaning |
| --- | --- |
| Theatre | Entire operating environment or portfolio |
| Campaign | Related objectives across missions |
| Mission | One outcome with budget, contract and gates |
| Formation | Versioned team arrangement for the mission |
| Unit | Team or specialist cell |
| Agent | Individual execution seat |

The theme comes from this operating model and compact insignia—not decorative combat
imagery. This keeps the product credible for engineering and client-facing work.

## Integration order

1. Implement `adapters/SwitchboardAdapter` against the existing tracker snapshot API.
2. Connect its ordered live event stream and replay from the snapshot cursor.
3. Replace the embedded demo arrays in `app.js` with adapter selectors.
4. Route command, approval, pause/resume and create-mission actions to backend policies.
5. Add the existing authentication and permission model to each action and target.
6. Run one real mission and compare every node, state, metric and artifact to source data.

See `adapters/api-contract.md` for the proposed payloads and safety boundaries.

## Files

- `index.html` — semantic application shell and interaction surfaces.
- `styles.css` — full design system, responsive behavior and themes.
- `app.js` — demo state, rendering, keyboard flows and local settings.
- `adapters/switchboard-adapter.js` — transport boundary and event vocabulary.
- `adapters/api-contract.md` — snapshot, event, command and policy contracts.
- `design/design-rationale.md` — decisions, feature priorities and research grounding.

## Browser support

Current Chromium, Firefox and Safari. The core app has no external dependencies or CDN.
Local speech, file export and some animation details can vary by browser.

