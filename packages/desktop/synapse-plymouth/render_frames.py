#!/usr/bin/env python3
"""SynapseOS Sleek Futuristic Monolith Plymouth Splash Renderer.

Aesthetic Architecture:
- Deep obsidian backdrop with soft volumetric nebula bloom (inspired by Synapse Monolith Wallpapers)
- Precision chamfered monolith wafer substrate with hairline alignment reticles & telemetry
- Exact mathematical Twin Hook Cipher vector geometry from synapseos-icon.svg
- Dual coherent UV laser optic collimators with molten kerf crystallization
- Dielectric ion arc discharge & expanding plasma bloom at central spark gap
- Liquid Silver Chrome typography (Orbitron / Inter / NotoSans) & telemetry progress bar
"""

import math
import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 25
END = 4.8
TOTAL_FRAMES = int(END * FPS)  # 120 frames
W, H = 600, 560
SS = 2  # Supersampling factor for razor-sharp antialiasing

# Color Palette (Matching Synapse Monolith Wallpapers & Catppuccin Mocha)
VOID_BG = (9, 9, 13)            # #09090d True Monolith Base
PLATE_BASE = (17, 17, 27)       # #11111b Deep obsidian crust
PLATE_SURFACE = (24, 24, 37)    # #181825 Inner substrate plate
PLATE_RIM = (49, 50, 68)        # #313244 Beveled edge shadow

# Chrome Metallic Palette
CHROME_WHITE = (255, 255, 255)
CHROME_MID = (205, 214, 244)    # #cdd6f4
CHROME_LOW = (147, 153, 178)    # #9399b2
CHROME_DARK = (49, 50, 68)      # #313244
TEXT_SILVER = (205, 214, 244)
TEXT_DIM = (108, 112, 134)      # #6c7086

# Exact Vector Coordinates from synapseos-icon.svg (128x128 space, centered at 64,64)
HOOK_A_BASE = [
    (95.5, 28.0), (91.9, 40.6), (51.4, 40.6), (45.1, 46.9), (45.1, 57.7),
    (63.1, 57.7), (59.5, 70.3), (41.5, 70.3), (32.5, 61.3), (32.5, 37.0),
    (41.5, 28.0)
]
HOOK_B_BASE = [(128.0 - x, 128.0 - y) for x, y in HOOK_A_BASE]

# Closed perimeter cutting paths (starts top-left, loops perimeter to close, ends at spark notch)
CUT_PATH_A = [
    (41.5, 28.0), (95.5, 28.0), (91.9, 40.6), (51.4, 40.6), (45.1, 46.9),
    (45.1, 57.7), (63.1, 57.7), (59.5, 70.3), (41.5, 70.3), (32.5, 61.3),
    (32.5, 37.0), (41.5, 28.0)
]
CUT_PATH_B = [(128.0 - x, 128.0 - y) for x, y in CUT_PATH_A]

CENTER_X = 300.0
CENTER_Y = 195.0
EM_SCALE = 2.30

# Laser Optic Gantries (Sleek overhead aerospace rails)
GANTRY_L = (70.0, 50.0)
GANTRY_R = (530.0, 50.0)

# Typography & Telemetry Positions
TYPO_Y = 412.0
PROG_Y = 482.0
PROG_W = 420.0


def ease_in_out(k):
    k = min(1.0, max(0.0, k))
    return 4 * k ** 3 if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def ease_out(k):
    k = min(1.0, max(0.0, k))
    return 1 - (1 - k) ** 3


def seg(t, t0, dur):
    return min(1.0, max(0.0, (t - t0) / max(dur, 1e-6)))


