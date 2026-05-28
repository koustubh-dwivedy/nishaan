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

**Next: Stage 1**
- `stage1.last.acquire`: download a Derby/Oxford last (Sketchfab/Cults3D — see plan), import into `master.blend` via `mcp_client.py`, `report`+`snapshot` to confirm.
- `stage1.last.condition`: scale to mm, orient (heel origin/toe +Y/up +Z), fill holes, derive featherline.

**Notes**
- Blender 5.1.2 at `/Applications/Blender.app/Contents/MacOS/Blender`; Inkscape at `/Applications/Inkscape.app/Contents/MacOS/inkscape`.
- Drive live Blender: `python3 scripts/mcp_client.py file <script>` (script sets `result`). Persist via `bpy.ops.wm.save_as_mainfile`; then headless `report`/`snapshot` on `master.blend`.
- To resume after any restart: `./init.sh` (pings MCP + prints next feature), read this file + `git log` + `spec.json`.
