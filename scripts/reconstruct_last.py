"""reconstruct_last.py — build the last from the two image-derived profiles.

Reads data/profile_side.json (top/instep + featherline heights) and
data/profile_top.json (half-width), both normalized to length=1.0 (heel t=0, toe t=1).
Each station -> an elliptical cross-section spanning [featherline .. instep] vertically
with the measured half-width; lofted, capped, subdivision-smoothed into a watertight LAST.

Convention: 1 unit == 1 mm, heel at origin, toe +Y, up +Z, width X.
Run inside Blender:  python3 scripts/mcp_client.py file scripts/reconstruct_last.py
"""
import bpy, bmesh, math, json, os
import numpy as np

PROJ = "/Users/koustubh/Claude/nishan"
LENGTH_MM = 285.0      # target last length
RING_SEG = 32
NSTN = 64
MIN_HALF = 1.5         # mm, clamp so end rings don't degenerate
# Last BOTTOM is modelled from shoemaking principles (a finished shoe's sole hides the
# true featherline, and tracing it on a glossy dark shoe is unreliable): a near-flat
# featherline plane with a heel-seat lift at the back and toe spring at the front.
SOLE_TOP_MM = 13.0     # featherline height above the ground in the forepart
HEEL_HEIGHT = 23.0     # extra lift at the very heel (t=0)
HEEL_END_T = 0.20      # heel-seat ramp ends here
TOE_SPRING = 10.0      # lift at the toe tip (t=1)
TOE_START_T = 0.84     # toe spring ramp starts here

side = json.load(open(os.path.join(PROJ, "data/profile_side.json")))
top = json.load(open(os.path.join(PROJ, "data/profile_top.json")))

def arrs(d, key):
    t = np.array([s["t"] for s in d["stations"]], float)
    v = np.array([s[key] for s in d["stations"]], float)
    o = np.argsort(t)
    return t[o], v[o]

ts_top, top_h = arrs(side, "top_h")          # traced instep/top silhouette (the key input)
ts_w, half_w = arrs(top, "half_w")           # traced width

T = np.linspace(0.0, 1.0, NSTN)
top_h_i = np.interp(T, ts_top, top_h) * LENGTH_MM   # height above ground (sole bottom)
half_w_i = np.interp(T, ts_w, half_w) * LENGTH_MM

# modelled last bottom (featherline) height above ground
def bottom_z(t):
    z = SOLE_TOP_MM
    if t < HEEL_END_T:
        z += HEEL_HEIGHT * (HEEL_END_T - t) / HEEL_END_T
    if t > TOE_START_T:
        z += TOE_SPRING * (t - TOE_START_T) / (1.0 - TOE_START_T)
    return z
fth_h_i = np.array([bottom_z(t) for t in T])
top_h_i = np.maximum(top_h_i, fth_h_i + 3.0)   # instep must stay above the featherline

def build():
    for ob in list(bpy.data.objects):
        if ob.name == "LAST":
            bpy.data.objects.remove(ob, do_unlink=True)
    bm = bmesh.new()
    rings = []
    for i in range(NSTN):
        y = T[i] * LENGTH_MM
        cz = (top_h_i[i] + fth_h_i[i]) / 2.0
        hh = max((top_h_i[i] - fth_h_i[i]) / 2.0, MIN_HALF)
        hw = max(half_w_i[i], MIN_HALF)
        ring = []
        for k in range(RING_SEG):
            a = 2.0 * math.pi * k / RING_SEG
            ring.append(bm.verts.new((hw * math.cos(a), y, cz + hh * math.sin(a))))
        rings.append((ring, y, cz))
    for i in range(len(rings) - 1):
        a = rings[i][0]; b = rings[i + 1][0]
        for k in range(RING_SEG):
            k2 = (k + 1) % RING_SEG
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    for (ring, y, cz), flip in ((rings[0], True), (rings[-1], False)):
        c = bm.verts.new((0.0, y, cz))
        for k in range(RING_SEG):
            k2 = (k + 1) % RING_SEG
            bm.faces.new((c, ring[k], ring[k2]) if flip else (c, ring[k2], ring[k]))
    bm.normal_update()
    me = bpy.data.meshes.new("LAST"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("LAST", me)
    bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new("subsurf", "SUBSURF"); mod.levels = mod.render_levels = 2
    for p in me.polygons:
        p.use_smooth = True
    return ob

ob = build()
deps = bpy.context.evaluated_depsgraph_get()
dims = [round(d, 1) for d in ob.evaluated_get(deps).dimensions]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
result = {"object": ob.name, "dims_mm_WxLxH": dims,
          "stations": NSTN, "length_mm": LENGTH_MM,
          "max_half_width_mm": round(float(half_w_i.max()), 1),
          "max_height_mm": round(float((top_h_i - fth_h_i).max()), 1)}
