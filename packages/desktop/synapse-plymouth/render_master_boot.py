#!/usr/bin/env python3
"""
SynapseOS Master Boot Intro Compositor (v3 Master Remaster)
Polished Cinematic Boot Sequence:
1. Full cinematic pour & nozzle retraction with seamless soft edge vignetting onto #11111b
2. Ultra-smooth seamless camera ease & background transition to centered 3D chrome "SynapseOS" emblem
3. Studio lighting grading on the finished 3D liquid chrome logo
4. Alternating specular light shimmer passes (6 passes total: L->R, R->L, L->R, R->L, L->R, R->L)
5. Clean hold on polished emblem with Catppuccin Mauve breathing glow ready for SDDM handoff
"""

import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

VIDEO_SRC = os.path.expanduser("~/Downloads/scene_grok_2026-10-31T15-21-06.mp4")
OUT_PREVIEW = os.path.expanduser("~/Desktop/SynapseOS_Flow_Assets/synapse-boot-final-preview.mp4")
W, H = 1920, 1080
FPS = 24
BG_COLOR = (17, 17, 27) # #11111b

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

# Frame at end of video (frame 240)
end_frame_idx = min(238, total_src_frames - 1)
end_frame_bytes = raw_bytes[end_frame_idx * frame_size : (end_frame_idx + 1) * frame_size]
end_img_1080 = Image.frombytes("RGB", (1080, 1080), end_frame_bytes)

# Studio Lighting Enhancement on the finished logo:
enhancer = ImageEnhance.Contrast(end_img_1080)
graded_1080 = enhancer.enhance(1.08)
enhancer = ImageEnhance.Brightness(graded_1080)
graded_1080 = enhancer.enhance(1.04)
enhancer = ImageEnhance.Color(graded_1080)
graded_1080 = enhancer.enhance(1.05)

# Build seamless perimeter vignette masks
# Full frame vignette (for pour phase)
vignette_pour = Image.new("L", (1080, 1080), 255)
vd = ImageDraw.Draw(vignette_pour)
for x in range(90):
    a = int(255 * (x / 90.0)**1.6)
    vd.line([(x, 0), (x, 1080)], fill=a)
    vd.line([(1079 - x, 0), (1079 - x, 1080)], fill=a)

# Centered plate vignette (for emblem phase)
vignette_plate = Image.new("L", (1080, 1080), 255)
vd2 = ImageDraw.Draw(vignette_plate)
for x in range(90):
    a = int(255 * (x / 90.0)**1.6)
    vd2.line([(x, 0), (x, 1080)], fill=a)
    vd2.line([(1079 - x, 0), (1079 - x, 1080)], fill=a)
for y in range(70):
    a = int(255 * (y / 70.0)**1.6)
    vd2.line([(0, 1079 - y), (1080, 1079 - y)], fill=a)
for y in range(220):
    a = int(255 * (y / 220.0)**1.8)
    vd2.line([(0, y), (1080, y)], fill=a)

# Clean centered canvas
clean_canvas = Image.new("RGB", (W, H), BG_COLOR)
clean_canvas.paste(graded_1080, (420, -134), vignette_plate)
clean_arr = np.asarray(clean_canvas, dtype=np.float32)

# Compute high-precision chrome mask
lum = (clean_arr[..., 0] * 0.299 + clean_arr[..., 1] * 0.587 + clean_arr[..., 2] * 0.114) / 255.0
chrome_mask = np.clip((lum - 0.16) / 0.35, 0, 1)

# Start ffmpeg encoder for preview mp4
enc_cmd = [
    "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
    "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
    "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p", OUT_PREVIEW
]
encoder = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE)

# Phase A: Cinematic Pour & Retraction (frames 0 to 216 ~9.0s)
cut_frame = min(216, total_src_frames - 25)
print(f"[2/5] Rendering Phase A: High-res cinematic pour (frames 0..{cut_frame})...")
for i in range(cut_frame):
    fbytes = raw_bytes[i * frame_size : (i + 1) * frame_size]
    fimg = Image.frombytes("RGB", (1080, 1080), fbytes)
    frame_canvas = Image.new("RGB", (W, H), BG_COLOR)
    frame_canvas.paste(fimg, (420, 0), vignette_pour)
    encoder.stdin.write(frame_canvas.tobytes())

