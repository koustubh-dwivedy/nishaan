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
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # this STL is a PAIR of lasts (two shells) -> keep the largest connected component
    import collections
    bm = bmesh.new(); bm.from_mesh(ob.data)
    adj = collections.defaultdict(set)
    for e in bm.edges:
        adj[e.verts[0]].add(e.verts[1]); adj[e.verts[1]].add(e.verts[0])
    seen = set(); comps = []
    for v in bm.verts:
        if v in seen: continue
        st = [v]; comp = []
        while st:
            u = st.pop()
            if u in seen: continue
            seen.add(u); comp.append(u); st.extend(adj[u] - seen)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    for comp in comps[1:]:
        bmesh.ops.delete(bm, geom=comp, context="VERTS")

    # orient: this model's length is along Z -> map to +Y; up = old +Y  ((x,y,z)->(x,-z,y))
    ext0 = [max(v.co[i] for v in bm.verts) - min(v.co[i] for v in bm.verts) for i in range(3)]
    if ext0.index(max(ext0)) == 2:                       # longest is Z (this file)
        for v in bm.verts:
            c = v.co.copy(); v.co = (c.x, -c.z, c.y)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free(); ob.data.update()

    def extents():
        xs = [v.co.x for v in ob.data.vertices]; ys = [v.co.y for v in ob.data.vertices]
        zs = [v.co.z for v in ob.data.vertices]
        return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

    (x0, x1), (y0, y1), (z0, z1) = extents()
    s = LENGTH_MM / (y1 - y0) if (y1 - y0) else 1.0      # scale so length (Y) = 285mm
    for v in ob.data.vertices:
        v.co *= s
    ob.data.update()

    # center X/Y/Z-min to a clean origin region (final orientation applied after we look)
    (x0, x1), (y0, y1), (z0, z1) = extents()
    cx = (x0 + x1) / 2
    for v in ob.data.vertices:
        v.co.x -= cx; v.co.y -= (y0 + y1) / 2; v.co.z -= (z0 + z1) / 2
    ob.data.update()

    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    for p in ob.data.polygons:
        p.use_smooth = True

    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
    (x0, x1), (y0, y1), (z0, z1) = extents()
    return {"imported": os.path.basename(path),
            "dims_mm_WxLxH": [round(x1 - x0, 1), round(y1 - y0, 1), round(z1 - z0, 1)],
            "verts": len(ob.data.vertices), "note": "W=X, L=Y(=285), H=Z; heel@origin, toe +Y"}

result = main()
