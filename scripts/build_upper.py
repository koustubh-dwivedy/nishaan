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
THICKNESS = 1.6         # mm calf leather: the upper's material thickness (the "buffer")

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

# THE BUFFER: give the upper real material thickness offset OUTWARD from the last.
# offset=1.0 -> the original (on-last) surface becomes the INNER face; the leather
# occupies last..last+THICKNESS, so the upper is a distinct 1.6mm layer over the last.
bpy.ops.object.select_all(action="DESELECT")
up.select_set(True); bpy.context.view_layer.objects.active = up
sol = up.modifiers.new("solidify", "SOLIDIFY")
sol.thickness = THICKNESS
sol.offset = 1.0
sol.use_even_offset = True
bpy.ops.object.modifier_apply(modifier="solidify")
# recompute normals outward
bm2 = bmesh.new(); bm2.from_mesh(up.data)
bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces)
bm2.to_mesh(up.data); bm2.free(); up.data.update()
for p in up.data.polygons:
    p.use_smooth = True

last.hide_render = True                    # show only the UPPER in renders by default
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
result = {"upper_verts": len(up.data.vertices), "upper_faces": len(up.data.polygons),
          "thickness_mm": THICKNESS, "note": "upper is a solid 1.6mm shell, inner face on the last"}
