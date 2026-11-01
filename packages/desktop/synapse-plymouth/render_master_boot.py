#!/usr/bin/env python3
"""
SynapseOS Master Boot Intro Compositor (v2 Remaster)
Polished Cinematic Boot Sequence:
1. Full cinematic pour & nozzle retraction (0.0s -> ~9.2s) with seamless soft edge vignetting onto #11111b
2. Ultra-smooth seamless camera ease & background dissolve to centered 3D chrome "SynapseOS" emblem
3. Multi-directional alternating specular light shimmer passes:
   - Pass 1: Left -> Right (L -> R)
   - Pass 2: Right -> Left (R -> L)
   - Pass 3: Left -> Right (L -> R)
   - Pass 4: Right -> Left (R -> L)
4. Clean hold on polished emblem with Catppuccin Mauve breathing glow ready for instant SDDM handoff
"""

import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

VIDEO_SRC = os.path.expanduser("~/Downloads/scene_grok_2026-10-31T15-21-06.mp4")
OUT_PREVIEW = os.path.expanduser("~/Desktop/SynapseOS_Flow_Assets/synapse-boot-final-preview.mp4")
OUT_FRAMES_DIR = "/tmp/synapse_boot_final_frames"
W, H = 1920, 1080
FPS = 25
BG_COLOR = (17, 17, 27) # #11111b

os.makedirs(OUT_FRAMES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUT_PREVIEW), exist_ok=True)

def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return 3 * t**2 - 2 * t**3

print("[1/5] Extracting video frames from source...")
raw_cmd = [
    "ffmpeg", "-v", "error", "-i", VIDEO_SRC,
    "-vf", f"scale=1080:1080,fps={FPS}",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
]
proc = subprocess.Popen(raw_cmd, stdout=subprocess.PIPE)
raw_bytes = proc.stdout.read()
proc.wait()

frame_size = 1080 * 1080 * 3
total_src_frames = len(raw_bytes) // frame_size
print(f"Total source frames at {FPS}fps: {total_src_frames}")

cut_frame = min(226, total_src_frames - 1)

# Extract reference end frame for emblem (at 1080x1080)
end_frame_bytes = raw_bytes[cut_frame * frame_size : (cut_frame + 1) * frame_size]
end_img_1080 = Image.frombytes("RGB", (1080, 1080), end_frame_bytes)

# Lighting Enhancement on the finished logo:
# Boost contrast, crispness, and specular metallic clarity
enhancer = ImageEnhance.Contrast(end_img_1080)
enhanced_1080 = enhancer.enhance(1.22)
enhancer = ImageEnhance.Sharpness(enhanced_1080)
enhanced_1080 = enhancer.enhance(1.35)
enhancer = ImageEnhance.Brightness(enhanced_1080)
enhanced_1080 = enhancer.enhance(1.06)

# Graded cool chrome speculars + Catppuccin Mauve rim
arr_1080 = np.asarray(enhanced_1080, dtype=np.float32)
lum_1080 = (arr_1080[..., 0] * 0.299 + arr_1080[..., 1] * 0.587 + arr_1080[..., 2] * 0.114) / 255.0
spec_mask_1080 = np.clip((lum_1080 - 0.38) / 0.5, 0, 1)[..., None]
arr_1080 += spec_mask_1080 * np.array([18, 22, 36], dtype=np.float32) # cool liquid chrome pop
arr_1080 = np.clip(arr_1080, 0, 255).astype(np.uint8)
graded_1080 = Image.fromarray(arr_1080, "RGB")

# Build ultra-smooth organic mask for emblem
emblem_mask = Image.new("L", (1080, 1080), 0)
d = ImageDraw.Draw(emblem_mask)
d.rounded_rectangle([85, 480, 995, 855], radius=100, fill=255)
d.rectangle([140, 840, 680, 900], fill=255) # dripping chrome droplets
emblem_mask = emblem_mask.filter(ImageFilter.GaussianBlur(28))

clean_canvas = Image.new("RGB", (W, H), BG_COLOR)
# Center emblem: source center (540, 675) -> target center (960, 540)
# Offset = (960 - 540, 540 - 675) = (420, -135)
clean_canvas.paste(graded_1080, (420, -135), emblem_mask)
clean_arr = np.asarray(clean_canvas, dtype=np.float32)

# Compute high-precision chrome luminance mask for light shimmer
lum = (clean_arr[..., 0] * 0.299 + clean_arr[..., 1] * 0.587 + clean_arr[..., 2] * 0.114) / 255.0
chrome_mask = np.clip((lum - 0.14) / 0.36, 0, 1)

