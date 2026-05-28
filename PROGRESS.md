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

**`stage1.last.acquire` REDONE — image-reverse-engineered last (v2)**
- v1 ellipse-guess last was poor (user feedback: "extremely shitty"). Replaced with an image-derived method per user's instruction (trace real Oxford photos, reverse-engineer the last).
- Pipeline: `trace_side.py` (OpenCV via `uv`) extracts the top/instep silhouette + featherline from a lateral Derby photo (horizontal-opening to drop shadow corridors, median+mean smoothing); `trace_top.py` extracts the width profile (PCA length axis) from the plan photo; `reconstruct_last.py` lofts cross-sections = **traced top silhouette + traced width + modelled bottom** (featherline plane + heel-seat lift + toe spring; the side featherline trace is unreliable on a glossy dark shoe, and a finished shoe hides the true featherline, so modelling the bottom is correct shoemaking practice).
- Result: watertight, 285×101×97mm, recognizable last (instep hump, toe taper, heel seat) — big improvement. Verified via lateral + ¾ renders.
- Reference photos (H&M, user-provided) are gitignored; only derived `data/profile_side.json` + `data/profile_top.json` committed. Attribution in `docs/REFERENCES.md`.
- Refinement opportunities: rounder toe box, soften heel-seat lip, medial/lateral asymmetry.

**Last v4 — smooth organic last (current).** User rejected the blocky/pointed earlier attempts. Rebuilt properly after researching Blender organic-modeling practice:
- `scripts/reconstruct_last.py`: loft LAST-SHAPED cross-sections (flat featherline bottom + domed asymmetric top from the traced plan left/right edges + convex instep from the traced side top), n-gon end caps (NOT single-vertex poles → no pinching), Catmull-Clark subsurf 2.
- Result: rounded heel, rounded toe box, convex instep, asymmetric plan, watertight. Verified lateral + ¾ + top renders — a legit last.
- Hard-won lessons (in spec note + memory): recalc_face_normals on prisms BEFORE boolean or voxel-remesh yields a hollow shell (signed-volume≈0, renders dark); snapshot.py now uses world ambient + aimed suns so geometry is always visible; round heel/toe in the silhouette not via smoothing.
- Retired scripts: build_last.py (v1 ellipse), reconstruct_last_v3.py (boolean, slab-sided).

**Next**
- Optional polish: fuller toe box, soften featherline edge, stronger medial/lateral asymmetry.
- `stage1.last.condition`: orientation/scale correct by construction; remaining = mark the featherline curve for Stage 2/3.
- `stage2.upper.build`: shrinkwrap a quad upper skin onto LAST, define topline/throat.

**Notes**
- Blender 5.1.2 at `/Applications/Blender.app/Contents/MacOS/Blender`; Inkscape at `/Applications/Inkscape.app/Contents/MacOS/inkscape`.
- Drive live Blender: `python3 scripts/mcp_client.py file <script>` (script sets `result`). Persist via `bpy.ops.wm.save_as_mainfile`; then headless `report`/`snapshot` on `master.blend`.
- To resume after any restart: `./init.sh` (pings MCP + prints next feature), read this file + `git log` + `spec.json`.
