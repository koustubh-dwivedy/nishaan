"""import_last.py — import a REAL professional last model and condition it.

Drop a downloaded last file into 00_last/ (glb/gltf/obj/stl/fbx). This imports it,
joins meshes, orients to our convention (length +Y, up +Z, heel at origin), scales
to LENGTH_MM, recalculates normals, shade-smooths, saves master.blend, and reports.

Orientation/heel-toe flip is best-effort; verify with snapshot and adjust the
FLIP_* switches below if needed.

Run:  python3 scripts/mcp_client.py file scripts/import_last.py
"""
import bpy, bmesh, os, glob
from mathutils import Vector

PROJ = "/Users/koustubh/Claude/nishan"
LAST_DIR = os.path.join(PROJ, "00_last")
LENGTH_MM = 285.0
FLIP_Y = False    # set True if heel/toe end up reversed
FLIP_Z = False    # set True if upside-down

def find_file():
    for ext in ("glb", "gltf", "obj", "stl", "fbx", "ply"):
        f = sorted(glob.glob(os.path.join(LAST_DIR, f"*.{ext}")))
        if f:
            return f[0]
    return None

def clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

def import_file(path):
    ext = path.lower().rsplit(".", 1)[-1]
    before = set(bpy.data.objects)
    if ext in ("glb", "gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == "obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == "stl":
        try: bpy.ops.wm.stl_import(filepath=path)
        except Exception: bpy.ops.import_mesh.stl(filepath=path)
    elif ext == "fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == "ply":
        try: bpy.ops.wm.ply_import(filepath=path)
        except Exception: bpy.ops.import_mesh.ply(filepath=path)
    return [o for o in bpy.data.objects if o not in before and o.type == "MESH"]

def main():
    path = find_file()
    if not path:
        return {"error": f"no last file found in {LAST_DIR} (drop a glb/obj/stl there)"}
    clear()
    meshes = import_file(path)
    if not meshes:
        return {"error": f"no mesh imported from {os.path.basename(path)}"}
    # join into one object
    bpy.ops.object.select_all(action="DESELECT")
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "LAST"; ob.data.name = "LAST"
    # apply any import transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # orient: longest axis -> Y (length), next -> X (width), shortest -> Z (height)
    bb = [Vector(c) for c in ob.bound_box]
    dims = ob.dimensions
    order = sorted(range(3), key=lambda i: dims[i], reverse=True)  # [longest, mid, short]
    bm = bmesh.new(); bm.from_mesh(ob.data)
    remap = {order[0]: 1, order[1]: 0, order[2]: 2}   # ->(X=1? ) length->Y, mid->X, short->Z
    for v in bm.verts:
        c = v.co.copy()
        v.co = Vector((c[order[1]], c[order[0]], c[order[2]]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free(); ob.data.update()

    # scale so length (Y) == LENGTH_MM
    d = ob.dimensions
    s = LENGTH_MM / d.y if d.y else 1.0
    ob.scale = (s, s, s)
    bpy.ops.object.transform_apply(scale=True)

    # flips + move heel to origin (min Y -> 0, sit on z: min Z -> 0)
    if FLIP_Y or FLIP_Z:
        bm = bmesh.new(); bm.from_mesh(ob.data)
        for v in bm.verts:
            if FLIP_Y: v.co.y = -v.co.y
            if FLIP_Z: v.co.z = -v.co.z
        if FLIP_Y or FLIP_Z:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(ob.data); bm.free(); ob.data.update()
    # recenter
    mn = Vector((min(v.co.x for v in ob.data.vertices),
                 min(v.co.y for v in ob.data.vertices),
                 min(v.co.z for v in ob.data.vertices)))
    cx = (min(v.co.x for v in ob.data.vertices) + max(v.co.x for v in ob.data.vertices)) / 2
    for v in ob.data.vertices:
        v.co.x -= cx; v.co.y -= mn.y; v.co.z -= mn.z
    ob.data.update()
    for p in ob.data.polygons:
        p.use_smooth = True

    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
    return {"imported": os.path.basename(path),
            "dims_mm_WxLxH": [round(ob.dimensions.x, 1), round(ob.dimensions.y, 1), round(ob.dimensions.z, 1)],
            "verts": len(ob.data.vertices)}

result = main()
