#!/usr/bin/env python3
"""Render the SynapseOS "Twin Hook" laser-engrave boot animation for Plymouth.

    render_frames.py OUTDIR ACCENT_HEX

Writes OUTDIR/frame-000.png ... (opaque, palette PNGs on the splash background),
OUTDIR/final.png (hold state) and OUTDIR/glow.png (RGBA bloom the script breathes).

Choreography (seconds): 0 ignite at opposite terminals, 0.35-2.0 twin contour cut
in mirror sync, 2.0-2.75 raster hatch, 2.72-3.05 arc jumps the kerf, 3.05 power-on
pulse + ring, 3.15-4.1 wordmark engraved letter by letter, 4.7 hold.
"""

import math
import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FPS = 25
END = 4.7
W, H = 600, 560          # frame size at 1080p; the script scales for other heights
SS = 2                   # supersampling
BG = (9, 9, 13)
WARM = (255, 196, 140)
TEXT = (205, 214, 244)

# Emblem: two identical chamfered hooks (200x200 design units), the second rotated 180deg.
HOOK_A = [(170, 20), (162, 48), (72, 48), (58, 62), (58, 86), (98, 86), (90, 114), (50, 114), (30, 94), (30, 40), (50, 20), (170, 20)]
HOOK_B = [(200 - x, 200 - y) for x, y in HOOK_A]
HATCH_Y = list(range(22, 179, 4))
# Wordmark "SYNAPSE" (564x80 units incl. margins), monoline chamfered letters.
WORD = [
    [(56, 0), (8, 0), (0, 8), (0, 12), (8, 20), (48, 20), (56, 28), (56, 32), (48, 40), (0, 40)],
    [(78, 0), (106, 22), (106, 40)], [(134, 0), (106, 22)],
    [(156, 40), (156, 0), (212, 40), (212, 0)],
    [(234, 40), (234, 12), (246, 0), (278, 0), (290, 12), (290, 40)], [(234, 26), (290, 26)],
    [(312, 40), (312, 0), (360, 0), (368, 8), (368, 18), (360, 26), (312, 26)],
    [(446, 0), (398, 0), (390, 8), (390, 12), (398, 20), (438, 20), (446, 28), (446, 32), (438, 40), (390, 40)],
    [(524, 0), (468, 0), (468, 40), (524, 40)], [(468, 20), (510, 20)],
]

EM_SCALE = 1.6                                   # px per emblem unit
EM_OX, EM_OY = (W - 200 * EM_SCALE) / 2, 30      # emblem origin
WD_SCALE = 0.8
WD_OX, WD_OY = (W - 524 * WD_SCALE) / 2, 438


def em(p):
    return ((EM_OX + p[0] * EM_SCALE) * SS, (EM_OY + p[1] * EM_SCALE) * SS)


def wd(p):
    return ((WD_OX + p[0] * WD_SCALE) * SS, (WD_OY + p[1] * WD_SCALE) * SS)


def ease(k):
    k = min(1.0, max(0.0, k))
    return 4 * k ** 3 if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def seg(t, t0, dur):
    return min(1.0, max(0.0, (t - t0) / dur))


class Poly:
    """Polyline with arc-length lookup."""

    def __init__(self, pts):
        self.pts = pts
        self.cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            self.cum.append(self.cum[-1] + math.dist(a, b))
        self.length = self.cum[-1]

    def point(self, d):
        d = min(max(d, 0.0), self.length)
        for i in range(1, len(self.cum)):
            if d <= self.cum[i]:
                a, b = self.pts[i - 1], self.pts[i]
                k = (d - self.cum[i - 1]) / max(self.cum[i] - self.cum[i - 1], 1e-9)
                return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        return self.pts[-1]

    def sub(self, d0, d1):
        d0, d1 = max(d0, 0.0), min(d1, self.length)
        if d1 <= d0:
            return []
        out = [self.point(d0)]
        out += [p for p, c in zip(self.pts, self.cum) if d0 < c < d1]
        out.append(self.point(d1))
        return out


def rgbf(c):
    return np.array(c, dtype=np.float32) / 255


