"""snapshot.py — visual telemetry for the Nishaan pipeline.

Renders the current scene from fixed canonical cameras so the agent can SEE what
it built. Run headless:

    blender --background master.blend --python scripts/snapshot.py -- --out 50_renders --tag stage1

Cameras: lateral (+X), medial (-X), top (+Z), three-quarter, sole (-Z).
Engine: Eevee, low samples (fast preview, not final render).
Prints the written image paths (one per line) for the agent to read back.
"""
import bpy, sys, os, math
from mathutils import Vector

def _argv():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []

def _parse():
    a = _argv()
    out = "50_renders"
    tag = "snap"
    if "--out" in a: out = a[a.index("--out") + 1]
    if "--tag" in a: tag = a[a.index("--tag") + 1]
    return out, tag

def scene_bbox():
    """Combined world-space bounding box of all mesh objects."""
    mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
    found = False
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        found = True
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            mins = Vector((min(mins[i], w[i]) for i in range(3)))
            maxs = Vector((max(maxs[i], w[i]) for i in range(3)))
    if not found:
        return Vector((0, 0, 0)), Vector((1, 1, 1))
    return mins, maxs

def setup_engine():
    sc = bpy.context.scene
    for name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = name
            break
        except (TypeError, Exception):
            continue
    sc.render.resolution_x = 900
    sc.render.resolution_y = 600
    sc.render.film_transparent = False

def add_light(loc):
    l = bpy.data.lights.new("snap_sun", "SUN")
    l.energy = 3.0
    o = bpy.data.objects.new("snap_sun", l)
    o.location = loc
    bpy.context.scene.collection.objects.link(o)
    return o

def render_from(name, loc, target, out_dir, tag):
    cam_data = bpy.data.cameras.new(f"snapcam_{name}")
    cam = bpy.data.objects.new(f"snapcam_{name}", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    direction = (target - Vector(loc))
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    path = os.path.abspath(os.path.join(out_dir, f"{tag}_{name}.png"))
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    # cleanup so cameras don't accumulate in the .blend
    bpy.data.objects.remove(cam, do_unlink=True)
    return path

def main():
    out_dir, tag = _parse()
    os.makedirs(out_dir, exist_ok=True)
    mins, maxs = scene_bbox()
    center = (mins + maxs) / 2.0
    size = max((maxs - mins).length, 1.0)
    d = size * 1.6
    add_light(center + Vector((d, -d, d)))
    setup_engine()
    cams = {
        "lateral":      center + Vector((0, -d, 0)),
        "medial":       center + Vector((0,  d, 0)),
        "top":          center + Vector((0,  0, d)),
        "three_quarter":center + Vector((d, -d, d * 0.6)),
        "sole":         center + Vector((0,  0, -d)),
    }
    written = []
    for name, loc in cams.items():
        try:
            written.append(render_from(name, loc, center, out_dir, tag))
        except Exception as e:
            print(f"SNAPSHOT_ERROR {name}: {e}", file=sys.stderr)
    print("SNAPSHOT_RENDERS:")
    for p in written:
        print(p)

if __name__ == "__main__":
    main()
