#!/usr/bin/env python3
"""Render the SynapseOS "Twin Hook" laser-engrave boot animation for Plymouth.

    render_frames.py OUTDIR ACCENT_HEX

Writes OUTDIR/frame-000.png ... (opaque, optimized PNGs on #11111b Obsidian Crust),
OUTDIR/final.png (hold state) and OUTDIR/glow.png (RGBA bloom the script breathes).

Choreography:
  0.00-0.35s: Dual optical reticle targeting & ignition at opposite hook terminals.
  0.35-2.00s: Twin Hook laser contour cut in mirror sync with dynamic radial sparks,
              anamorphic lens flares, and thermal dissipation kerf trails.
  2.00-2.75s: Raster hatch sweep under the contour with micro-spark ejecta.
  2.72-3.05s: Dielectric arc jump bridging the kerf with electric micro-sparks.
  3.05-3.75s: Power-on surge pulse + dual holographic shockwave rings.
  3.15-4.15s: "SYNAPSE" geometric wordmark engraved letter by letter.
  0.35-4.20s: High-tech glowing progress line and laser sweep below the wordmark.
  4.20-4.70s: System convergence and hold calibration.
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
W, H = 600, 560          # Canvas size for 1080p display; script scales for other resolutions
SS = 2                   # Supersampling factor for crisp anti-aliasing
BG = (17, 17, 27)        # #11111b Obsidian Crust
WHITE = (255, 255, 255)
WARM = (255, 196, 140)
TEXT = (205, 214, 244)   # #cdd6f4 Liquid Silver Chrome
MUTED = (45, 48, 66)     # Subtle guide track slot

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
EM_OX, EM_OY = (W - 200 * EM_SCALE) / 2, 30      # emblem origin (140, 30)
WD_SCALE = 0.8
WD_OX, WD_OY = (W - 524 * WD_SCALE) / 2, 438     # wordmark origin (90.4, 438)

# Progress line coordinates
PL_X0 = 76.0
PL_X1 = 524.0
PL_Y = 492.0


def em(p):
    return ((EM_OX + p[0] * EM_SCALE) * SS, (EM_OY + p[1] * EM_SCALE) * SS)


def wd(p):
    return ((WD_OX + p[0] * WD_SCALE) * SS, (WD_OY + p[1] * WD_SCALE) * SS)


def pl(x, y):
    return (x * SS, y * SS)


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
    return np.array(c, dtype=np.float32) / 255.0


class Frame:
    """Additive light layers on the dark Obsidian Crust plate."""

    def __init__(self):
        self.size = (W * SS, H * SS)
        self.sharp = np.zeros((H * SS, W * SS, 3), np.float32)
        self.glow_src = np.zeros_like(self.sharp)

    def _layer(self):
        return Image.new("L", self.size, 0)

    def _add(self, mask_img, color, gain=1.0, glow=0.0):
        box = mask_img.getbbox()
        if not box:
            return
        x0, y0, x1, y1 = box
        crop = mask_img.crop(box)
        m = (np.asarray(crop, np.float32) / 255.0) * gain
        col = rgbf(color)
        for c in range(3):
            mc = m * col[c]
            self.sharp[y0:y1, x0:x1, c] += mc
            if glow > 0:
                self.glow_src[y0:y1, x0:x1, c] += mc * glow

    def lines(self, pts, color, width, gain=1.0, glow=0.0, joint="curve"):
        if len(pts) < 2:
            return
        img = self._layer()
        ImageDraw.Draw(img).line(pts, fill=255, width=max(1, int(round(width * SS))), joint=joint)
        self._add(img, color, gain, glow)

    def batch_lines(self, segments, color, gain=1.0, glow=0.0):
        """Draw multiple line segments in a single pass for optimal performance."""
        if not segments:
            return
        img = self._layer()
        d = ImageDraw.Draw(img)
        for pts, w, a in segments:
            if len(pts) >= 2:
                d.line(pts, fill=int(round(a * 255)), width=max(1, int(round(w * SS))))
        self._add(img, color, gain, glow)

    def dot(self, p, r, color, gain=1.0, glow=0.0):
        img = self._layer()
        ImageDraw.Draw(img).ellipse([p[0] - r * SS, p[1] - r * SS, p[0] + r * SS, p[1] + r * SS], fill=255)
        self._add(img, color, gain, glow)

    def ring(self, c, r, color, width, gain):
        img = self._layer()
        ImageDraw.Draw(img).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=255, width=max(1, int(round(width * SS))))
        self._add(img, color, gain, glow=1.5)

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
        masked = Image.fromarray((np.asarray(img, np.float32) * np.asarray(clip, np.float32) / 255.0).astype(np.uint8))
        self._add(masked, color, gain=0.45, glow=0.30)

    def render(self, glow_gain=1.0):
        # 1. Downscale glow to (W, H) for smooth multi-tier bloom
        glow_uint = np.clip(self.glow_src * 255.0, 0, 255).astype(np.uint8)
        glow_img = Image.fromarray(glow_uint).resize((W, H), Image.BILINEAR)
        g1 = np.asarray(glow_img.filter(ImageFilter.GaussianBlur(2.5)), np.float32) / 255.0
        g2 = np.asarray(glow_img.filter(ImageFilter.GaussianBlur(7.0)), np.float32) / 255.0
        g3 = np.asarray(glow_img.filter(ImageFilter.GaussianBlur(16.0)), np.float32) / 255.0

        # 2. Downscale sharp buffer with Lanczos for anti-aliasing
        sharp_uint = np.clip(self.sharp * 255.0, 0, 255).astype(np.uint8)
        sharp_img = Image.fromarray(sharp_uint).resize((W, H), Image.LANCZOS)
        sharp_res = np.asarray(sharp_img, np.float32) / 255.0

        # 3. Composite onto #11111b Obsidian Crust background
        light = sharp_res + (g1 * 0.75 + g2 * 0.45 + g3 * 0.25) * glow_gain
        out = rgbf(BG) + light
        return Image.fromarray((np.clip(out, 0, 1) * 255.0 + 0.5).astype(np.uint8))


def build_sparks(hooks, seed=42):
    """Deterministic spark particles with dynamic radial dispersion, variable mass, and physical motion."""
    rng = random.Random(seed)
    sparks = []

    # 1. Twin Hook contour cut sparks (0.35 to 2.0s)
    t = 0.35
    dt = 1 / 50
    while t < 2.0:
        p = ease(seg(t, 0.35, 1.65))
        for h in hooks:
            pos = h.point(p * h.length)
            x, y = em(pos)
            dp = 0.005
            p_ahead = min(1.0, p + dp)
            p_back = max(0.0, p - dp)
            pt_ahead = em(h.point(p_ahead * h.length))
            pt_back = em(h.point(p_back * h.length))
            tangent_angle = math.atan2(pt_ahead[1] - pt_back[1], pt_ahead[0] - pt_back[0])

            # Ejection cone: biased backward and outward from the cutting direction
            num_spray = rng.randint(2, 3)
            for _ in range(num_spray):
                spray_dir = tangent_angle + math.pi + rng.uniform(-1.25, 1.25)
                speed = rng.uniform(80, 260) * SS
                vx = math.cos(spray_dir) * speed
                vy = math.sin(spray_dir) * speed - rng.uniform(20, 60) * SS  # thermal plume
                lifetime = rng.uniform(0.18, 0.42)
                brightness = rng.uniform(0.9, 1.4)
                width = rng.uniform(1.0, 1.5)
                sparks.append((t, x, y, vx, vy, lifetime, brightness, width))

            # Radial isotropic micro-droplets
            if rng.random() < 0.6:
                ang = rng.uniform(0, 2 * math.pi)
                speed = rng.uniform(40, 130) * SS
                vx = math.cos(ang) * speed
                vy = math.sin(ang) * speed - 25 * SS
                lifetime = rng.uniform(0.24, 0.50)
                brightness = rng.uniform(0.7, 1.1)
                width = rng.uniform(0.7, 1.1)
                sparks.append((t, x, y, vx, vy, lifetime, brightness, width))
        t += dt

    # 2. Raster hatch micro-sparks (2.0 to 2.75s)
    t = 2.0
    while t < 2.75:
        k = ease(seg(t, 2.0, 0.75))
        sy = 16 + k * 172
        if rng.random() < 0.65:
            hx = rng.uniform(40, 160)
            x, y = em((hx, sy))
            ang = rng.uniform(-math.pi * 0.85, -math.pi * 0.15)
            speed = rng.uniform(60, 160) * SS
            sparks.append((t, x, y, math.cos(ang) * speed, math.sin(ang) * speed, rng.uniform(0.14, 0.30), rng.uniform(0.8, 1.2), 1.0))
        t += dt * 1.5

    # 3. Kerf arc jump electric micro-sparks (2.72 to 3.05s)
    t = 2.72
    while t < 3.05:
        if rng.random() < 0.75:
            arc_x = rng.uniform(94, 106)
            arc_y = 100 + rng.uniform(-6, 6)
            x, y = em((arc_x, arc_y))
            ang = rng.uniform(0, 2 * math.pi)
            speed = rng.uniform(80, 200) * SS
            sparks.append((t, x, y, math.cos(ang) * speed, math.sin(ang) * speed, rng.uniform(0.10, 0.25), rng.uniform(1.0, 1.5), 1.1))
        t += dt

    return sparks


def draw_frame(t, accent, hooks, words, sparks, rng):
    """Render a single frame at timestamp t."""
    f = Frame()
    cut = ease(seg(t, 0.35, 1.65))
    hot_len, warm_len = 16, 70          # design units behind the cutting head

    # 1. Raster hatch under the contour (2.0 to 2.75s)
    k = ease(seg(t, 2.0, 0.75))
    if t >= 2.0:
        sy = 16 + k * 172
        f.hatch(accent, lambda j, y: min(1.0, max(0.0, (sy - y) / 8)))
        if 0 < k < 1:
            f.lines([em((24, sy)), em((176, sy))], WHITE, 1.6 * EM_SCALE, gain=1.2, glow=2.0)
            f.lines([em((20, sy)), em((180, sy))], accent, 3.2 * EM_SCALE, gain=0.6, glow=1.5)

    # 2. Twin Hook laser contour cut (0.0 to 2.0s and permanent groove)
    for h in hooks:
        d = cut * h.length
        cooling = 1.0 - seg(t, 2.0, 0.5)

        channel_d = d - warm_len * cooling
        if channel_d > 0:
            f.lines([em(p) for p in h.sub(0, channel_d)], accent, 2.4 * EM_SCALE, glow=1.0, joint=None)
            bright_accent = (min(255, accent[0] + 50), min(255, accent[1] + 50), min(255, accent[2] + 50))
            f.lines([em(p) for p in h.sub(0, channel_d)], bright_accent, 1.0 * EM_SCALE, gain=0.7, glow=0.5, joint=None)

        if cut < 1 or cooling > 0:
            f.lines([em(p) for p in h.sub(d - warm_len * cooling, d - hot_len * cooling)], WARM, 2.4 * EM_SCALE, glow=1.4, joint=None)
            f.lines([em(p) for p in h.sub(d - hot_len * cooling, d)], WHITE, 2.8 * EM_SCALE, gain=1.4, glow=2.2, joint=None)

        if t < 2.0:
            tip = em(h.point(d))
            flick = 1.0 if t >= 0.35 else ease(seg(t, 0.0, 0.35))
            if t < 0.35:
                reticle_r = (18.0 * (1.0 - ease(seg(t, 0.0, 0.35)))) * EM_SCALE
                if reticle_r > 3.0:
                    f.ring(tip, reticle_r * SS, accent, 1.0 * EM_SCALE, gain=0.8 * flick)
            f.dot(tip, 2.6 * EM_SCALE * flick, WHITE, gain=1.6, glow=3.0)
            f.dot(tip, 6.0 * EM_SCALE * flick, accent, gain=0.5, glow=2.2)
            if t >= 0.35:
                flare_len = (18.0 + 4.0 * math.sin(t * 45)) * EM_SCALE * SS
                f.lines([(tip[0] - flare_len, tip[1]), (tip[0] + flare_len, tip[1])], WHITE, 1.2, gain=0.85, glow=2.0)
                f.lines([(tip[0] - flare_len * 1.5, tip[1]), (tip[0] + flare_len * 1.5, tip[1])], accent, 2.2, gain=0.45, glow=1.5)

    # 3. Dynamic radial sparks with physical cooling stages
    g = 480 * SS
    white_segs = []
    warm_segs = []
    accent_segs = []

    for (tb, x, y, vx, vy, life, bright, w) in sparks:
        a = t - tb
        if 0 < a < life:
            fade = 1.0 - (a / life)
            fade_sq = fade * fade * bright
            px = x + vx * a
            py = y + vy * a + 0.5 * g * a * a
            prev_a = max(0.0, a - 0.024)
            qx = x + vx * prev_a
            qy = y + vy * prev_a + 0.5 * g * prev_a * prev_a

            if fade > 0.60:
                white_segs.append(([(qx, qy), (px, py)], w * 1.1, min(1.0, fade_sq * 1.3)))
                warm_segs.append(([(qx, qy), (px, py)], w * 1.8, min(1.0, fade_sq * 0.9)))
            elif fade > 0.25:
                warm_segs.append(([(qx, qy), (px, py)], w * 1.2, min(1.0, fade_sq * 1.1)))
                accent_segs.append(([(qx, qy), (px, py)], w * 2.0, min(1.0, fade_sq * 0.7)))
            else:
                accent_segs.append(([(qx, qy), (px, py)], w * 1.3, min(1.0, fade_sq * 0.9)))

    if accent_segs:
        f.batch_lines(accent_segs, accent, gain=1.0, glow=1.2)
    if warm_segs:
        f.batch_lines(warm_segs, WARM, gain=1.1, glow=1.4)
    if white_segs:
        f.batch_lines(white_segs, WHITE, gain=1.4, glow=2.0)

    # 4. Arc jumps the kerf (2.72 to 3.05s)
    a = seg(t, 2.72, 0.33)
    if 0 < a < 1:
        pts = [(94 + i * 2.4, 100 + (rng.uniform(-5.0, 5.0) if 0 < i < 5 else 0)) for i in range(6)]
        f.lines([em(p) for p in pts], WHITE, 1.5 * EM_SCALE, gain=1.5, glow=3.0, joint=None)
        f.lines([em(p) for p in pts], accent, 3.2 * EM_SCALE, gain=0.8, glow=2.5, joint=None)
        if rng.random() < 0.6:
            pts2 = [(94 + i * 2.4, 100 + (rng.uniform(-3.0, 3.0) if 0 < i < 5 else 0)) for i in range(6)]
            f.lines([em(p) for p in pts2], WHITE, 0.9 * EM_SCALE, gain=1.0, glow=2.0, joint=None)

    # 5. Power-on surge pulse & dual holographic shockwave (3.05 to 3.75s)
    pulse = math.exp(-max(0.0, t - 3.05) * 4.5) if t >= 3.05 else 0.0
    r1 = seg(t, 3.05, 0.65)
    if 0 < r1 < 1:
        f.ring(em((100, 100)), (65 + 105 * ease(r1)) * EM_SCALE * SS, accent, 1.8 * EM_SCALE, gain=(1.0 - r1) * 0.9)
    r2 = seg(t, 3.12, 0.55)
    if 0 < r2 < 1:
        f.ring(em((100, 100)), (50 + 110 * ease(r2)) * EM_SCALE * SS, WHITE, 1.0 * EM_SCALE, gain=(1.0 - r2) * 0.6)

    # 6. Wordmark engraved stroke by stroke (3.15 to 4.15s)
    n = len(words)
    for i, w in enumerate(words):
        t0 = 3.15 + i * (0.95 / n)
        p = seg(t, t0, 0.95 / n + 0.08)
        if p <= 0:
            continue
        d = p * w.length
        f.lines([wd(q) for q in w.sub(0, d)], TEXT, 2.6 * WD_SCALE + 0.4, glow=0.55, joint=None)
        if p < 1:
            tip = wd(w.point(d))
            f.dot(tip, 2.2, WHITE, gain=1.5, glow=2.5)
            f.dot(tip, 5.0, accent, gain=0.45, glow=2.0)

    # 7. High-Tech Glowing Progress Line & Laser Sweep below SYNAPSE wordmark
    track_opacity = ease(seg(t, 0.15, 0.35))
    if track_opacity > 0:
        f.lines([pl(PL_X0, PL_Y), pl(PL_X1, PL_Y)], MUTED, 1.4, gain=0.6 * track_opacity, glow=0.1)
        bracket_color = (min(255, accent[0] // 2 + 35), min(255, accent[1] // 2 + 35), min(255, accent[2] // 2 + 35))
        f.lines([pl(PL_X0 + 4, PL_Y - 4), pl(PL_X0, PL_Y - 4), pl(PL_X0, PL_Y + 4), pl(PL_X0 + 4, PL_Y + 4)],
                bracket_color, 1.2, gain=0.8 * track_opacity, glow=0.5)
        f.lines([pl(PL_X1 - 4, PL_Y - 4), pl(PL_X1, PL_Y - 4), pl(PL_X1, PL_Y + 4), pl(PL_X1 - 4, PL_Y + 4)],
                bracket_color, 1.2, gain=0.8 * track_opacity, glow=0.5)
        for frac in (0.25, 0.50, 0.75):
            nx = PL_X0 + (PL_X1 - PL_X0) * frac
            f.lines([pl(nx, PL_Y - 2.5), pl(nx, PL_Y + 2.5)], MUTED, 1.0, gain=0.8 * track_opacity, glow=0.1)

    prog_k = ease(seg(t, 0.35, 3.85))
    if prog_k > 0:
        curr_x = PL_X0 + (PL_X1 - PL_X0) * prog_k
        f.lines([pl(PL_X0, PL_Y), pl(curr_x, PL_Y)], accent, 2.0, gain=0.95, glow=1.1)
        f.lines([pl(PL_X0, PL_Y), pl(curr_x, PL_Y)], WHITE, 0.9, gain=0.5, glow=0.5)

        if prog_k < 1.0 and t < 4.25:
            f.dot(pl(curr_x, PL_Y), 2.2, WHITE, gain=1.6, glow=3.0)
            f.dot(pl(curr_x, PL_Y), 5.2, accent, gain=0.6, glow=2.2)
            f.lines([pl(curr_x, PL_Y - 6), pl(curr_x, PL_Y + 6)], WHITE, 1.2, gain=1.4, glow=2.5)
            tail_x0 = max(PL_X0, curr_x - 38)
            if curr_x > tail_x0:
                f.lines([pl(tail_x0, PL_Y), pl(curr_x, PL_Y)], WHITE, 1.4, gain=0.6, glow=1.5)

    return f.render(glow_gain=0.85 + 1.6 * pulse)


def render_glow(accent):
    """RGBA bloom of the finished emblem and progress rule; script breathes it in the hold state."""
    f = Frame()
    for h in (HOOK_A, HOOK_B):
        f.lines([em(p) for p in h], accent, 3.2 * EM_SCALE, glow=1.2, joint=None)
    f.lines([pl(PL_X0, PL_Y), pl(PL_X1, PL_Y)], accent, 2.4, glow=1.0)
    f.lines([pl(PL_X0, PL_Y - 4), pl(PL_X0, PL_Y + 4)], accent, 1.8, glow=0.8)
    f.lines([pl(PL_X1, PL_Y - 4), pl(PL_X1, PL_Y + 4)], accent, 1.8, glow=0.8)

    glow = Image.fromarray(np.clip(f.glow_src * 255.0, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12 * SS))
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
    img = draw_frame(i / FPS, accent, HOOKS, WORDS, SPARKS, random.Random(1000 + i))
    img.quantize(colors=256, method=Image.Quantize.LIBIMAGEQUANT).save(out / f"frame-{i:03d}.png", optimize=True)


def main():
    out = Path(sys.argv[1])
    h = sys.argv[2].lstrip("#")
    accent = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    out.mkdir(parents=True, exist_ok=True)
    frames = int(END * FPS)
    workers = min(os.cpu_count() or 2, 8)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        list(pool.map(write_frame, [(i, accent, out) for i in range(frames)]))
    draw_frame(END + 2, accent, HOOKS, WORDS, SPARKS, random.Random(0)).save(out / "final.png", optimize=True)
    render_glow(accent).save(out / "glow.png", optimize=True)
    print(f"{frames} frames -> {out}")


if __name__ == "__main__":
    main()
