# Progress Log

Newest entries on top. Read this + `git log` + `spec.json` at the start of every session.

---

## 2026-05-29 — Stage 0: harness bring-up

**Done**
- Created project folder structure (`00_last` … `50_renders`, `telemetry`, `scripts`).
- Scaffolded harness: `init.sh`, `spec.json` (feature list), `snapshot.py` + `report.py` telemetry scripts, `README.md`, `.gitignore`.
- Initialized git, baseline commit, created public GitHub repo, pushed.
- Blender + Inkscape installed via Homebrew.

**Verified**
- `harness.env` ✅ — Blender 5.1.2 + Inkscape installed; `./init.sh` runs clean (bpy headless smoke test passes).
- `harness.telemetry` ✅ — `report.py` emits valid JSON (cube watertight, dims), `snapshot.py` renders all 5 canonical views; agent confirmed it can view a render.
- `harness.repo` ✅ — public repo pushed: https://github.com/koustubh-dwivedy/nishaan

**Environment**
- Blender: `/Applications/Blender.app/Contents/MacOS/Blender` (5.1.2).
- Inkscape: `/Applications/Inkscape.app/Contents/MacOS/inkscape`.
- BlenderMCP: _pending — install addon + register MCP server in Claude Code, then run the cube smoke test over MCP._

**`harness.mcp` — in progress (blocked on a manual GUI step)**
- ✅ MCP server registered: `claude mcp add blender -- uvx blender-mcp` (local config); `claude mcp list` shows `blender ✓ Connected`.
- ✅ Addon fetched: `vendor/blendermcp_addon.py` (gitignored; MIT, ahujasid/blender-mcp).
- ⏳ **Manual (you):** install + enable the addon in Blender, click "Connect to Claude". See `docs/SETUP_MCP.md`.
- ⏳ **Next session:** new MCP tools load at session start → run the cube-over-MCP smoke test to pass the `harness.mcp` gate.

**Next after MCP**
- `stage1.last.acquire`: download a Derby/Oxford last and import it; `stage1.last.condition`: scale/orient/clean.

**Notes**
- Blender 5.1.2 at `/Applications/Blender.app/Contents/MacOS/Blender`; Inkscape at `/Applications/Inkscape.app/Contents/MacOS/inkscape`.
- Telemetry scripts verified on a primitive (cube): watertight, dims, 5 canonical renders.
