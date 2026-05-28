"""reconstruct_last.py — last by lofting LAST-SHAPED cross-sections.

(History: a boolean plan+profile intersection nailed the silhouettes but gave
rectangular, slab-sided sections; an ellipse loft gave a pointed toe. This is the
method that works.) This lofts proper last cross-sections:
  - flat-ish FEATHERLINE bottom (width from the traced plan outline, asymmetric),
  - smoothly DOMED top rising to the traced instep height,
so sides/top are rounded by construction (no slab faces). Ends are capped with
n-gons (NOT single-vertex poles -> no pinching) and the whole thing is Catmull-Clark
subdivided -> a clean organic last.

Convention: 1 unit == 1 mm, heel at origin, toe +Y, up +Z, width X.
Run:  python3 scripts/mcp_client.py file scripts/reconstruct_last.py
"""
import bpy, bmesh, json, os, math
import numpy as np

PROJ = "/Users/koustubh/Claude/nishan"
LENGTH_MM = 285.0
NSTN = 60
T_TOE = 0.965          # stop lofting before the tip; cap -> rounded toe box
N_BOT, N_TOP = 10, 26  # points on the flat bottom and the domed top, per ring
SOLE_TOP_MM, HEEL_HEIGHT, HEEL_END_T, TOE_SPRING, TOE_START_T = 12.0, 22.0, 0.20, 9.0, 0.85
SUBSURF = 2

side = json.load(open(os.path.join(PROJ, "data/profile_side.json")))
top = json.load(open(os.path.join(PROJ, "data/profile_top.json")))

def arr(d, key):
    t = np.array([s["t"] for s in d["stations"]], float)
    v = np.array([s[key] for s in d["stations"]], float)
    o = np.argsort(t); return t[o], v[o]

ts_top, top_h = arr(side, "top_h")
ts_l, left = arr(top, "left")
ts_r, right = arr(top, "right")

def heavy_smooth(y, w=21):
    w = min(w, (len(y)//2)*2+1); p = w//2
    return np.convolve(np.pad(y, p, mode="edge"), np.ones(w)/w, mode="valid")

T = np.linspace(0.0, T_TOE, NSTN)
top_z = heavy_smooth(np.interp(T, ts_top, top_h) * LENGTH_MM, 17)   # convex instep
xL = np.interp(T, ts_l, left) * LENGTH_MM
xR = np.interp(T, ts_r, right) * LENGTH_MM

def bottom_z(t):
    z = SOLE_TOP_MM
    if t < HEEL_END_T: z += HEEL_HEIGHT * (HEEL_END_T - t) / HEEL_END_T
    if t > TOE_START_T: z += TOE_SPRING * (t - TOE_START_T) / (1.0 - TOE_START_T)
    return z
bot_z = np.array([bottom_z(t) for t in T])
top_z = np.maximum(top_z, bot_z + 6.0)

def ring(i):
    """D-section: flat bottom xL->xR at bot_z, domed top arc back xR->xL to top_z."""
    xl, xr, bz, tz = xL[i], xR[i], bot_z[i], top_z[i]
    y = T[i] * LENGTH_MM
    cx, rx = (xl + xr) / 2.0, (xr - xl) / 2.0
    pts = []
    for j in range(N_BOT):                       # bottom (featherline), xL -> xR
        x = xl + (xr - xl) * j / (N_BOT - 1)
        pts.append((x, y, bz))
    for j in range(1, N_TOP):                    # domed top, xR -> xL (exclude dup ends)
        th = math.pi * j / N_TOP
        pts.append((cx + rx * math.cos(th), y, bz + (tz - bz) * math.sin(th)))
    return pts

for ob in list(bpy.data.objects):
    if ob.name == "LAST":
        bpy.data.objects.remove(ob, do_unlink=True)

bm = bmesh.new()
rings = []
for i in range(NSTN):
    rings.append([bm.verts.new(p) for p in ring(i)])
P = len(rings[0])
for i in range(NSTN - 1):
    a, b = rings[i], rings[i + 1]
    for k in range(P):
        k2 = (k + 1) % P
        bm.faces.new((a[k], a[k2], b[k2], b[k]))
bm.faces.new(rings[0][::-1])     # heel cap (n-gon, reversed for outward normal)
bm.faces.new(rings[-1])          # toe cap (n-gon)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("LAST"); bm.to_mesh(me); bm.free()
last = bpy.data.objects.new("LAST", me)
bpy.context.scene.collection.objects.link(last)
ss = last.modifiers.new("subsurf", "SUBSURF"); ss.levels = ss.render_levels = SUBSURF
for p in me.polygons:
    p.use_smooth = True

deps = bpy.context.evaluated_depsgraph_get()
dims = [round(d, 1) for d in last.evaluated_get(deps).dimensions]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
result = {"object": "LAST", "dims_mm_WxLxH": dims, "ring_pts": P, "rings": NSTN}
