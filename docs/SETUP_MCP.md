# BlenderMCP setup (one-time, manual GUI steps)

The MCP server (`uvx blender-mcp`) is already registered with Claude Code
(`claude mcp add blender -- uvx blender-mcp`). Two steps remain that require the
Blender GUI and can't be automated:

## 1. Install + enable the addon
1. Download the addon (already vendored locally at `vendor/blendermcp_addon.py`;
   source: https://github.com/ahujasid/blender-mcp , MIT).
2. Open **Blender → Edit → Preferences → Add-ons → Install…**
3. Select `vendor/blendermcp_addon.py`.
4. Tick the box next to **"Interface: Blender MCP"** to enable it.

## 2. Start the addon's server
1. In the 3D viewport, press **N** to open the sidebar.
2. On the right edge, open the **"BlenderMCP"** tab (scroll the vertical tab strip if needed).
3. At the bottom of the panel, click **"Connect to MCP server"**.
   - NOTE: older docs call this "Connect to Claude" — in the current addon the
     button text is **"Connect to MCP server"**.
4. It should change to **"Disconnect from MCP server"** + **"Running on port 9876"** = live.
   (Leave Poly Haven / Hyper3D / Sketchfab / Hunyuan options off — not needed.)

Leave this Blender instance running during any pipeline session — the MCP server
talks to Blender over a local socket (default port 9876) that this addon opens.

## 3. Verify (next Claude Code session)
Newly-registered MCP tools load at session start, so open a **fresh** session, then:
- Ask Claude to create a cube and export it via the Blender MCP tools.
- Run `snapshot.py` / `report.py` and confirm the render + telemetry JSON.

That passes the `harness.mcp` gate in `spec.json`.

> Source attribution: BlenderMCP by ahujasid (MIT). A richer alternative with
> arbitrary `bpy` script execution + async jobs: github.com/djeada/blender-mcp-server.
