"""SYNAPSE wordmark glyphs, built on the Twin-Hook S grid from synapseos-icon.svg.

Every glyph shares the S construction: cap height 72, stroke 12.6, 45-degree
outer chamfer 9, inner chamfer 6.3 and parallel slanted terminals (dx -3.6
over one stroke height). Coordinates are glyph-local, y down, origin top-left.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CAP = 72.0
T = 12.6          # stroke
C = 9.0           # outer chamfer
CI = 6.3          # inner chamfer
SL = 3.6          # terminal slant
GAP = 9.0         # letter spacing

# Twin-Hook S, straight from the icon (translated so its box starts at 0,0).
_HOOK_A = [(63.0, 0.0), (59.4, 12.6), (18.9, 12.6), (12.6, 18.9), (12.6, 29.7),
           (30.6, 29.7), (27.0, 42.3), (9.0, 42.3), (0.0, 33.3), (0.0, 9.0), (9.0, 0.0)]
_HOOK_B = [(63.0 - x, 72.0 - y) for x, y in _HOOK_A]


def _s():
    return 63.0, [_HOOK_A, _HOOK_B], []


def _y(w=58.0):
    sl, sr = (w - T) / 2, (w + T) / 2
    return w, [[(0, 0), (T, 0), (T, 23.4), (T + CI, 29.7), (w - T - CI, 29.7), (w - T, 23.4),
                (w - T, 0), (w, 0), (w, 33.3), (w - C, 42.3), (sr, 42.3), (sr, CAP),
                (sl, CAP), (sl, 42.3), (C, 42.3), (0, 33.3)]], []


def _arch(w):
    """Inverted-U body shared by N and A."""
    return [(0, CAP), (0, C), (C, 0), (w - C, 0), (w, C), (w, CAP), (w - T, CAP),
            (w - T, T + CI), (w - T - CI, T), (T + CI, T), (T, T + CI), (T, CAP)]


def _n(w=58.0):
    return w, [_arch(w)], []


def _a(w=58.0):
    return w, [_arch(w), [(T, 29.7), (w - T, 29.7), (w - T, 42.3), (T, 42.3)]], []


def _p(w=56.0):
    outer = [(0, CAP), (0, C), (C, 0), (w - C, 0), (w, C), (w, 33.3), (w - C, 42.3),
             (T, 42.3), (T, CAP)]
    hole = [(T, T), (w - T - CI, T), (w - T, T + CI), (w - T, 29.7 - CI + 3.0),
            (w - T - 3.0, 29.7), (T, 29.7)]
    return w, [outer], [hole]


def _e(w=52.0):
    return w, [[(0, C), (C, 0), (w, 0), (w - SL, T), (T, T), (T, 29.7), (w - 6, 29.7),
                (w - 6 - SL, 42.3), (T, 42.3), (T, 59.4), (w, 59.4), (w - SL, CAP),
                (C, CAP), (0, CAP - C)]], []


GLYPHS = {"S": _s, "Y": _y, "N": _n, "A": _a, "P": _p, "E": _e}


def layout(text="SYNAPSE"):
    """Return [(char, x_offset, width, polys, holes)] and the total advance width."""
    out, x = [], 0.0
    for ch in text:
        w, polys, holes = GLYPHS[ch]()
        out.append((ch, x, w, polys, holes))
        x += w + GAP
    return out, x - GAP


def glyph_mask(size, glyphs, scale, ox, oy, only=None, ss=2):
    """Antialiased L-mode mask of the laid-out glyphs (optionally a subset by index)."""
    W, H = size
    m = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(m)
    for i, (_, gx, _, polys, holes) in enumerate(glyphs):
        if only is not None and i not in only:
            continue
        tr = lambda p: [((ox + (gx + x) * scale) * ss, (oy + y * scale) * ss) for x, y in p]
        for p in polys:
            d.polygon(tr(p), fill=255)
        for p in holes:
            d.polygon(tr(p), fill=0)
    return m.resize((W, H), Image.LANCZOS)


def fblur(a, r):
    """Float box-blur x3 (~gaussian) without 8-bit quantisation."""
    r = max(1, int(round(r)))
    for _ in range(3):
        for ax in (0, 1):
            c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(2)], mode="edge"), axis=ax)
            a = (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
    return a


def chrome(mask, top, height, rim=(203, 166, 247), rim_strength=0.55, sweep=None):
    """Liquid-silver shading for a glyph mask.

    top/height: pixel span of the cap height (drives the horizon reflection).
    sweep: optional x position (px) of a diagonal specular sweep.
    Returns RGBA.
    """
    W, H = mask.size
    a = np.asarray(mask, dtype=np.float32) / 255.0
    ys = (np.arange(H, dtype=np.float32)[:, None] - top) / max(height, 1)
    ys = np.clip(ys, 0, 1)

    # Horizon chrome ramp: bright sky, dark horizon band just under the middle, warm floor.
    stops = np.array([0.0, 0.30, 0.50, 0.53, 0.75, 1.0])
    lum = np.array([1.00, 0.86, 0.48, 0.22, 0.58, 0.82])
    base = np.interp(ys, stops, lum)
    base = np.broadcast_to(base, (H, W)).copy()

    # Bevel lighting from the blurred mask gradient (light from upper-left).
    soft = fblur(a, height * 0.02)
    gy, gx = np.gradient(soft)
    bevel = np.clip(-(gx * 0.7 + gy * 0.9) * height * 0.9, -0.5, 0.6)
    base = np.clip(base + bevel, 0, 1)

    if sweep is not None:
        xx = np.arange(W, dtype=np.float32)[None, :]
        yy = np.arange(H, dtype=np.float32)[:, None]
        band = np.exp(-(((xx - sweep) + (yy - top) * 0.45) / (height * 0.22)) ** 2)
        base = np.clip(base + band * 0.55, 0, 1)

    silver_lo = np.array([88, 92, 112], np.float32)    # cool gunmetal
    silver_hi = np.array([248, 250, 255], np.float32)  # specular white
    rgb = silver_lo + (silver_hi - silver_lo) * base[..., None]
    # Faint cool tint toward #cdd6f4 in the mids.
    rgb = rgb * 0.9 + np.array([205, 214, 244], np.float32) * 0.1 * base[..., None]

    # Thin mauve rim: edge band of the mask.
    edge = np.clip(a - np.asarray(mask.filter(ImageFilter.MinFilter(3)), np.float32) / 255.0, 0, 1)
    rgb = rgb * (1 - edge[..., None] * rim_strength) + np.array(rim, np.float32) * edge[..., None] * rim_strength

    out = np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def glow(mask, radius, color=(203, 166, 247), strength=0.6):
    g = mask.filter(ImageFilter.GaussianBlur(radius))
    a = np.asarray(g, np.float32) * strength
    rgba = np.zeros((*a.shape, 4), np.uint8)
    rgba[..., :3] = color
    rgba[..., 3] = np.clip(a, 0, 255)
    return Image.fromarray(rgba, "RGBA")
