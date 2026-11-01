#!/usr/bin/env python3
"""SynapseOS cinematic boot intro compositor.

Timeline (25 fps, canvas 1280x640 authored for 1080p):
  A  laser-cut S  — graded source clip (Veo render), screen-blended onto obsidian
  B  handoff      — specular flash hides the swap to the exact vector S
  C  settle       — S morphs to true proportions and slides into wordmark position
  D  engrave      — Y N A P S E laser-revealed left to right, hot kerf cooling to silver
  E  sweep        — one specular pass over the silver wordmark
Then the Plymouth script holds final.png and breathes glow.png until boot completes.

Usage: compose_intro.py SOURCE.mp4 OUT_DIR [ACCENT_HEX] [--preview out.mp4]
"""

import colorsys
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import wordmark as wm

FPS = 25
W, H = 1280, 640
BG = np.array([17, 17, 27], np.float32)           # #11111b, matches script background

SRC_SIZE = 720                                     # graded square source
SRC_SPEED = 1.25
SRC_HANDOFF = 5.5                                  # seconds: S finished, lasers retracted
SRC_S_BBOX = (206, 262, 559, 485)                  # S bounds in the source at handoff
VID = 640                                          # source drawn at this size, centred

N_A = int(SRC_HANDOFF / SRC_SPEED * FPS)           # 110
N_B, N_C, N_E = 8, 15, 15
LETTER_STAGGER, LETTER_DUR = 2.5, 7.5              # frames
N_D = int(LETTER_STAGGER * 5 + LETTER_DUR) + 2     # 22
TOTAL = N_A + N_B + N_C + N_D + N_E

WM_WIDTH = 960.0


def ease(k):
    k = min(1.0, max(0.0, k))
    return 4 * k ** 3 if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def ease_out(k):
    k = min(1.0, max(0.0, k))
    return 1 - (1 - k) ** 3


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- source video
def read_source(path):
    """Decode the source once into a list of float32 frames (SRC_SIZE^2 RGB)."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vf",
           f"scale={SRC_SIZE}:{SRC_SIZE}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    n = len(raw) // (SRC_SIZE * SRC_SIZE * 3)
    arr = np.frombuffer(raw, np.uint8)[: n * SRC_SIZE * SRC_SIZE * 3]
    return arr.reshape(n, SRC_SIZE, SRC_SIZE, 3), _src_fps(path)


def _src_fps(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate", "-of", "csv=p=0", str(path)],
                         check=True, capture_output=True, text=True).stdout.strip()
    a, b = out.split("/")
    return float(a) / float(b)


def accent_shift(rgb, accent):
    """Rotate the mauve laser light toward the theme accent (identity for mauve)."""
    target_h = colorsys.rgb_to_hsv(*[c / 255 for c in accent])[0]
    mauve_h = colorsys.rgb_to_hsv(203 / 255, 166 / 255, 247 / 255)[0]
    if abs(target_h - mauve_h) < 0.01:
        return rgb
    f = rgb / 255.0
    mx, mn = f.max(-1), f.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    # Only strongly coloured pixels in the violet/magenta band move.
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    violet = np.clip((b + r * 0.5 - g * 1.4) * 2.0, 0, 1) * np.clip((sat - 0.15) * 3, 0, 1)
    lum = mx[..., None]
    tint = np.array(accent, np.float32) / 255.0
    shifted = lum * (tint / tint.max()) * (0.6 + 0.4 * sat[..., None]) + (1 - sat[..., None]) * lum * 0.4
    return (f * (1 - violet[..., None]) + np.clip(shifted, 0, 1) * violet[..., None]) * 255.0


def vignette_mask():
    yy, xx = np.mgrid[0:VID, 0:VID].astype(np.float32)
    c = (VID - 1) / 2
    r = np.hypot((xx - c) / c, (yy - c) / c * 1.05)
    m = np.clip((1.0 - r) / 0.35, 0, 1) ** 1.5
    m[int(VID * 0.80):] *= np.linspace(1, 0, VID - int(VID * 0.80))[:, None]  # hide slab rubble
    return m[..., None]


def video_layer(frames, src_fps, t_src, accent, vmask):
    i = min(len(frames) - 1, int(round(t_src * src_fps)))
    fr = np.asarray(Image.fromarray(frames[i]).resize((VID, VID), Image.LANCZOS), np.float32)
    fr = accent_shift(fr, accent)
    layer = np.zeros((H, W, 3), np.float32)
    x0, y0 = (W - VID) // 2, (H - VID) // 2
    y_lo, y_hi = max(0, -y0), min(VID, H - y0)
    layer[max(0, y0):max(0, y0) + (y_hi - y_lo), x0:x0 + VID] = (fr * vmask)[y_lo:y_hi]
    return layer


def screen(base, top, amount=1.0):
    t = top / 255.0 * amount
    return 255.0 - (255.0 - base) * (1.0 - t)


# ------------------------------------------------------------------ geometry
def s_box_in_canvas():
    k = VID / SRC_SIZE
    x0, y0 = (W - VID) / 2, (H - VID) / 2
    bx0, by0, bx1, by1 = SRC_S_BBOX
    return x0 + bx0 * k, y0 + by0 * k, x0 + bx1 * k, y0 + by1 * k


def final_layout():
    glyphs, tw = wm.layout()
    sc = WM_WIDTH / tw
    return glyphs, sc, (W - tw * sc) / 2, (H - wm.CAP * sc) / 2


def s_mask_box(box, ss=3):
    """Mask of the vector S stretched into an arbitrary box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    glyphs, _ = wm.layout("S")
    sx, sy = (x1 - x0) / 63.0, (y1 - y0) / wm.CAP
    big = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(big)
    for _, _, _, polys, _ in glyphs:
        for p in polys:
            d.polygon([((x0 + x * sx) * ss, (y0 + y * sy) * ss) for x, y in p], fill=255)
    return big.resize((W, H), Image.LANCZOS)


