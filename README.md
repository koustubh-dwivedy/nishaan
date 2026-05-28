# Nishaan — Agent-Driven Dress-Shoe Design Pipeline

**Nishaan** (ਨਿਸ਼ਾਨ / निशान — *"the mark you leave"*) is a personalized footwear brand with an
Indian/Punjabi visual identity. This repo is the **reusable pipeline** for designing a custom
**Derby/Oxford dress shoe** — driven by an AI agent (Claude) rather than operated by hand in a GUI.

```
last → 3D upper → styling/panel split → flatten to 2D → cut-ready DXF/SVG → maker assembly
```

## How it works

Claude drives **Blender** through the **official Blender Lab MCP extension** — talking to its live TCP
socket via `scripts/mcp_client.py` (`{type:execute,code,strict_json}` null-byte protocol) — composing a
library of `bpy` scripts. The agent never works blind — every geometry mutation is followed by an
**OBSERVE** step:

- **`scripts/snapshot.py`** — renders the scene from fixed canonical cameras the agent views to judge form.
- **`scripts/report.py`** — emits numeric telemetry (dimensions, distortion, watertightness) to `telemetry/`.

Design proceeds as a loop: `mutate → snapshot + report → evaluate against spec.json → iterate or advance`.

This harness follows Anthropic's
[*Effective harnesses for long-running agents*](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):
an `init.sh` bring-up, a structured `spec.json` feature list with pass/fail gates, `PROGRESS.md`,
and git commit-per-feature as durable cross-session memory.

## Layout

| Path | Purpose |
|---|---|
| `00_last/` | Imported & conditioned shoe last |
| `10_upper/` | Upper surface built on the last |
| `20_panels/` | Split style panels |
| `30_flats/` | Flattened 2D panels |
| `40_exports/` | Cut-ready DXF/SVG/PDF for laser/CNC |
| `50_renders/` | `snapshot()` render output (not versioned) |
| `telemetry/` | `report()` JSON metrics (versioned — the memory) |
| `scripts/` | `bpy` pipeline + telemetry scripts |
| `inspirations/` | Brand research, logo concepts, motifs |
| `init.sh` | Session bring-up + smoke test |
| `spec.json` | Feature list with testable gates |
| `PROGRESS.md` | Cross-session progress log |

## Session ritual

1. `pwd` (confirm directory)
2. Read `PROGRESS.md`, `git log`, `spec.json`
3. `./init.sh` (launch Blender + MCP, smoke test, print state)
4. Pick the **single** highest-priority incomplete feature in `spec.json`
5. Implement → `snapshot` + `report` → verify against the feature's gate
6. Commit + update `PROGRESS.md` + push

See the full plan at `~/.claude/plans/what-happened-bro-i-golden-reef.md`.
