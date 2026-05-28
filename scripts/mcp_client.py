"""mcp_client.py — direct socket bridge to Blender's OFFICIAL MCP add-on.

The official Blender Lab MCP extension (lab_blender_org/mcp) runs a non-blocking
TCP socket server inside Blender (default localhost:9876). Protocol:

  request : {"type":"execute","code":<python>,"strict_json":true}  + b"\\0"
  response: {"status":"ok","result":{...},"stdout":...,"stderr":...} + b"\\0"

The executed `code` MUST assign a JSON-serializable dict to a variable named
`result`; that dict comes back under response["result"].

Talking to this socket directly lets the harness drive the *live* Blender from
the shell regardless of whether MCP tools are loaded in the Claude session —
which keeps the pipeline resumable without restarts.

Usage:
    python3 scripts/mcp_client.py ping
    python3 scripts/mcp_client.py code "result = {'v': __import__('bpy').app.version_string}"
    python3 scripts/mcp_client.py file path/to_script.py     # script must set `result`
"""
import socket, json, sys

HOST, PORT = "localhost", 9876

def execute(code, strict_json=True, timeout=120):
    req = json.dumps({"type": "execute", "code": code, "strict_json": strict_json})
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    s.sendall(req.encode("utf-8") + b"\0")
    buf = bytearray()
    try:
        while b"\0" not in buf:
            chunk = s.recv(8192)
            if not chunk:
                break
            buf.extend(chunk)
    finally:
        s.close()
    payload = bytes(buf[:buf.index(b"\0")]) if b"\0" in buf else bytes(buf)
    return json.loads(payload.decode("utf-8"))

PING = "import bpy; result = {'version': bpy.app.version_string, 'objects': [o.name for o in bpy.data.objects]}"

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    mode = sys.argv[1]
    if mode == "ping":
        resp = execute(PING)
    elif mode == "code":
        resp = execute(sys.argv[2])
    elif mode == "file":
        with open(sys.argv[2]) as f:
            resp = execute(f.read())
    else:
        print(__doc__); sys.exit(2)
    print(json.dumps(resp, indent=2))
    sys.exit(0 if resp.get("status") == "ok" else 1)

if __name__ == "__main__":
    main()
