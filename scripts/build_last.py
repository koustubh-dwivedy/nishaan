"""build_last.py — parametric Derby/Oxford shoe last (run inside Blender via MCP).

No free, openly-licensed, directly-downloadable *dress* last exists, so we build
one from standard last measurements. Convention: 1 blender unit == 1 mm, heel at
origin, toe +Y, up +Z, width along X.

The last is a lofted tube of elliptical cross-sections ("stations") along the
length, with a raised heel seat and toe spring built into the bottom (sole) line,
capped at both ends and smoothed with subdivision -> a closed, watertight solid.

This is a FIRST parametric pass (EU42 men's dress); the harness OBSERVES it
(snapshot + report) and iterates the station table toward a truer last shape.

Run:  python3 scripts/mcp_client.py file scripts/build_last.py
"""
import bpy, bmesh, math, os

PROJ = "/Users/koustubh/Claude/nishan"

# EU42 men's dress last, approximate. Each station:
#   t        : 0 = heel end, 1 = toe tip
#   half_w   : semi-width  (X, medial-lateral), mm
#   bottom_z : sole line height (mm)  -> heel seat raised, dips to 0 at ball, rises at toe (toe spring)
#   top_z    : top of last cone (mm)
LENGTH = 285.0            # last length incl. toe allowance (foot ~268mm)
RING_SEGMENTS = 28
STATIONS = [
    # t,    half_w, bottom_z, top_z
    (0.00,   16.0,   28.0,    62.0),   # heel end (blunt, rounded, raised heel seat)
    (0.05,   22.0,   24.0,    74.0),
    (0.13,   27.0,   14.0,    90.0),
    (0.25,   30.0,    5.0,    99.0),   # instep peak
    (0.38,   31.0,    1.0,    92.0),   # waist
    (0.50,   37.0,    0.0,    80.0),   # flat load-bearing sole begins
    (0.60,   43.0,    0.0,    72.0),   # ball / joint (widest)
    (0.70,   42.0,    0.5,    62.0),
    (0.80,   38.0,    2.0,    52.0),   # toe box keeps volume
    (0.88,   33.0,    5.0,    44.0),
    (0.94,   26.0,    9.0,    36.0),   # toe spring lifting
    (0.985,  17.0,   13.0,    30.0),   # rounded toe (not collapsed)
    (1.00,    7.0,   15.0,    26.0),   # small rounded toe tip
]

def station_geo(s):
    t, half_w, bottom_z, top_z = s
    y = t * LENGTH
    z_center = (top_z + bottom_z) / 2.0
    half_h = (top_z - bottom_z) / 2.0
    return y, half_w, half_h, z_center

def build():
    # remove any prior LAST
    for ob in list(bpy.data.objects):
        if ob.name == "LAST":
            bpy.data.objects.remove(ob, do_unlink=True)

    bm = bmesh.new()
    rings = []
    for s in STATIONS:
        y, half_w, half_h, z_center = station_geo(s)
        ring = []
        for k in range(RING_SEGMENTS):
            ang = 2.0 * math.pi * k / RING_SEGMENTS
            x = half_w * math.cos(ang)
            z = z_center + half_h * math.sin(ang)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)

    # connect consecutive rings with quads
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(RING_SEGMENTS):
            k2 = (k + 1) % RING_SEGMENTS
            bm.faces.new((a[k], a[k2], b[k2], b[k]))

    # cap heel (ring 0) and toe (last ring) with center-fan
    for ring, s, flip in ((rings[0], STATIONS[0], True), (rings[-1], STATIONS[-1], False)):
        y, _, _, z_center = station_geo(s)
        c = bm.verts.new((0.0, y, z_center))
        for k in range(RING_SEGMENTS):
            k2 = (k + 1) % RING_SEGMENTS
            f = (c, ring[k], ring[k2]) if flip else (c, ring[k2], ring[k])
            bm.faces.new(f)

    bm.normal_update()
    me = bpy.data.meshes.new("LAST")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("LAST", me)
    bpy.context.scene.collection.objects.link(ob)

    # smooth: subdivision surface + shade smooth
    mod = ob.modifiers.new("subsurf", "SUBSURF")
    mod.levels = mod.render_levels = 2
    for p in me.polygons:
        p.use_smooth = True

    return ob

def main():
    ob = build()
    # evaluate post-modifier dimensions
    deps = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(deps)
    dims = [round(d, 2) for d in ev.dimensions]
    os.makedirs(PROJ, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PROJ, "master.blend"))
    return {
        "object": ob.name,
        "dims_mm_LxWxH": [dims[1], dims[0], dims[2]],
        "target_length_mm": LENGTH,
        "stations": len(STATIONS),
        "saved": True,
    }

result = main()
