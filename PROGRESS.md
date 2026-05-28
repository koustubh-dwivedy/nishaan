# Progress Log

Newest entries on top. Read this + `git log` + `spec.json` at the start of every session.

---

## 2026-05-29 — Stage 0: harness bring-up

**Done**
- Created project folder structure (`00_last` … `50_renders`, `telemetry`, `scripts`).
- Scaffolded harness: `init.sh`, `spec.json` (feature list), `snapshot.py` + `report.py` telemetry scripts, `README.md`, `.gitignore`.
- Initialized git, baseline commit, created public GitHub repo, pushed.
- Blender + Inkscape installed via Homebrew.

**Environment**
- Blender: installed (verify path in `init.sh`).
- Inkscape: installed.
- BlenderMCP: _pending — install addon + register MCP server in Claude Code, then run smoke test._

**Next**
- `harness.mcp` feature: install BlenderMCP addon, register MCP server, pass the smoke test (`snapshot`/`report` produce a render + telemetry JSON).
- Then `stage1.last.acquire`: download a Derby/Oxford last and condition it.

**Open questions / notes**
- Confirm Blender CLI path on this machine for `init.sh` (`/Applications/Blender.app/Contents/MacOS/Blender`).
