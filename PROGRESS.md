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

**Last — REAL professional model (current/canonical).** User rejected all procedural attempts ("exceptionally perfect" required); procedural-from-shoe-photos has a real quality ceiling. Switched to a real last:
- User downloaded `MALE LAST SIZE 9.stl` into `00_last/` (a L/R pair of lasts).
- `scripts/import_last.py`: import → keep largest connected component (one last) → orient (length Z→+Y, up +Z, heel@origin) → scale length=285mm → recalc normals → save master.blend.
- Result: single watertight last, 100×285×101mm, genuine professional geometry (cone, instep, featherline, toe spring). Verified lateral + ¾ + report.
- Raw STL gitignored (provenance/licence varies, 3MB binary); master.blend (conditioned scene) committed. **Provenance flagged to user** — if the model's licence restricts redistribution, swap to the confirmed CC-BY Sketchfab "Foot Form / Shoe Last".
- Procedural scripts retained but superseded as the last source.

**Stage 2 — upper surface (v1, in progress).**
- `scripts/build_upper.py`: copy LAST → UPPER, delete sole (downward-facing faces → featherline boundary), cut collar/throat opening (rear region above a topline curve; vamp/toe stays closed). LAST kept but `hide_render=True`.
- Verified via contrasting-material top render: collar/throat opening is cut in the rear/instep, vamp/toe closed, upper conforms to last.
- v1 topline shape is a crude heuristic (linear `topline_z(t)`); needs refinement to a real Derby topline (collar height at heel, throat V at the facings).

**User feedback (important):** what I'd called the "upper" was just the trimmed last surface — coincident with the last, NO buffer, NO design, NO logo/stitches/patterns. Corrected the framing. Design decisions captured: **Plain Derby**, **logo on heel counter**, **brogue + mojari/phulkari motifs**, **1.6mm calf**.

**Buffer DONE:** `build_upper.py` now solidifies the upper 1.6mm OUTWARD (offset=1.0) → a real leather-thickness layer whose inner face is on the last. Verified: approx thickness 1.57mm; upper width 103.4 vs last 100.2 (1.6mm proud each side). 25 stray non-manifold rim edges to clean during paneling.

**Still TODO for a real upper (in order):**
1. Refine Derby topline (collar height + throat V at facings); add lasting allowance at featherline.
2. `stage3.panels.split`: Derby panels — vamp, quarters, facings/eyestay (eyelets), tongue, heel counter — as real pieces/seams.
3. Stitching: seam stitch lines.
4. Logo: Nishaan Aankra mark debossed on the heel counter (from inspirations/nishaan_logos.svg).
5. Motifs: brogue perforations + mojari/phulkari/morpankh patterns on cap/facings (from inspirations/*.svg).

**Stage 3 design attempt (scripts/build_design.py) — HONEST status.**
- Built: stitch beads following the sharp-edge seam loops, 10 eyelets along the throat, a heel-logo disc, leather material + sun-studio render rig.
- Works: featherline stitching renders correctly (clay ¾). Buffer + last are solid.
- Does NOT work yet: throat/topline stitching + eyelets face away/need refinement; leather colour over-exposes (oxblood→orange under Standard transform); brogue + real logo not done.
- **Conclusion (honest):** blind scripted detailing + render-and-look does NOT converge to high quality — compounding issues (buried elements vs 1.6mm shell, self-shadowed throat, exposure, framing) each cost a render iteration. Same ceiling as the procedural last. A finished/photoreal designed shoe is a 3D-artist task done INTERACTIVELY in Blender's viewport (BlenderMCP supports guided live work), or the project should lean on its real strength: the manufacturing pipeline (panels→flatten→cut patterns, design as precise 2D lines). Awaiting user direction.

**Notes**
- Blender 5.1.2 at `/Applications/Blender.app/Contents/MacOS/Blender`; Inkscape at `/Applications/Inkscape.app/Contents/MacOS/inkscape`.
- Drive live Blender: `python3 scripts/mcp_client.py file <script>` (script sets `result`). Persist via `bpy.ops.wm.save_as_mainfile`; then headless `report`/`snapshot` on `master.blend`.
- To resume after any restart: `./init.sh` (pings MCP + prints next feature), read this file + `git log` + `spec.json`.
