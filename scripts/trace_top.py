"""trace_top.py — extract the last's WIDTH profile from a top (plan) Oxford photo.

Isolates one shoe, finds its length axis via PCA, and measures half-width at each
station along the length. Combined with the side profile (trace_side.py) this gives
full cross-sections for reconstructing the last.

Run:
    uv run --with opencv-python-headless --with numpy \
        scripts/trace_top.py references/hm_oxford_2.jpg data/profile_top.json references/_dbg_top.png
"""
import cv2, numpy as np, json, sys

img_path, out_json, out_overlay = sys.argv[1], sys.argv[2], sys.argv[3]
M = 80

bgr = cv2.imread(img_path)
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
H, W = gray.shape
border = np.concatenate([gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]])
bg = int(np.median(border))
fg = ((gray < bg - 30).astype(np.uint8)) * 255
k = np.ones((9, 9), np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k, iterations=3)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, k, iterations=2)
cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
c = cnts[0]                                   # largest = one shoe
mask = np.zeros_like(fg); cv2.drawContours(mask, [c], -1, 255, -1)

ys, xs = np.where(mask > 0)
pts = np.column_stack([xs, ys]).astype(np.float64)
mean = pts.mean(axis=0)
cov = np.cov((pts - mean).T)
evals, evecs = np.linalg.eigh(cov)
axis_len = evecs[:, np.argmax(evals)]         # principal (length) direction
axis_wid = evecs[:, np.argmin(evals)]
L = (pts - mean) @ axis_len                   # length coord
Wd = (pts - mean) @ axis_wid                  # width coord
lmin, lmax = L.min(), L.max()
length_px = lmax - lmin

# width at each length bin
bins = np.linspace(lmin, lmax, M + 1)
raw_t, raw_hw, centers = [], [], []
for i in range(M):
    sel = (L >= bins[i]) & (L < bins[i + 1])
    if sel.sum() < 5:
        continue
    w = Wd[sel]
    raw_t.append(((bins[i] + bins[i + 1]) / 2 - lmin) / length_px)
    raw_hw.append((w.max() - w.min()) / 2.0)
    centers.append((w.max() + w.min()) / 2.0)
raw_t = np.array(raw_t); raw_hw = np.array(raw_hw, float)

# wider end = heel -> ensure t=0 is heel
if raw_hw[:len(raw_hw)//3].mean() < raw_hw[-len(raw_hw)//3:].mean():
    raw_t = 1.0 - raw_t[::-1]; raw_hw = raw_hw[::-1]; centers = centers[::-1]

hw_s = np.polyval(np.polyfit(raw_t, raw_hw, 7), raw_t)   # smooth
stations = [{"t": round(float(t), 4), "half_w": round(float(hw / length_px), 4)}
            for t, hw in zip(raw_t, hw_s)]
report = {"source": img_path, "view": "top", "length_px": float(length_px),
          "note": "half-width as fraction of length; heel t=0, toe t=1, smoothed",
          "stations": stations}
with open(out_json, "w") as f:
    json.dump(report, f, indent=2)

# overlay: contour + width segments (reconstruct endpoints in image space)
ov = bgr.copy()
cv2.drawContours(ov, [c], -1, (0, 180, 0), 3)
for i in range(M):
    sel = (L >= bins[i]) & (L < bins[i + 1])
    if sel.sum() < 5:
        continue
    lc = (bins[i] + bins[i + 1]) / 2
    w = Wd[sel]
    p1 = mean + axis_len * lc + axis_wid * w.min()
    p2 = mean + axis_len * lc + axis_wid * w.max()
    cv2.line(ov, tuple(p1.astype(int)), tuple(p2.astype(int)), (0, 0, 255), 2)
x0, y0, ww, hh = cv2.boundingRect(c)
m = 40
crop = ov[max(0, y0-m):min(H, y0+hh+m), max(0, x0-m):min(W, x0+ww+m)]
sc = 900.0 / crop.shape[1]
cv2.imwrite(out_overlay, cv2.resize(crop, (900, int(crop.shape[0]*sc))))
print(json.dumps({"stations": len(stations), "length_px": round(float(length_px), 1)}, indent=2))