def parse_hex_color(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def to_screen(pt, ss=SS):
    x = (CENTER_X + (pt[0] - 64.0) * EM_SCALE) * ss
    y = (CENTER_Y + (pt[1] - 64.0) * EM_SCALE) * ss
    return (x, y)


class PathTracker:
    def __init__(self, pts, ss=SS):
        self.screen_pts = [to_screen(p, ss) for p in pts]
        self.cum = [0.0]
        for a, b in zip(self.screen_pts, self.screen_pts[1:]):
            self.cum.append(self.cum[-1] + math.dist(a, b))
        self.total_len = self.cum[-1]

    def point_at(self, dist):
        dist = min(max(dist, 0.0), self.total_len)
        for i in range(1, len(self.cum)):
            if dist <= self.cum[i]:
                a, b = self.screen_pts[i - 1], self.screen_pts[i]
                span = max(self.cum[i] - self.cum[i - 1], 1e-9)
                k = (dist - self.cum[i - 1]) / span
                return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        return self.screen_pts[-1]

    def subpath(self, d0, d1):
        d0 = max(d0, 0.0)
        d1 = min(d1, self.total_len)
        if d1 <= d0:
            return []
        res = [self.point_at(d0)]
        for p, c in zip(self.screen_pts, self.cum):
            if d0 < c < d1:
                res.append(p)
        res.append(self.point_at(d1))
        return res


def load_fonts():
    bold_candidates = [
        "/usr/share/fonts/Orbitron Black.ttf",
        "/usr/share/fonts/inter/Inter.ttc",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    ]
    mono_candidates = [
        "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/noto/NotoSansMono-Regular.ttf",
    ]

    font_title = None
    for p in bold_candidates:
        if os.path.isfile(p):
            try:
                font_title = ImageFont.truetype(p, 36 * SS)
                break
            except Exception:
                continue

    font_mono = None
    for p in mono_candidates:
        if os.path.isfile(p):
            try:
                font_mono = ImageFont.truetype(p, 10 * SS)
                break
            except Exception:
                continue

    if not font_title:
        font_title = ImageFont.load_default()
    if not font_mono:
        font_mono = ImageFont.load_default()

    return font_title, font_mono


def build_chrome_texture(accent_rgb):
    """Generates a 45-degree Liquid Chrome metallic texture tailored to the accent."""
    W_s, H_s = W * SS, H * SS
    y, x = np.mgrid[0:H_s, 0:W_s]
    diag = (x + y) / (W_s + H_s)

    ar, ag, ab = accent_rgb
    stops = [
        (0.00, np.array([255, 255, 255], dtype=np.float32)),
        (0.25, np.array([205, 214, 244], dtype=np.float32)),
        (0.50, np.array([186, 194, 222], dtype=np.float32)),
        (0.75, np.array([ar, ag, ab], dtype=np.float32)),
        (1.00, np.array([min(255, ar + 30), min(255, ag + 30), min(255, ab + 30)], dtype=np.float32))
    ]

    grad_arr = np.zeros((H_s, W_s, 4), dtype=np.uint8)
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        mask = (diag >= t0) & (diag <= t1)
        k = (diag[mask] - t0) / (t1 - t0)
        for ch in range(3):
            grad_arr[mask, ch] = (c0[ch] + k * (c1[ch] - c0[ch])).astype(np.uint8)
    grad_arr[:, :, 3] = 255
    return Image.fromarray(grad_arr)


def render_monolith_backdrop(accent_rgb):
    """Pre-renders the static Monolith backdrop, plate, and alignment reticles."""
    img = Image.new("RGBA", (W * SS, H * SS), (*VOID_BG, 255))
    draw = ImageDraw.Draw(img)

    # 1. Soft Volumetric Nebula Glow (Centered behind Monolith)
    cx, cy = CENTER_X * SS, CENTER_Y * SS
    glow = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    ar, ag, ab = accent_rgb
    for radius, alpha in [(190 * SS, 12), (140 * SS, 24), (95 * SS, 45), (55 * SS, 75)]:
        gd.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(ar, ag, ab, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(28 * SS))
    img.alpha_composite(glow)

    # 2. Precision Laser Track Gridlines (Fine Cyberdeck Matrix)
    grid_layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_layer)
    for x in range(60, W, 40):
        gdraw.line([(x * SS, 40 * SS), (x * SS, (H - 40) * SS)], fill=(PLATE_RIM[0], PLATE_RIM[1], PLATE_RIM[2], 25), width=1)
    for y in range(60, H, 40):
        gdraw.line([(60 * SS, y * SS), ((W - 60) * SS, y * SS)], fill=(PLATE_RIM[0], PLATE_RIM[1], PLATE_RIM[2], 25), width=1)
    img.alpha_composite(grid_layer)

    # 3. Floating Architectural Monolith Substrate Plate
    plate = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pw, ph = 175.0 * SS, 175.0 * SS
    x0, y0 = cx - pw, cy - ph
    x1, y1 = cx + pw, cy + ph
    radius = 28.0 * SS

    # Drop shadow
    shadow = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([x0 + 2 * SS, y0 + 6 * SS, x1 + 2 * SS, y1 + 6 * SS], radius=radius, fill=(0, 0, 0, 180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * SS))
    img.alpha_composite(shadow)

    # Monolith outer bevel rim
    pd.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(*PLATE_BASE, 245), outline=(ar, ag, ab, 60), width=int(1.5 * SS))
    # Monolith inner machined facet
    inset = 6.0 * SS
    pd.rounded_rectangle([x0 + inset, y0 + inset, x1 - inset, y1 - inset], radius=radius - 4 * SS, fill=(*PLATE_SURFACE, 235))

    # Specular Top-Left Gleam Wire (45-degree horizon reflection)
    pd.line([(x0 + 32 * SS, y0 + inset), (x1 - 32 * SS, y0 + inset)], fill=(255, 255, 255, 110), width=int(1.2 * SS))
    pd.line([(x0 + inset, y0 + 32 * SS), (x0 + inset, y1 - 32 * SS)], fill=(255, 255, 255, 70), width=int(1.2 * SS))

    # Corner Alignment Reticles / Fiducial Crosshairs
    tick_len = 10.0 * SS
    for bx, by in [(x0 + 18 * SS, y0 + 18 * SS), (x1 - 18 * SS, y0 + 18 * SS),
                   (x0 + 18 * SS, y1 - 18 * SS), (x1 - 18 * SS, y1 - 18 * SS)]:
        dx = tick_len if bx < cx else -tick_len
        dy = tick_len if by < cy else -tick_len
        pd.line([(bx, by), (bx + dx, by)], fill=(ar, ag, ab, 170), width=int(1.5 * SS))
        pd.line([(bx, by), (bx, by + dy)], fill=(ar, ag, ab, 170), width=int(1.5 * SS))

    # Precision Micro-Telemetry Etching
    f_title, f_mono = load_fonts()
    pd.text((x0 + 22 * SS, y1 - 18 * SS), "MONOLITH // SPEC-01", font=f_mono, fill=(*CHROME_LOW, 140))
    pd.text((x1 - 120 * SS, y1 - 18 * SS), "STEALTH // ACTIVE", font=f_mono, fill=(ar, ag, ab, 160))

    img.alpha_composite(plate)
    return img