# Build continuous soft edge mask for 1080 square in 1920x1080 canvas
vignette_mask_1080 = Image.new("L", (1080, 1080), 255)
vd = ImageDraw.Draw(vignette_mask_1080)
# Feather left & right 80px
for vx in range(80):
    alpha = int(255 * (vx / 80.0))
    vd.line([(vx, 0), (vx, 1080)], fill=alpha)
    vd.line([(1079 - vx, 0), (1079 - vx, 1080)], fill=alpha)

# Start ffmpeg encoder for preview mp4
enc_cmd = [
    "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
    "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
    "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "17",
    "-pix_fmt", "yuv420p", OUT_PREVIEW
]
encoder = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE)

print("[2/5] Rendering Phase A: High-res cinematic pour & retraction with feathered borders...")
for i in range(cut_frame):
    fbytes = raw_bytes[i * frame_size : (i + 1) * frame_size]
    fimg = Image.frombytes("RGB", (1080, 1080), fbytes)
    
    frame_canvas = Image.new("RGB", (W, H), BG_COLOR)
    frame_canvas.paste(fimg, (420, 0), vignette_mask_1080)
    encoder.stdin.write(frame_canvas.tobytes())

print("[3/5] Rendering Phase B: Seamless camera ease & background dissolve...")
trans_frames = 24
for t in range(trans_frames):
    p = ease_in_out(t / float(trans_frames))
    
    # Eased vertical shift from 0 to -135
    shift_y = int(p * (-135))
    
    fbytes = raw_bytes[(cut_frame - 1) * frame_size : cut_frame * frame_size]
    src_fimg = Image.frombytes("RGB", (1080, 1080), fbytes)
    
    base_src = Image.new("RGB", (W, H), BG_COLOR)
    base_src.paste(src_fimg, (420, shift_y), vignette_mask_1080)
    
    # Blend smoothly into clean enhanced emblem on #11111b
    blended = Image.blend(base_src, clean_canvas, p)
    encoder.stdin.write(blended.tobytes())

print("[4/5] Rendering Phase C: Quad-pass alternating light shimmer (L->R, R->L, L->R, R->L)...")
xx = np.arange(W, dtype=np.float32)[None, :]
yy = np.arange(H, dtype=np.float32)[:, None]

shimmer_passes = [
    ("L->R", 520, 1400, 0.42, 20),
    ("R->L", 1400, 520, -0.42, 20),
    ("L->R", 520, 1400, 0.42, 20),
    ("R->L", 1400, 520, -0.42, 20),
]

for direction, start_x, end_x, angle, num_f in shimmer_passes:
    print(f"  > Shimmer pass: {direction} ({num_f} frames)")
    for g in range(num_f):
        p = ease_in_out(g / float(num_f))
        sweep_x = start_x + (end_x - start_x) * p
        
        # Specular beam slanted along motion vector
        beam = np.exp(-(((xx - sweep_x) + (yy - 540) * angle) / 36.0) ** 2)
        
        # Intense starburst glint center
        dist = np.hypot(xx - sweep_x, (yy - 540) * 1.5)
        star = np.exp(-(dist / 30.0) ** 2) * 1.8
        
        # Specular light intensity modulated by chrome reflectivity
        light = (beam * 0.95 + star * 1.5) * chrome_mask
        
        flare_rgb = np.zeros((H, W, 3), np.float32)
        flare_rgb[..., 0] = light * 245 # R
        flare_rgb[..., 1] = light * 248 # G
        flare_rgb[..., 2] = light * 255 # B
        
        # Subtle violet/mauve outer corona glow on the sweep
        corona = np.exp(-(((xx - sweep_x) + (yy - 540) * angle) / 75.0) ** 2) * chrome_mask * 0.35
        flare_rgb[..., 0] += corona * 203
        flare_rgb[..., 1] += corona * 166
        flare_rgb[..., 2] += corona * 247
        
        frame_arr = np.clip(clean_arr + flare_rgb, 0, 255).astype(np.uint8)
        encoder.stdin.write(frame_arr.tobytes())

print("[5/5] Rendering Phase D: Clean hold on final emblem for SDDM handoff...")
final_img = Image.fromarray(clean_arr.astype(np.uint8), "RGB")
final_img.save(os.path.join(OUT_FRAMES_DIR, "final.png"))

# Save breathing glow for Plymouth theme
glow_mask = Image.fromarray((chrome_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(32))
glow_rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
glow_draw = Image.new("RGBA", (W, H), (203, 166, 247, 150)) # Catppuccin Mauve
glow_rgba.paste(glow_draw, (0, 0), glow_mask)
glow_rgba.save(os.path.join(OUT_FRAMES_DIR, "glow.png"))

# Hold still for 20 frames (~0.8s) before login screen takes over
for _ in range(20):
    encoder.stdin.write(final_img.tobytes())

encoder.stdin.close()
encoder.wait()

print(f"✔ Master boot sequence rendered successfully: {OUT_PREVIEW}")
