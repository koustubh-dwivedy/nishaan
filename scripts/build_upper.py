"""build_upper.py — build the UPPER surface on the LAST (Stage 2).

The lasted upper is the last's outer surface from the featherline (where upper meets
sole) up to the topline (collar + lace throat); the vamp/toe is fully covered.

Method: copy LAST -> UPPER, delete the sole (downward-facing faces) leaving the
featherline boundary, then open the collar/throat (rear region above a topline curve)
leaving the forepart closed. LAST is kept (hidden in render) as the form underneath.

Run:  python3 scripts/mcp_client.py file scripts/build_upper.py
"""
import bpy, bmesh, os

PROJ = "/Users/koustubh/Claude/nishan"
LENGTH = 285.0
VAMP_START_T = 0.46     # forward of this the upper is closed (vamp + toe)
SOLE_NZ = -0.25         # faces with normal.z below this are sole -> removed

def topline_z(t):
    # collar height (mm) from heel(t=0) sweeping up to the throat front
    return 60.0 + (t / VAMP_START_T) * 38.0

last = bpy.data.objects["LAST"]
for o in list(bpy.data.objects):
    if o.name == "UPPER":
        bpy.data.objects.remove(o, do_unlink=True)

up = last.copy(); up.data = last.data.copy()
up.name = "UPPER"; up.data.name = "UPPER"
bpy.context.scene.collection.objects.link(up)

bm = bmesh.new(); bm.from_mesh(up.data); bm.normal_update()
kill = []
for f in bm.faces:
    c = f.calc_center_median()
    if f.normal.z < SOLE_NZ:               # sole / underside -> featherline boundary
        kill.append(f); continue
    t = c.y / LENGTH
    if t < VAMP_START_T and c.z > topline_z(t):   # collar + throat opening
        kill.append(f)
bmesh.ops.delete(bm, geom=kill, context="FACES")
# clean stray loose verts
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
bm.normal_update()
bm.to_mesh(up.data); bm.free(); up.data.update()
for p in up.data.polygons:
    p.use_smooth = True

last.hide_render = True                    # show only the UPPER in renders
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
result = {"upper_verts": len(up.data.vertices), "upper_faces": len(up.data.polygons)}
