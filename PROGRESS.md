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

**`harness.mcp` ✅ done**
- Discovery: the installed add-on is the **official Blender Lab MCP extension** (`lab_blender_org/mcp`), NOT the third-party `ahujasid/blender-mcp`. They speak different protocols on port 9876.
- De-registered the wrong `uvx blender-mcp` server. We now drive the live Blender directly via `scripts/mcp_client.py` (official protocol: null-byte-delimited `{type:execute,code,strict_json}`).
- Smoke test passed end-to-end: `ping` → live scene; created+exported `SMOKE_CUBE`; saved `master.blend`; headless `report.py` (20mm watertight) + `snapshot.py` (5 renders, viewed) confirmed.
- `master.blend` reset to a **clean template** (0 objects, unit_system NONE → 1 unit == 1 mm).

**Stage 0 COMPLETE.** All four harness features done; repo pushed.

---

## 2026-05-29 — Stage 1: parametric last

**`stage1.last.acquire` ✅ done**
- Research finding: no free, no-login, directly-downloadable *dress* (Derby/Oxford) last exists. Best open last (OpenRun, CC BY-SA 4.0) is athletic + login-gated; only no-login direct downloads are foot scans. Chose **parametric** (FOSS, controllable, dress-appropriate).
- `scripts/build_last.py` lofts elliptical stations (EU42 men's dress) → `LAST` mesh, subsurf-smoothed, saved to `master.blend`. Built via `mcp_client.py` in live Blender.
- Telemetry: **watertight**, L285×W86×H99mm, oriented heel@origin / toe +Y / up +Z. Gate met.
- Observed via `snapshot.py` (fixed cameras for +Y-length convention: lateral/medial/top/heel/toe/3·4/sole). Iterated the station table once (fuller heel, more toe-box volume).
- v1 is geometrically correct but shape is approximate (toe tip tapers thin; mirror-symmetric, real last is medial/lateral asymmetric). Refine `STATIONS` in build_last.py for higher fidelity if desired.

**Next**
- `stage1.last.condition`: largely satisfied by construction (scale/orient correct). Remaining: derive/mark the **featherline** (upper↔sole boundary) explicitly for Stage 2/3.
- Then `stage2.upper.build`: shrinkwrap a quad upper skin onto LAST, define topline/throat.

**Notes**
- Blender 5.1.2 at `/Applications/Blender.app/Contents/MacOS/Blender`; Inkscape at `/Applications/Inkscape.app/Contents/MacOS/inkscape`.
- Drive live Blender: `python3 scripts/mcp_client.py file <script>` (script sets `result`). Persist via `bpy.ops.wm.save_as_mainfile`; then headless `report`/`snapshot` on `master.blend`.
- To resume after any restart: `./init.sh` (pings MCP + prints next feature), read this file + `git log` + `spec.json`.