# --------------------------------------------------------------- compositing
def save_frame(rgb, path):
    """256-colour palette PNG: visually identical on these dark frames at ~55% of the size."""
    Image.fromarray(rgb).quantize(256, method=Image.Quantize.MEDIANCUT,
                                  dither=Image.Dither.FLOYDSTEINBERG).save(path, optimize=True)


def over(base, rgba):
    a = np.asarray(rgba, np.float32)
    al = a[..., 3:4] / 255.0
    return base * (1 - al) + a[..., :3] * al


def add_glow(base, mask, radius, color, strength):
    g = wm.fblur(np.asarray(mask, np.float32) / 255.0, radius) * strength
    return screen(base, g[..., None] * np.array(color, np.float32))


def render(frames, src_fps, accent, out_dir, preview=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    vmask = vignette_mask()
    glyphs, sc, fx, fy = final_layout()
    cap = wm.CAP * sc
    start_box = s_box_in_canvas()
    end_box = (fx, fy, fx + 63 * sc, fy + cap)
    full_mask = wm.glyph_mask((W, H), glyphs, sc, fx, fy, ss=3)
    letter_masks = [wm.glyph_mask((W, H), glyphs, sc, fx, fy, only={i}, ss=3) for i in range(7)]
    full_chrome = wm.chrome(full_mask, fy, cap, rim=accent)
    hot = np.array([255, 244, 236], np.float32)
    acc = np.array(accent, np.float32)

    ff = None
    if preview:
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf",
                               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x11111b,tpad=stop_mode=clone:stop_duration=2.5",
                               "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(preview)],
                              stdin=subprocess.PIPE)

    xs = np.arange(W, dtype=np.float32)[None, :]
    last = None
    for f in range(TOTAL):
        img = np.broadcast_to(BG, (H, W, 3)).copy()

        if f < N_A + N_B:
            t_src = min(SRC_HANDOFF, f / FPS * SRC_SPEED)
            v = video_layer(frames, src_fps, t_src, accent, vmask)
            fade = 1.0 if f < N_A else 1.0 - ease((f - N_A) / N_B)
            img = screen(img, v, fade)

        if f >= N_A:
            # Vector S: stretched to the video S, then settles into the wordmark slot.
            k = 0.0 if f < N_A + N_B else ease((f - N_A - N_B) / N_C)
            box = tuple(a + (b - a) * k for a, b in zip(start_box, end_box))
            m = s_mask_box(box) if k < 1.0 else letter_masks[0]
            appear = ease_out((f - N_A) / N_B) if f < N_A + N_B else 1.0
            ch = wm.chrome(m, box[1], box[3] - box[1], rim=accent)
            arr = np.asarray(ch, np.float32)
            arr[..., 3] *= appear
            img = over(img, Image.fromarray(arr.astype(np.uint8)))
            img = add_glow(img, m, 26, acc * 0.5, 0.35 * appear)
            if f < N_A + N_B + 4:
                # Specular handoff flash travelling across the S.
                p = (f - N_A) / (N_B + 4)
                sx = box[0] + (box[2] - box[0] + 120) * p - 60
                band = np.exp(-((xs - sx) / 40.0) ** 2) * (np.asarray(m, np.float32) / 255.0)
                img = screen(img, band[..., None] * hot * 0.9)

        d0 = N_A + N_B + N_C
        if f >= d0:
            for li in range(1, 7):
                st = d0 + (li - 1) * LETTER_STAGGER
                if f < st:
                    continue
                k = (f - st) / LETTER_DUR
                gm = np.asarray(letter_masks[li], np.float32) / 255.0
                cols = np.nonzero(gm.max(0) > 0.01)[0]
                gx0, gx1 = cols.min(), cols.max()
                edge = gx0 + (gx1 - gx0 + 24) * ease_out(min(k, 1.0)) - 12
                reveal = np.clip((edge - xs) / 6.0, 0, 1)
                vis = gm * reveal
                chrome = np.asarray(wm.chrome(letter_masks[li], fy, cap, rim=accent), np.float32)
                # Kerf heat: hot just behind the cut edge, cooling to silver.
                heat = np.exp(-np.clip(edge - xs, 0, None) / 38.0) * max(0.0, 1.2 - k * 0.9)
                heat = np.clip(heat, 0, 1)[..., None]
                col = chrome[..., :3] * (1 - heat) + (hot * 0.6 + acc * 0.4) * heat
                al = vis[..., None]
                img = img * (1 - al) + col * al
                if k < 1.0:
                    beam = np.exp(-((xs - edge) / 3.0) ** 2) * np.clip(gm.max(0, keepdims=True) * 1.0, 0, 1)
                    rows = (gm.max(1) > 0.01)[:, None].astype(np.float32)
                    glow_line = np.exp(-((xs - edge) / 14.0) ** 2) * rows
                    img = screen(img, (beam * rows)[..., None] * hot + glow_line[..., None] * acc * 0.55)

        e0 = d0 + N_D
        if f >= e0:
            p = (f - e0) / N_E
            sweep_x = fx - 200 + (WM_WIDTH + 400) * ease(p)
            sw = np.asarray(wm.chrome(full_mask, fy, cap, rim=accent, sweep=sweep_x), np.float32)
            img = over(img, Image.fromarray(sw.astype(np.uint8)))

        if f >= d0:
            settle = ease_out((f - d0) / (N_D + N_E))
            img = add_glow(img, full_mask, 34, acc * 0.45, 0.25 * settle)

        out = np.clip(img, 0, 255).astype(np.uint8)
        save_frame(out, out_dir / f"frame-{f:03d}.png")
        if ff:
            ff.stdin.write(out.tobytes())
        last = out

    # Hold assets for the script's breathing loop.
    save_frame(last, out_dir / "final.png")
    g = wm.fblur(np.asarray(full_mask, np.float32) / 255.0, 30)
    glow = np.zeros((H, W, 4), np.uint8)
    glow[..., :3] = accent
    glow[..., 3] = np.clip(g * 255 * 0.55, 0, 255).astype(np.uint8)
    Image.fromarray(glow, "RGBA").save(out_dir / "glow.png", optimize=True)

    if ff:
        ff.stdin.close()
        ff.wait()
    return TOTAL


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
        args = [a for a in args if a != preview]
    src, out_dir = args[0], args[1]
    accent = hex_rgb(args[2]) if len(args) > 2 else (203, 166, 247)
    frames, src_fps = read_source(src)
    n = render(frames, src_fps, accent, out_dir, preview)
    print(f"{n} frames -> {out_dir}")


if __name__ == "__main__":
    main()