def draw_sleek_laser_head(draw, mount_pt, target_pt, accent_rgb, active=True):
    """Draws a sleek aerospace optical collimator and high-energy laser beam."""
    mx, my = mount_pt[0] * SS, mount_pt[1] * SS
    tx, ty = target_pt

    dx = tx - mx
    dy = ty - my
    dist = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)

    # Gimbal shoulder mount
    draw.ellipse([mx - 6 * SS, my - 6 * SS, mx + 6 * SS, my + 6 * SS], fill=(40, 42, 54), outline=(100, 105, 130), width=SS)

    # Sleek carbon truss arm to emitter nozzle
    nozzle_dist = max(30 * SS, dist - 35 * SS)
    nx = mx + nozzle_dist * math.cos(angle)
    ny = my + nozzle_dist * math.sin(angle)

    draw.line([(mx, my), (nx, ny)], fill=(30, 32, 44), width=int(3.5 * SS))
    draw.line([(mx, my), (nx, ny)], fill=(90, 95, 120), width=int(1.2 * SS))

    # Emitter focus nozzle
    draw.ellipse([nx - 4 * SS, ny - 4 * SS, nx + 4 * SS, ny + 4 * SS], fill=(50, 52, 70), outline=(200, 210, 230), width=SS)

    if active:
        ar, ag, ab = accent_rgb
        # Converging photonic focus cone
        perp_x = -math.sin(angle) * (2.8 * SS)
        perp_y = math.cos(angle) * (2.8 * SS)
        draw.polygon([(nx - perp_x, ny - perp_y), (nx + perp_x, ny + perp_y), (tx, ty)], fill=(ar, ag, ab, 85))

        # Coherent Core Beam
        draw.line([(nx, ny), (tx, ty)], fill=(ar, ag, ab, 180), width=int(2.4 * SS))
        draw.line([(nx, ny), (tx, ty)], fill=(255, 255, 255, 255), width=int(1.0 * SS))

        # Focal Point Plasma Flare
        draw.ellipse([tx - 5 * SS, ty - 5 * SS, tx + 5 * SS, ty + 5 * SS], fill=(ar, ag, ab, 140))
        draw.ellipse([tx - 2 * SS, ty - 2 * SS, tx + 2 * SS, ty + 2 * SS], fill=(255, 255, 255, 255))