class Frame:
    """Additive light layers on the dark plate."""

    def __init__(self):
        self.size = (W * SS, H * SS)
        self.sharp = np.zeros((H * SS, W * SS, 3), np.float32)
        self.glow_src = np.zeros_like(self.sharp)

    def _layer(self):
        return Image.new("L", self.size, 0)

    def _add(self, mask_img, color, gain=1.0, glow=0.0):
        m = np.asarray(mask_img, np.float32)[..., None] / 255
        light = m * rgbf(color) * gain
        self.sharp += light
        if glow:
            self.glow_src += light * glow

    def lines(self, pts, color, width, gain=1.0, glow=0.0, joint="curve"):
        if len(pts) < 2:
            return
        img = self._layer()
        ImageDraw.Draw(img).line(pts, fill=255, width=max(1, int(round(width * SS))), joint=joint)
        self._add(img, color, gain, glow)

    def dot(self, p, r, color, gain=1.0, glow=0.0):
        img = self._layer()
        ImageDraw.Draw(img).ellipse([p[0] - r * SS, p[1] - r * SS, p[0] + r * SS, p[1] + r * SS], fill=255)
        self._add(img, color, gain, glow)

    def ring(self, c, r, color, width, gain):
        img = self._layer()
        ImageDraw.Draw(img).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=255, width=int(width * SS))
        self._add(img, color, gain, glow=1.2)

    def hatch(self, color, reveal):
        """reveal(j) -> fraction of hatch line j drawn; lines alternate direction; clipped to the hooks."""
        img = self._layer()
        d = ImageDraw.Draw(img)
        for j, y in enumerate(HATCH_Y):
            f = reveal(j, y)
            if f <= 0:
                continue
            x0, x1 = (28, 28 + 144 * f) if j % 2 == 0 else (172 - 144 * f, 172)
            d.line([em((x0, y)), em((x1, y))], fill=255, width=int(1.3 * EM_SCALE * SS))
        clip = self._layer()
        cd = ImageDraw.Draw(clip)
        cd.polygon([em(p) for p in HOOK_A], fill=255)
        cd.polygon([em(p) for p in HOOK_B], fill=255)
        masked = Image.fromarray((np.asarray(img, np.float32) * np.asarray(clip, np.float32) / 255).astype(np.uint8))
        self._add(masked, color, gain=0.42, glow=0.25)

    def render(self, glow_gain):
        glow = Image.fromarray(np.clip(self.glow_src * 255, 0, 255).astype(np.uint8))
        g1 = np.asarray(glow.filter(ImageFilter.GaussianBlur(4 * SS)), np.float32) / 255
        g2 = np.asarray(glow.filter(ImageFilter.GaussianBlur(14 * SS)), np.float32) / 255
        light = self.sharp + (g1 * 0.9 + g2 * 0.7) * glow_gain
        out = rgbf(BG) + light
        img = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))
        return img.resize((W, H), Image.LANCZOS)


def build_sparks(hooks, seed=7):
    """Deterministic spark particles shed by the two laser tips during the contour cut."""
    rng = random.Random(seed)
    sparks = []
    t = 0.35
    while t < 2.0:
        p = ease(seg(t, 0.35, 1.65))
        for h in hooks:
            x, y = em(h.point(p * h.length))
            for _ in range(2):
                ang = rng.uniform(0, 2 * math.pi)
                sp = rng.uniform(60, 220) * SS
                sparks.append((t, x, y, math.cos(ang) * sp, math.sin(ang) * sp - 40 * SS, rng.uniform(0.18, 0.42)))
        t += 1 / 50
    return sparks


