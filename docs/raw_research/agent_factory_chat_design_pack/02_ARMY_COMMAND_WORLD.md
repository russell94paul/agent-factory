# 02 — Army Command World

## Positioning

**Command Console:** precision-first serious Agentic IDE.  
**Battlefield View:** spatial, animated, gamified projection.

Both operate on the same typed domain/event model.

## World hierarchy

Possible world areas:
- Command HQ
- Engineering Command
- Integration Theatre
- Data Theatre
- Product Theatre
- Intelligence Command
- Signal Corps
- Surveillance Command
- Defence / Rules of Engagement
- Training & Evaluation Range
- After-Action Command
- Advanced Projects Command (“Black Site”)
- Doctrine Library
- Intelligence Archive

## Current technical estate → Army-world roles

These are **display identities**, not necessarily repository renames.

| Technical system | Army-world concept |
|---|---|
| zeus-memory | Intelligence Archive / Military Intelligence |
| zeus-chat-exp | Intelligence Command |
| CCE | Engineering Corps |
| clients / Snowflake DWH | Data Command |
| power_bi | Analytics Division |
| eclipse | Legacy Command Post |
| wiki | Doctrine Library |
| connectors | Signal Corps / Integration Command |
| core_api | Core Command Network |
| agent factory | Force Generation Command |
| evaluation | Training & Evaluation Range |
| observability | Surveillance Command |
| governance | Rules of Engagement |
| replay/debugging | After-Action Command |
| autonomous R&D | Advanced Projects Command |

## 10 spatial concepts

1. **Global Operations Map** — replaces portfolio/project navigation.
2. **Operational Theatres** — replaces workspace/app switching.
3. **Front Lines** — replaces priority filters.
4. **Task Forces / Squads** — replaces raw agent/session lists.
5. **Formations** — replaces some DAG/team topology configuration.
6. **Fog of War** — replaces hidden uncertainty metadata.
7. **Supply Lines** — replaces fragmented dependency/context/preflight pages.
8. **Signals Network** — replaces much transcript/Slack/event switching.
9. **Commander's Intent** — replaces disconnected OKR/roadmap context.
10. **After-Action System** — replaces fragmented postmortems and learning capture.

## 10 direct-control features

1. Target Lock
2. Deploy Reinforcements
3. Distress Signal
4. Surveillance Mode
5. Rapid Task Force
6. Recon Mission
7. Breach
8. Hot Drop Specialist
9. Battle Plan
10. Command Override

## Why spatial can be faster

The world can encode context implicitly:

`LOCATION + ZOOM + TARGET + FORMATION + GESTURE = CONTEXT`

Traditional interfaces repeatedly ask:
- which project?
- which mission?
- which team?
- which repo?
- which environment?
- which logs?
- which time range?

In a strong spatial model, those are inherited from where the operator is already focused.