def render_single_frame(frame_idx, base_img, chrome_tex, tracker_a, tracker_b, accent_rgb):
    t = frame_idx / FPS  # 0.0 to 4.8s
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    ar, ag, ab = accent_rgb
    f_title, f_mono = load_fonts()

    # Timeline segmentation
    cut_prog = ease_in_out(seg(t, 0.6, 2.3))       # 0.6s -> 2.9s (Cut duration)
    spark_prog = seg(t, 2.9, 0.6)                  # 2.9s -> 3.5s (Dielectric discharge)
    typo_prog = ease_out(seg(t, 3.2, 1.2))         # 3.2s -> 4.4s (Typography reveal)

    # 1. Molten Cut Paths & Crystallized Chrome Emblem
    dist_a = cut_prog * tracker_a.total_len
    dist_b = cut_prog * tracker_b.total_len

    sub_a = tracker_a.subpath(0, dist_a)
    sub_b = tracker_b.subpath(0, dist_b)

    # Liquid Chrome Emblem reveal as cut progresses
    if cut_prog > 0.05:
        mask = Image.new("L", (W * SS, H * SS), 0)
        mdraw = ImageDraw.Draw(mask)
        pts_a = [to_screen(p) for p in HOOK_A_BASE]
        pts_b = [to_screen(p) for p in HOOK_B_BASE]

        alpha_poly = int(255 * ease_out(min(1.0, cut_prog * 1.2)))
        mdraw.polygon(pts_a, fill=alpha_poly)
        mdraw.polygon(pts_b, fill=alpha_poly)

        # Composite Chrome Texture through the polygon mask
        img.paste(chrome_tex, (0, 0), mask)

        # Precision Specular Rims on the Chrome Emblem
        draw.polygon(pts_a, outline=(255, 255, 255, int(alpha_poly * 0.9)), width=int(1.2 * SS))
        draw.polygon(pts_b, outline=(ar, ag, ab, int(alpha_poly * 0.8)), width=int(1.2 * SS))

        # Specular horizon sheen line across upper hook (SVG line 42)
        pt_top_l = to_screen((34.0, 28.0))
        pt_top_r = to_screen((94.0, 28.0))
        gleam_alpha = int(alpha_poly * (0.7 + 0.3 * math.sin(t * 3.5)))
        draw.line([pt_top_l, pt_top_r], fill=(255, 255, 255, gleam_alpha), width=int(1.4 * SS))

    # Molten Kerf Trace (Glowing incandescent edge where cut is active)
    if len(sub_a) >= 2:
        draw.line(sub_a, fill=(ar, ag, ab, 220), width=int(2.2 * SS))
        recent_a = tracker_a.subpath(max(0, dist_a - 18 * SS), dist_a)
        if len(recent_a) >= 2:
            draw.line(recent_a, fill=(255, 255, 255, 255), width=int(1.6 * SS))

    if len(sub_b) >= 2:
        draw.line(sub_b, fill=(ar, ag, ab, 220), width=int(2.2 * SS))
        recent_b = tracker_b.subpath(max(0, dist_b - 18 * SS), dist_b)
        if len(recent_b) >= 2:
            draw.line(recent_b, fill=(255, 255, 255, 255), width=int(1.6 * SS))

    # 2. Dual Laser Optical Heads
    head_a_pos = tracker_a.point_at(dist_a) if cut_prog < 1.0 else to_screen((59.5, 70.3))
    head_b_pos = tracker_b.point_at(dist_b) if cut_prog < 1.0 else to_screen((68.5, 57.7))
    is_cutting = 0.05 < cut_prog < 0.999

    draw_sleek_laser_head(draw, GANTRY_L, head_a_pos, accent_rgb, active=is_cutting)
    draw_sleek_laser_head(draw, GANTRY_R, head_b_pos, accent_rgb, active=is_cutting)

    # 3. Photonic Sparks Spray
    if is_cutting:
        rng = random.Random(frame_idx * 19)
        for hpos, angle_base in [(head_a_pos, math.pi * 0.25), (head_b_pos, -math.pi * 0.75)]:
            for _ in range(7):
                sp_ang = angle_base + rng.uniform(-0.8, 0.8)
                sp_spd = rng.uniform(8.0, 20.0) * SS
                sp_x = hpos[0] + sp_spd * math.cos(sp_ang)
                sp_y = hpos[1] + sp_spd * math.sin(sp_ang)
                draw.line([hpos, (sp_x, sp_y)], fill=(255, 255, 255, 230), width=int(1.0 * SS))
                draw.ellipse([sp_x - SS, sp_y - SS, sp_x + SS, sp_y + SS], fill=(ar, ag, ab, 200))

    # 4. Central Dielectric Arc Spark Discharge
    if spark_prog > 0:
        sp_a = to_screen((59.5, 70.3))
        sp_b = to_screen((68.5, 57.7))
        mid = ((sp_a[0] + sp_b[0]) / 2, (sp_a[1] + sp_b[1]) / 2)

        # Dielectric arc jitter
        jitter = (math.sin(t * 50) * 3 * SS, math.cos(t * 50) * 3 * SS)
        arc_mid = (mid[0] + jitter[0], mid[1] + jitter[1])

        arc_alpha = int(255 * (1.0 - 0.25 * (1.0 - spark_prog)))
        draw.line([sp_a, arc_mid, sp_b], fill=(255, 255, 255, arc_alpha), width=int(2.4 * SS))
        draw.line([sp_a, arc_mid, sp_b], fill=(ar, ag, ab, int(arc_alpha * 0.8)), width=int(4.5 * SS))

        # Expanding plasma shockwave ring
        if 0.0 < spark_prog < 0.8:
            shock_r = (spark_prog / 0.8) * 80.0 * SS
            shock_a = int(180 * (1.0 - spark_prog / 0.8))
            draw.ellipse([mid[0] - shock_r, mid[1] - shock_r, mid[0] + shock_r, mid[1] + shock_r],
                         outline=(ar, ag, ab, shock_a), width=int(1.5 * SS))

        # Permanent Dielectric Core Spark (SVG lines 31-33)
        draw.ellipse([mid[0] - 3.5 * SS, mid[1] - 3.5 * SS, mid[0] + 3.5 * SS, mid[1] + 3.5 * SS], fill=(255, 255, 255, 255))
        draw.ellipse([mid[0] - 7.0 * SS, mid[1] - 7.0 * SS, mid[0] + 7.0 * SS, mid[1] + 7.0 * SS], fill=(ar, ag, ab, 160))

    # 5. High-Resolution Sleek Typography
    if typo_prog > 0:
        ty_y = TYPO_Y * SS
        text_a = "SYNAPSE"
        text_b = "OS"
        sub_text = "INTELLIGENT CYBERDECK · PRIME DIRECTIVE STEALTH"

        bbox_a = draw.textbbox((0, 0), text_a, font=f_title)
        bbox_b = draw.textbbox((0, 0), text_b, font=f_title)
        w_a = bbox_a[2] - bbox_a[0]
        w_b = bbox_b[2] - bbox_b[0]
        gap = 8 * SS
        total_w = w_a + gap + w_b
        tx0 = (W * SS - total_w) / 2

        alpha_typo = int(255 * typo_prog)
        draw.text((tx0, ty_y), text_a, font=f_title, fill=(*TEXT_SILVER, alpha_typo))
        draw.text((tx0 + w_a + gap, ty_y), text_b, font=f_title, fill=(ar, ag, ab, alpha_typo))

        # Precision Subtitle Tagline
        bbox_sub = draw.textbbox((0, 0), sub_text, font=f_mono)
        w_sub = bbox_sub[2] - bbox_sub[0]
        draw.text(((W * SS - w_sub) / 2, ty_y + 44 * SS), sub_text, font=f_mono, fill=(*CHROME_LOW, int(alpha_typo * 0.85)))

        # Precision Technical Rule Line (SVG lines 47-51)
        rx0 = (W * SS - total_w) / 2
        rx1 = rx0 + total_w
        ry = ty_y + 60 * SS
        draw.line([(rx0, ry), (rx1, ry)], fill=(ar, ag, ab, int(alpha_typo * 0.7)), width=int(1.2 * SS))

    # 6. Sleek Telemetry Progress Bar
    py = PROG_Y * SS
    px0 = (W - PROG_W) / 2 * SS
    px1 = px0 + PROG_W * SS
    bar_h = 4 * SS

    boot_pct = ease_in_out(seg(t, 0.4, 4.0))

    # Subtle background groove
    draw.rounded_rectangle([px0, py, px1, py + bar_h], radius=2 * SS, fill=(*PLATE_BASE, 200), outline=(*PLATE_RIM, 120), width=1)

    # Active glowing fill bar
    fill_w = max(0.0, (px1 - px0) * boot_pct)
    if fill_w > 0:
        draw.rounded_rectangle([px0, py, px0 + fill_w, py + bar_h], radius=2 * SS, fill=(ar, ag, ab, 240))
        # Leading edge white pip
        draw.ellipse([px0 + fill_w - 3 * SS, py - SS, px0 + fill_w + 3 * SS, py + bar_h + SS], fill=(255, 255, 255, 255))

    # Status Telemetry readout below progress bar
    status_str = f"SYSTEM INITIALIZATION [{int(boot_pct * 100):3d}%]   //   DIRECTIVE: SECURE"
    if boot_pct >= 0.99:
        status_str = "SYSTEM PRIMED [100%]   //   ALL CORES NOMINAL"
    bbox_stat = draw.textbbox((0, 0), status_str, font=f_mono)
    stat_w = bbox_stat[2] - bbox_stat[0]
    draw.text(((W * SS - stat_w) / 2, py + 12 * SS), status_str, font=f_mono, fill=(*TEXT_DIM, 200))

    # Downsample with Lanczos for smooth subpixel anti-aliasing
    final_frame = img.resize((W, H), Image.Resampling.LANCZOS)
    return final_frame


