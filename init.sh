#!/usr/bin/env bash
# init.sh — Nishaan pipeline session bring-up.
# Run at the START of every session. Confirms the environment is healthy before
# any design work (guards against environment degradation), then prints state.
set -uo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
echo "== Nishaan harness bring-up =="
echo "PWD: $ROOT"

# --- locate Blender ---
BLENDER=""
for c in "/Applications/Blender.app/Contents/MacOS/Blender" "$(command -v blender 2>/dev/null)"; do
  if [ -n "$c" ] && [ -x "$c" ]; then BLENDER="$c"; break; fi
done
if [ -z "$BLENDER" ]; then
  echo "FAIL: Blender not found. Install: brew install --cask blender"; exit 1
fi
echo "Blender: $BLENDER"
"$BLENDER" --version | head -1

# --- locate Inkscape (non-fatal) ---
if [ -x "/Applications/Inkscape.app/Contents/MacOS/inkscape" ]; then
  echo "Inkscape: /Applications/Inkscape.app/Contents/MacOS/inkscape"
elif command -v inkscape >/dev/null 2>&1; then
  echo "Inkscape: $(command -v inkscape)"
else
  echo "WARN: Inkscape not found (needed at Stage 5)."
fi

# --- live Blender MCP socket (official lab_blender_org/mcp extension) ---
# Non-fatal: the headless pipeline works without it, but live-driving needs it.
if python3 scripts/mcp_client.py ping >/dev/null 2>&1; then
  echo "Blender MCP socket: LIVE (localhost:9876) — can drive the running Blender."
else
  echo "Blender MCP socket: not responding. Open Blender, enable the MCP add-on,"
  echo "  click 'Connect to MCP server' (port 9876). See docs/SETUP_MCP.md."
fi

# --- master .blend (created once MCP is wired) ---
MASTER="$ROOT/master.blend"
if [ -f "$MASTER" ]; then
  echo "Master scene: $MASTER"
  echo "-- telemetry on master --"
  "$BLENDER" --background "$MASTER" --python "$ROOT/scripts/report.py" -- --out telemetry --tag init 2>/dev/null \
    | sed -n '/REPORT_JSON:/,$p' | head -40
else
  echo "Master scene: (none yet — created during harness.mcp feature)"
  echo "-- smoke test: Blender can run bpy headless --"
  "$BLENDER" --background --python-expr "import bpy; print('BPY_OK', bpy.app.version_string)" 2>/dev/null \
    | grep BPY_OK || { echo "FAIL: bpy smoke test"; exit 1; }
fi

# --- state for the agent ---
echo "== State =="
echo "-- next incomplete features (spec.json) --"
python3 - <<'PY'
import json
try:
    s = json.load(open("spec.json"))
    todo = [f for f in s["features"] if not f.get("done")]
    for f in todo[:3]:
        print(f"  [ ] {f['id']}: {f['desc']}")
    print(f"  ({len(todo)} incomplete / {len(s['features'])} total)")
except Exception as e:
    print("  spec.json unreadable:", e)
PY
echo "-- recent commits --"
git log --oneline -5 2>/dev/null || echo "  (no git history yet)"
echo "== Ready. Read PROGRESS.md, then work the top incomplete feature. =="
