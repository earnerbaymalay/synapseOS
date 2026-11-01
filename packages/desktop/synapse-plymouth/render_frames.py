#!/usr/bin/env python3
"""
SynapseOS — Authentic 3D Liquid Chrome Monolith Plymouth Splash Renderer.
Extracts and renders the authentic 3D embossed chrome "SynapseOS" emblem matching the
boot video text size, texture, liquid reflections, and metallic colouring.
Renders seamless alternating specular light shimmer loop frames + breathing glow.
"""

import sys
import os
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

def ease_in_out(t):
    return 3 * t**2 - 2 * t**3

def main():
    if len(sys.argv) < 3:
        print("Usage: render_frames.py <output_dir> <hex_accent>")
        sys.exit(1)

    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    hex_color = sys.argv[2].lstrip("#")
    accent_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Find master plate image
    script_dir = Path(__file__).resolve().parent
    master_candidates = [
        Path("master_plate_960.png"),
        script_dir / "master_plate_960.png",
        script_dir / "src" / "master_plate_960.png"
    ]
    master_path = None
    for p in master_candidates:
        if p.exists():
            master_path = p
            break
            
    if not master_path:
        raise FileNotFoundError("master_plate_960.png not found")

    master_img = Image.open(master_path).convert("RGB")
    w, h = master_img.size # 960, 540
    arr = np.asarray(master_img, dtype=np.float32)

    # Save final.png
    master_img.save(out_dir / "final.png", optimize=True)

    # Compute high-precision chrome reflectivity mask
    lum = (arr[..., 0] * 0.299 + arr[..., 1] * 0.587 + arr[..., 2] * 0.114) / 255.0
    chrome_mask = np.clip((lum - 0.20) / 0.40, 0, 1)

    xx = np.arange(w, dtype=np.float32)[None, :]
    yy = np.arange(h, dtype=np.float32)[:, None]

    # Window mask around the 3D chrome letters & liquid puddle
    wx = np.clip(1.0 - (np.abs(xx - 480.0) - 340.0) / 40.0, 0, 1)
    wy = np.clip(1.0 - (np.abs(yy - 280.0) - 90.0) / 30.0, 0, 1)
    chrome_mask *= (wx * wy)

    # Save glow.png (breathing ambient accent glow)
    glow_mask = Image.fromarray((chrome_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    glow_rgba = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_fill = Image.new("RGBA", (w, h), (*accent_rgb, 160))
    glow_rgba.paste(glow_fill, (0, 0), glow_mask)
    glow_rgba.save(out_dir / "glow.png", optimize=True)

    # Render 40 looping specular reflection frames:
    # 20 frames Left -> Right, 20 frames Right -> Left
    center_y = 280.0
    passes = [
        (260.0, 700.0, 0.35, 20), # L -> R
        (700.0, 260.0, -0.35, 20), # R -> L
    ]

    frame_count = 0
    for start_x, end_x, slant, num_f in passes:
        for f in range(num_f):
            p = ease_in_out(f / float(num_f))
            sweep_x = start_x + (end_x - start_x) * p

            beam = np.exp(-(((xx - sweep_x) + (yy - center_y) * slant) / 24.0) ** 2)
            dist = np.hypot(xx - sweep_x, (yy - center_y) * 1.8)
            star = np.exp(-(dist / 20.0) ** 2) * 1.5

            light = (beam * 0.95 + star * 1.3) * chrome_mask

            flare_rgb = np.zeros((h, w, 3), np.float32)
            flare_rgb[..., 0] = light * 240
            flare_rgb[..., 1] = light * 245
            flare_rgb[..., 2] = light * 255

            corona = np.exp(-(((xx - sweep_x) + (yy - center_y) * slant) / 55.0) ** 2) * chrome_mask * 0.35
            flare_rgb[..., 0] += corona * accent_rgb[0]
            flare_rgb[..., 1] += corona * accent_rgb[1]
            flare_rgb[..., 2] += corona * accent_rgb[2]

            frame_arr = np.clip(arr + flare_rgb, 0, 255).astype(np.uint8)
            frame_name = f"frame-{frame_count:03d}.png"
            Image.fromarray(frame_arr, "RGB").save(out_dir / frame_name, optimize=True)
            frame_count += 1

    print(f"Generated {frame_count} frames, final.png, and glow.png for accent #{hex_color} in {out_dir}")

if __name__ == "__main__":
    main()