_WORKER_CTX = {}


def init_worker(base_img, chrome_tex, tracker_a, tracker_b, accent_rgb, out_dir):
    _WORKER_CTX["base_img"] = base_img
    _WORKER_CTX["chrome_tex"] = chrome_tex
    _WORKER_CTX["tracker_a"] = tracker_a
    _WORKER_CTX["tracker_b"] = tracker_b
    _WORKER_CTX["accent_rgb"] = accent_rgb
    _WORKER_CTX["out_dir"] = Path(out_dir)


def render_frame_task(idx):
    ctx = _WORKER_CTX
    frame = render_single_frame(
        idx,
        ctx["base_img"],
        ctx["chrome_tex"],
        ctx["tracker_a"],
        ctx["tracker_b"],
        ctx["accent_rgb"],
    )
    fpath = ctx["out_dir"] / f"frame-{idx:03d}.png"
    frame.save(fpath, "PNG", optimize=True)
    return idx


def main():
    accent_hex = sys.argv[2] if len(sys.argv) > 2 else "cba6f7"
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("themes/synapseos-mauve")
    out_dir.mkdir(parents=True, exist_ok=True)

    accent_rgb = parse_hex_color(accent_hex)
    print(f"[+] Initializing Sleek Monolith Render: accent={accent_hex} frames={TOTAL_FRAMES} out={out_dir}")

    # Pre-render static backdrop & chrome texture
    base_img = render_monolith_backdrop(accent_rgb)
    chrome_tex = build_chrome_texture(accent_rgb)

    # Path trackers
    tracker_a = PathTracker(CUT_PATH_A, SS)
    tracker_b = PathTracker(CUT_PATH_B, SS)

    print("[+] Rendering 120 high-fidelity frames with ProcessPoolExecutor...")
    with ProcessPoolExecutor(
        initializer=init_worker,
        initargs=(base_img, chrome_tex, tracker_a, tracker_b, accent_rgb, str(out_dir)),
    ) as executor:
        for idx in executor.map(render_frame_task, range(TOTAL_FRAMES)):
            if idx % 20 == 0 or idx == TOTAL_FRAMES - 1:
                print(f"    -> Frame {idx:03d}/{TOTAL_FRAMES} complete")

    print(f"[✓] Successfully generated {TOTAL_FRAMES} frames in {out_dir}")


if __name__ == "__main__":
    main()
