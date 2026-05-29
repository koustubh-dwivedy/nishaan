"""build_design.py — Derby design on the UPPER + studio render.

Seams are the SHARP rim creases left by the solidify (topline opening + featherline).
Stitches run along them; eyelets sit along the topline loop in the throat; a debossed
Nishaan mark goes on the heel counter. Sun lighting (unit-independent) + auto-framed
camera + leather material. Re-runnable for the critique loop.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

PROJ = "/Users/koustubh/Claude/nishan"
LEATHER = (0.33, 0.09, 0.05, 1); THREAD = (0.88, 0.80, 0.60, 1); METAL = (0.60, 0.47, 0.20, 1)
STITCH_STEP = 5.5; STITCH_R = 0.85; SHARP_DEG = 30.0; N_EYELETS = 5

def clean(p):
    for o in list(bpy.data.objects):
        if o.name.startswith(p): bpy.data.objects.remove(o, do_unlink=True)
def mat(n, c, metallic=0.0, rough=0.5):
    m = bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = c; b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    return m

up = bpy.data.objects["UPPER"]; last = bpy.data.objects["LAST"]
up.data.materials.clear(); up.data.materials.append(mat("leather", LEATHER, 0.0, 0.45))

# ---- sharp edge loops (the seams) ----
bm = bmesh.new(); bm.from_mesh(up.data); bm.normal_update()
thr = math.radians(SHARP_DEG)
sharp = []
for e in bm.edges:
    if len(e.link_faces) == 2:
        a = e.link_faces[0].normal; b = e.link_faces[1].normal
        if a.angle(b) > thr: sharp.append(e)
    elif len(e.link_faces) == 1:
        sharp.append(e)
sset = set(sharp); used = set(); loops = []
emap = {}
for e in sharp:
    emap.setdefault(e.verts[0].index, []).append(e); emap.setdefault(e.verts[1].index, []).append(e)
for s in sharp:
    if s in used: continue
    loop = []; e = s; v = e.verts[0]
    while e and e not in used:
        used.add(e); loop.append(v.co.copy()); nv = e.other_vert(v)
        nxt = [x for x in emap.get(nv.index, []) if x not in used]
        v = nv; e = nxt[0] if nxt else None
    if len(loop) > 6: loops.append(loop)
bm.free()
cen = Vector((0, 142, 45))

# ---- stitches along every seam loop ----
clean("stitch"); sb = bmesh.new()
for loop in loops:
    prev = loop[0]; acc = 0.0; pts = [loop[0]]
    for p in loop[1:]:
        acc += (p - prev).length
        if acc >= STITCH_STEP: pts.append(p); acc = 0.0
        prev = p
    for p in pts:
        out = p + (p - cen).normalized() * 0.4    # sit PROUD of the outer surface (shell is 1.6mm)
        bmesh.ops.create_uvsphere(sb, u_segments=6, v_segments=4, radius=STITCH_R,
                                  matrix=Matrix.Translation(out))
sm = bpy.data.meshes.new("stitchM"); sb.to_mesh(sm); sb.free()
st = bpy.data.objects.new("stitch", sm); bpy.context.scene.collection.objects.link(st)
st.data.materials.append(mat("thread", THREAD, 0, 0.6))
for p in st.data.polygons: p.use_smooth = True

# ---- topline loop = seam loop with most points in throat (rear half, high z) ----
def score(loop):
    return sum(1 for p in loop if p.y < 150 and p.z > 45)
topline = max(loops, key=score) if loops else []
throat = sorted([p for p in topline if 55 < p.y < 130], key=lambda p: p.y)
left = [p for p in throat if p.x < 0]; right = [p for p in throat if p.x > 0]

# ---- eyelets along facing edges ----
clean("eyelet"); eb = bmesh.new()
def pick(row, n):
    if len(row) < 2: return []
    return [row[round(i * (len(row) - 1) / (n - 1))] for i in range(n)]
placed = 0
for row in (left, right):
    for p in pick(row, N_EYELETS):
        nrm = (p - cen); nrm.x *= 1.4; nrm = nrm.normalized()
        loc = p + nrm * 0.5   # sit ON the surface, proud (not buried)
        T = Matrix.Translation(loc) @ nrm.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        bmesh.ops.create_circle(eb, cap_ends=True, segments=14, radius=2.6, matrix=T)
        placed += 1
em = bpy.data.meshes.new("eyeletM"); eb.to_mesh(em); eb.free()
ey = bpy.data.objects.new("eyelet", em); bpy.context.scene.collection.objects.link(ey)
ey.data.materials.append(mat("brass", METAL, 1.0, 0.3))

# ---- heel logo: small debossed disc on the heel counter (raycast back face) ----
clean("logo")
hit, loc, nrm, idx = up.ray_cast(Vector((0, -40, 55)), Vector((0, 1, 0)))
if hit:
    lb = bmesh.new()
    T = Matrix.Translation(loc + nrm * 0.2) @ nrm.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.create_circle(lb, cap_ends=True, segments=24, radius=9, matrix=T)
    lm = bpy.data.meshes.new("logoM"); lb.to_mesh(lm); lb.free()
    lo = bpy.data.objects.new("logo", lm); bpy.context.scene.collection.objects.link(lo)
    lo.data.materials.append(mat("logoMat", (0.20, 0.05, 0.03, 1), 0, 0.3))

# ---- studio: sun lights (unit-independent), ground, auto-framed camera ----
clean("studio_"); sc = bpy.context.scene
if sc.world is None: sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True; sc.world.node_tree.nodes.get("Background").inputs[1].default_value = 0.30
try: sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception: sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'   # truer leather colour (AgX washes it pink)
sc.view_settings.exposure = -1.0
sc.render.resolution_x = 1200; sc.render.resolution_y = 800
gm = bmesh.new(); bmesh.ops.create_grid(gm, x_segments=1, y_segments=1, size=1500,
        matrix=Matrix.Translation((0, 142, -1)))
g = bpy.data.meshes.new("studio_ground"); gm.to_mesh(g); gm.free()
gob = bpy.data.objects.new("studio_ground", g); sc.collection.objects.link(gob)
gob.data.materials.append(mat("studio_floor", (0.20, 0.20, 0.22, 1), 0, 0.8))
def sun(name, loc, energy):
    l = bpy.data.lights.new("studio_" + name, "SUN"); l.energy = energy
    o = bpy.data.objects.new("studio_" + name, l); o.location = loc
    o.rotation_euler = (cen - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(o)
sun("key", (300, -250, 400), 1.5); sun("fill", (-350, -150, 250), 0.5); sun("rim", (-80, 500, 350), 1.0)
last.hide_render = True
# auto-frame
vs = [up.matrix_world @ v.co for v in up.data.vertices]
mn = Vector((min(p.x for p in vs), min(p.y for p in vs), min(p.z for p in vs)))
mx = Vector((max(p.x for p in vs), max(p.y for p in vs), max(p.z for p in vs)))
c = (mn + mx) / 2; size = (mx - mn).length
cam_d = bpy.data.cameras.new("studio_cam"); cam_d.lens = 50
cam = bpy.data.objects.new("studio_cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
def shoot(name, loc, look):
    cam.location = loc; cam.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(PROJ, "50_renders/design_" + name + ".png")
    bpy.ops.render.render(write_still=True)
# hero: front-lateral 3/4 (distance ~1.5x diagonal, like snapshot.py)
shoot("hero", c + Vector((size * 0.9, -size * 0.95, size * 0.65)), c)
# plan: straight above, whole shoe -> verify eyelets + stitches landed
shoot("plan", c + Vector((0, 0.01, size * 1.6)), c)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
result = {"seam_loops": len(loops), "stitches": len(st.data.vertices),
          "eyelets": placed, "throat_L": len(left), "throat_R": len(right)}
