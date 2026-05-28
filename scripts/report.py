"""report.py — numeric telemetry for the Nishaan pipeline.

Emits structured metrics about every mesh object so the agent evaluates its work
against spec.json gates with numbers, not vibes. Run headless:

    blender --background master.blend --python scripts/report.py -- --out telemetry --tag stage1

Per object: world-space dimensions (mm), vert/face/tri counts, surface area,
non-manifold edge count (watertight check), and a scene-level scale note.
Writes telemetry/<tag>.json and prints it to stdout.
"""
import bpy, bmesh, sys, os, json, datetime
from mathutils import Vector

def _argv():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []

def _parse():
    a = _argv()
    out = "telemetry"; tag = "report"
    if "--out" in a: out = a[a.index("--out") + 1]
    if "--tag" in a: tag = a[a.index("--tag") + 1]
    return out, tag

def world_dims(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    xs = [c.x for c in cs]; ys = [c.y for c in cs]; zs = [c.z for c in cs]
    return [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs) - min(zs), 2)]

def mesh_metrics(ob):
    me = ob.to_mesh()
    bm = bmesh.new(); bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    area = round(sum(f.calc_area() for f in bm.faces), 2)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    nverts = len(bm.verts); nfaces = len(bm.faces)
    bm.free(); ob.to_mesh_clear()
    return {
        "verts": nverts, "faces": nfaces, "tris": tris,
        "surface_area_mm2": area,
        "non_manifold_edges": non_manifold,
        "watertight": non_manifold == 0,
    }

def main():
    out_dir, tag = _parse()
    os.makedirs(out_dir, exist_ok=True)
    objects = []
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        m = {"name": ob.name, "dims_mm": world_dims(ob)}
        try:
            m.update(mesh_metrics(ob))
        except Exception as e:
            m["error"] = str(e)
        objects.append(m)
    report = {
        "tag": tag,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "blender_version": bpy.app.version_string,
        "unit_scale": bpy.context.scene.unit_settings.scale_length,
        "object_count": len(objects),
        "objects": objects,
    }
    path = os.path.abspath(os.path.join(out_dir, f"{tag}.json"))
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print("REPORT_JSON:", path)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