# Phase B: Seamless Camera Ease & Background Transition (28 frames)
print("[3/5] Rendering Phase B: Seamless camera ease & transition...")
trans_frames = 28
for t in range(trans_frames):
    p = ease_in_out(t / float(trans_frames))
    src_idx = min(cut_frame + t, total_src_frames - 1)
    fbytes = raw_bytes[src_idx * frame_size : (src_idx + 1) * frame_size]
    src_fimg = Image.frombytes("RGB", (1080, 1080), fbytes)
    
    # Slight grading ease
    enh = ImageEnhance.Contrast(src_fimg)
    src_graded = enh.enhance(1.0 + 0.08 * p)
    
    # Smooth vertical shift from 0 to -134
    shift_y = int(p * (-134))
    
    # Smooth blend between pour vignette and plate vignette
    curr_vignette = Image.blend(vignette_pour, vignette_plate, p)
    
    frame_canvas = Image.new("RGB", (W, H), BG_COLOR)
    frame_canvas.paste(src_graded, (420, shift_y), curr_vignette)
    
    # Gentle blend with clean plate at the tail
    if p > 0.4:
        blend_factor = (p - 0.4) / 0.6
        frame_canvas = Image.blend(frame_canvas, clean_canvas, blend_factor)
        
    encoder.stdin.write(frame_canvas.tobytes())

# Phase C: 6 Alternating Specular Light Shimmer Passes
# L->R, R->L, L->R, R->L, L->R, R->L
print("[4/5] Rendering Phase C: 6 alternating specular light shimmer passes...")
xx = np.arange(W, dtype=np.float32)[None, :]
yy = np.arange(H, dtype=np.float32)[:, None]

shimmer_passes = [
    ("L->R", 520, 1380, 0.35, 18),
    ("R->L", 1380, 520, -0.35, 18),
    ("L->R", 520, 1380, 0.35, 18),
    ("R->L", 1380, 520, -0.35, 18),
    ("L->R", 520, 1380, 0.35, 18),
    ("R->L", 1380, 520, -0.35, 18),
]

for direction, start_x, end_x, angle, num_f in shimmer_passes:
    print(f"  > Shimmer pass: {direction} ({num_f} frames)")
    for g in range(num_f):
        p = ease_in_out(g / float(num_f))
        sweep_x = start_x + (end_x - start_x) * p
        
        # Specular light beam
        beam = np.exp(-(((xx - sweep_x) + (yy - 540) * angle) / 38.0) ** 2)
        dist = np.hypot(xx - sweep_x, (yy - 540) * 1.8)
        star = np.exp(-(dist / 30.0) ** 2) * 1.6
        
        light = (beam * 0.95 + star * 1.4) * chrome_mask
        
        flare_rgb = np.zeros((H, W, 3), np.float32)
        flare_rgb[..., 0] = light * 240
        flare_rgb[..., 1] = light * 245
        flare_rgb[..., 2] = light * 255
        
        # Mauve reflection on chrome
        corona = np.exp(-(((xx - sweep_x) + (yy - 540) * angle) / 85.0) ** 2) * chrome_mask * 0.35
        flare_rgb[..., 0] += corona * 203
        flare_rgb[..., 1] += corona * 166
        flare_rgb[..., 2] += corona * 247
        
        frame_arr = np.clip(clean_arr + flare_rgb, 0, 255).astype(np.uint8)
        encoder.stdin.write(frame_arr.tobytes())

# Phase D: Clean Hold with Ambient Glow for SDDM handoff
print("[5/5] Rendering Phase D: Clean hold with breathing glow...")
final_img = Image.fromarray(clean_arr.astype(np.uint8), "RGB")

# Mauve breathing glow
glow_mask = Image.fromarray((chrome_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(32))
glow_rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
glow_draw = Image.new("RGBA", (W, H), (203, 166, 247, 140)) # Catppuccin Mauve
glow_rgba.paste(glow_draw, (0, 0), glow_mask)

for hold_f in range(24): # 1.0s hold
    pulse = 0.5 + 0.5 * np.sin(hold_f / 24.0 * np.pi)
    curr_glow = glow_rgba.copy()
    # Apply alpha modulation
    alpha = curr_glow.split()[3].point(lambda a: int(a * pulse * 0.6))
    curr_glow.putalpha(alpha)
    
    hold_frame = final_img.copy()
    hold_frame.paste(curr_glow, (0, 0), curr_glow)
    encoder.stdin.write(hold_frame.tobytes())

encoder.stdin.close()
proc = encoder.wait()
print(f"✔ Remastered boot sequence successfully written to: {OUT_PREVIEW}")
