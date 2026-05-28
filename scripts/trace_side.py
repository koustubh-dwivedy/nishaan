"""trace_side.py — extract the LAST profile from a lateral Oxford photo.

Reverse-engineers the last's longitudinal profile from a clean side-on shoe image:
the upper's TOP edge and the FEATHERLINE (upper<->sole seam). The sole/heel block
below the featherline is NOT part of the last and is excluded.

Run (OpenCV pulled on-demand by uv):
    uv run --with opencv-python-headless --with numpy \
        scripts/trace_side.py references/hm_oxford_1.jpg data/profile_side.json references/_dbg_side.png

Output JSON: stations sampled along the length (heel t=0 -> toe t=1) with normalized
top and featherline heights, plus pixel geometry for scaling. A debug overlay PNG is
written so the trace can be visually verified before it drives geometry.
"""
import cv2, numpy as np, json, sys

img_path, out_json, out_overlay = sys.argv[1], sys.argv[2], sys.argv[3]
N = 80

bgr = cv2.imread(img_path)
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
H, W = gray.shape

# background brightness from the image border
border = np.concatenate([gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]])
bg = int(np.median(border))

# foreground (whole shoe) = clearly darker than background
fg = ((gray < bg - 30).astype(np.uint8)) * 255
k = np.ones((9, 9), np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k, iterations=3)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, k, iterations=2)
cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
c = max(cnts, key=cv2.contourArea)
mask = np.zeros_like(fg)
cv2.drawContours(mask, [c], -1, 255, -1)

# sole/heel = the near-BLACK band at the bottom. Strict threshold so glossy
# dark-brown upper (which is ~50-90 gray) is excluded and only the black sole/heel remains.
DARK = 40
darkmask = ((((gray < DARK).astype(np.uint8)) & (mask > 0)).astype(np.uint8)) * 255
# horizontal opening removes thin VERTICAL dark streaks (throat shadows, stitching,
# eyelets) while keeping the horizontally-continuous sole/heel band intact.
sole = cv2.morphologyEx(darkmask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (41, 1)))
sole = cv2.morphologyEx(sole, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

xs = np.where(mask.sum(axis=0) > 0)[0]
x0, x1 = int(xs.min()), int(xs.max())
length_px = x1 - x0

# featherline = TOP edge of the sole band per column (NaN where no sole -> interpolate)
ts, top_raw, fth_raw = [], [], []
for i in range(N):
    t = i / (N - 1)
    x = min(max(int(round(x0 + t * length_px)), x0), x1)
    col = np.where(mask[:, x] > 0)[0]
    if len(col) == 0:
        continue
    top_y, bot_y = int(col.min()), int(col.max())
    scol = np.where(sole[:, x] > 0)[0]
    feather_y = float(scol.min()) if len(scol) else np.nan
    ts.append(t); top_raw.append(top_y); fth_raw.append(feather_y)

ts = np.array(ts); top_raw = np.array(top_raw, float); fth_raw = np.array(fth_raw, float)
# fill invalid featherline columns by interpolating from valid neighbours
valid = ~np.isnan(fth_raw)
if valid.sum() >= 2:
    fth_raw = np.interp(ts, ts[valid], fth_raw[valid])
base_y = float(mask.shape[0])  # use image bottom as a stable reference for normalization
base_y = float(max(np.where(mask[:, x] > 0)[0].max() for x in
                   [min(max(int(round(x0 + t * length_px)), x0), x1) for t in ts]))

# robust smoothing: median filter kills per-column outliers (arch gaps, dark
# stitching/eyelets bridging up), then a moving average; keeps real features
# (heel-seat rise, toe spring) without polynomial ringing.
def median_filt(y, w=11):
    w = min(w, (len(y) // 2) * 2 + 1); pad = w // 2
    yp = np.pad(y, pad, mode="edge")
    return np.array([np.median(yp[i:i + w]) for i in range(len(y))])
def smooth(y, w=9):
    w = min(w, (len(y) // 2) * 2 + 1); pad = w // 2
    yp = np.pad(y, pad, mode="edge")
    return np.convolve(yp, np.ones(w) / w, mode="valid")
top_s = smooth(median_filt(top_raw, 7), 7)
fth_s = smooth(median_filt(fth_raw, 13), 9)
fth_s = np.maximum(fth_s, top_s + 2)  # featherline must stay below the top profile

stations = []
for t, ty, ts_, fy, fs_ in zip(ts, top_raw, top_s, fth_raw, fth_s):
    stations.append({
        "t": round(float(t), 4),
        "x": min(max(int(round(x0 + t * length_px)), x0), x1),
        "top_y_raw": int(ty), "top_y": int(round(ts_)),
        "feather_y_raw": int(fy), "feather_y": int(round(fs_)),
        "top_h": round((base_y - ts_) / length_px, 4),
        "feather_h": round((base_y - fs_) / length_px, 4),
    })

report = {
    "source": img_path, "view": "lateral",
    "image_wh": [W, H], "shoe_x_range": [x0, x1], "length_px": length_px,
    "base_y": base_y,
    "note": "heights normalized by length_px (length=1.0); heel t=0, toe t=1; curves polyfit-smoothed",
    "stations": stations,
}
with open(out_json, "w") as f:
    json.dump(report, f, indent=2)

# debug overlay: connected polylines (red=top profile, blue=featherline)
ov = bgr.copy()
top_pts = np.array([[s["x"], s["top_y"]] for s in stations], np.int32)
fth_pts = np.array([[s["x"], s["feather_y"]] for s in stations], np.int32)
cv2.polylines(ov, [top_pts], False, (0, 0, 255), 5)
cv2.polylines(ov, [fth_pts], False, (255, 0, 0), 5)
# crop to shoe bbox (+margin) and upscale for clear inspection
ys_all = np.where(mask.sum(axis=1) > 0)[0]
y0, y1 = int(ys_all.min()), int(ys_all.max())
m = 40
crop = ov[max(0, y0 - m):min(H, y1 + m), max(0, x0 - m):min(W, x1 + m)]
scale = 1100.0 / crop.shape[1]
crop = cv2.resize(crop, (1100, int(crop.shape[0] * scale)))
cv2.imwrite(out_overlay, crop)
print(json.dumps({"stations": len(stations), "length_px": length_px,
                  "x_range": [x0, x1], "base_y": int(base_y)}, indent=2))