def draw_frame(t, accent, hooks, words, sparks, rng):
    """One frame at time t; rng only drives the kerf arc's flicker."""
    f = Frame()
    cut = ease(seg(t, 0.35, 1.65))
    hot_len, warm_len = 16, 70          # design units behind the tip

    # Hatch raster (2.0-2.75) under the contour
    k = ease(seg(t, 2.0, 0.75))
    if t >= 2.0:
        sy = 16 + k * 172
        f.hatch(accent, lambda j, y: min(1.0, max(0.0, (sy - y) / 8)))
        if 0 < k < 1:
            f.lines([em((26, sy)), em((174, sy))], (255, 255, 255), 1.5 * EM_SCALE, gain=0.95, glow=1.0)

    for h in hooks:
        d = cut * h.length
        cooling = 1 - seg(t, 2.0, 0.5)          # warm/hot trail shrinks into the end point after the pass
        f.lines([em(p) for p in h.sub(0, d - warm_len * cooling)], accent, 2.2 * EM_SCALE, glow=1.0, joint=None)
        if cut >= 1 and cooling <= 0:
            continue
        f.lines([em(p) for p in h.sub(d - warm_len * cooling, d - hot_len * cooling)], WARM, 2.2 * EM_SCALE, glow=1.2, joint=None)
        f.lines([em(p) for p in h.sub(d - hot_len * cooling, d)], (255, 255, 255), 2.5 * EM_SCALE, glow=1.5, joint=None)
        if t < 2.0:
            tip = em(h.point(d))
            flick = 1.0 if t >= 0.35 else ease(seg(t, 0.0, 0.35))
            f.dot(tip, 2.6 * EM_SCALE * flick, (255, 255, 255), glow=2.5)
            f.dot(tip, 5.0 * EM_SCALE * flick, accent, gain=0.35, glow=2.0)

    # Sparks with gravity
    g = 520 * SS
    for (tb, x, y, vx, vy, life) in sparks:
        a = t - tb
        if 0 < a < life:
            fade = 1 - a / life
            px, py = x + vx * a, y + vy * a + 0.5 * g * a * a
            qx, qy = x + vx * (a - 0.025), y + vy * (a - 0.025) + 0.5 * g * (a - 0.025) ** 2
            f.lines([(qx, qy), (px, py)], WARM if fade < 0.6 else (255, 255, 255), 1.1, gain=fade, glow=0.8 * fade)

    # Arc jumps the kerf (2.72-3.05)
    a = seg(t, 2.72, 0.33)
    if 0 < a < 1:
        pts = [(94 + i * 2.4, 100 + (rng.uniform(-4.5, 4.5) if 0 < i < 5 else 0)) for i in range(6)]
        f.lines([em(p) for p in pts], (255, 255, 255), 1.2 * EM_SCALE, glow=2.5, joint=None)

    # Power-on pulse + ring (3.05)
    pulse = math.exp(-max(0.0, t - 3.05) * 4.5) if t >= 3.05 else 0.0
    r = seg(t, 3.05, 0.7)
    if 0 < r < 1:
        f.ring(em((100, 100)), (70 + 90 * ease(r)) * EM_SCALE * SS, accent, 1.5 * EM_SCALE, gain=(1 - r) * 0.8)

    # Wordmark engraved stroke by stroke (3.15-4.1)
    n = len(words)
    for i, w in enumerate(words):
        t0 = 3.15 + i * (0.95 / n)
        p = seg(t, t0, 0.95 / n + 0.08)
        if p <= 0:
            continue
        d = p * w.length
        f.lines([wd(q) for q in w.sub(0, d)], TEXT, 2.6 * WD_SCALE + 0.4, glow=0.45, joint=None)
        if p < 1:
            tip = wd(w.point(d))
            f.dot(tip, 2.0, (255, 255, 255), glow=2.0)
            f.dot(tip, 4.5, accent, gain=0.3, glow=1.5)

    return f.render(glow_gain=0.85 + 1.6 * pulse)


def render_glow(accent):
    """RGBA bloom of the finished emblem; the script fades it in and out in the hold state."""
    f = Frame()
    for h in (HOOK_A, HOOK_B):
        f.lines([em(p) for p in h], accent, 3.0 * EM_SCALE, glow=1.0, joint=None)
    glow = Image.fromarray(np.clip(f.glow_src * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12 * SS))
    lum = np.asarray(glow.convert("L"), np.float32)
    alpha = np.clip(lum * 2.2, 0, 255).astype(np.uint8)
    rgba = np.zeros((H * SS, W * SS, 4), np.uint8)
    rgba[..., :3] = accent
    rgba[..., 3] = alpha
    return Image.fromarray(rgba, "RGBA").resize((W, H), Image.LANCZOS)


HOOKS = [Poly(HOOK_A), Poly(HOOK_B)]
WORDS = [Poly(w) for w in WORD]
SPARKS = build_sparks(HOOKS)


def write_frame(job):
    i, accent, out = job
    img = draw_frame(i / FPS, accent, HOOKS, WORDS, SPARKS, random.Random(1000 + i))  # per-frame seed: reproducible in parallel
    img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(out / f"frame-{i:03d}.png", optimize=True)


def main():
    out = Path(sys.argv[1])
    h = sys.argv[2].lstrip("#")
    accent = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    out.mkdir(parents=True, exist_ok=True)
    frames = int(END * FPS)
    with ProcessPoolExecutor(max_workers=os.cpu_count() or 2) as pool:
        list(pool.map(write_frame, [(i, accent, out) for i in range(frames)]))
    draw_frame(END + 2, accent, HOOKS, WORDS, SPARKS, random.Random(0)).save(out / "final.png", optimize=True)
    render_glow(accent).save(out / "glow.png", optimize=True)
    print(f"{frames} frames -> {out}")


if __name__ == "__main__":
    main()
