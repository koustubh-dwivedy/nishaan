# Blender MCP setup

We use the **official Blender Lab MCP extension** (`lab_blender_org/mcp`, ships
for Blender 5.1+), *not* the third-party `ahujasid/blender-mcp`. The harness drives
the running Blender by talking to the extension's TCP socket directly via
`scripts/mcp_client.py` — so it works regardless of whether any MCP tools are
loaded in the current Claude session (keeps the pipeline resumable without restarts).

## One-time enable (GUI)
1. Blender → **Edit → Preferences → Get Extensions / Add-ons** → enable **"MCP"**
   (by Blender Lab). It's already installed at
   `~/Library/Application Support/Blender/5.1/extensions/lab_blender_org/mcp`.
2. In the 3D viewport press **N** → open the **"Blender MCP"** sidebar tab.
3. Click **"Connect to MCP server"** → it shows **"Running on port 9876"**.

Leave Blender running during a session. It does **not** need to be the foreground
app for the official extension (its server is non-blocking on the main thread).

## Protocol (how mcp_client.py talks to it)
- Request : `{"type":"execute","code":<python>,"strict_json":true}` + `\0`
- Response: `{"status":"ok","result":{...},"stdout":...,"stderr":...}` + `\0`
- The `code` must assign a JSON-serializable dict to a variable named `result`.

```bash
python3 scripts/mcp_client.py ping                     # liveness + scene objects
python3 scripts/mcp_client.py code "result = {...}"     # inline
python3 scripts/mcp_client.py file path/to_script.py    # script must set `result`
```

`./init.sh` pings this socket at session start and reports LIVE / not responding.

## Verified
- `ping` returns the live scene; smoke test created+exported a cube and saved `master.blend`;
  headless `report.py`/`snapshot.py` confirmed it (watertight, 20mm, rendered). `harness.mcp` ✅.

> Note: we are NOT using `uvx blender-mcp` (that third-party server speaks a different
> protocol on the same port and was de-registered). Native MCP-tool registration for the
> official server can be revisited later per https://www.blender.org/lab/mcp-server/.
