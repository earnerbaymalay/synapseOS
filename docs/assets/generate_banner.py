#!/usr/bin/env python3
"""generate_banner.py — Generates the official SynapseOS Cyberdeck banner and responsive ASCII art.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "docs", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)
BANNER_PATH = os.path.join(ASSETS_DIR, "synapseos-banner.png")

# Dimensions
WIDTH = 1200
HEIGHT = 320

def create_banner():
    # 1. Base Canvas
    img = Image.new("RGBA", (WIDTH, HEIGHT), (14, 14, 21, 255))
    draw = ImageDraw.Draw(img)

    # 2. Radial Background Glow behind text (Mauve #cba6f7)
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    center_x, center_y = WIDTH // 2, HEIGHT // 2 - 15
    for r in range(240, 0, -8):
        alpha = int((1 - r / 240) * 45)
        glow_draw.ellipse(
            (center_x - r * 2.2, center_y - r * 0.9, center_x + r * 2.2, center_y + r * 0.9),
            fill=(203, 166, 247, alpha)
        )
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 3. Outer Chamfered Cyberdeck Frame
    margin = 16
    draw.rounded_rectangle(
        [margin, margin, WIDTH - margin, HEIGHT - margin],
        radius=18,
        outline=(49, 50, 68, 255),
        width=2
    )
    # Corner Accent Brackets (Electric Mauve)
    bracket_len = 36
    # Top-Left
    draw.line([margin + 8, margin, margin + 8 + bracket_len, margin], fill=(203, 166, 247, 255), width=3)
    draw.line([margin, margin + 8, margin, margin + 8 + bracket_len], fill=(203, 166, 247, 255), width=3)
    # Top-Right
    draw.line([WIDTH - margin - 8 - bracket_len, margin, WIDTH - margin - 8, margin], fill=(203, 166, 247, 255), width=3)
    draw.line([WIDTH - margin, margin + 8, WIDTH - margin, margin + 8 + bracket_len], fill=(203, 166, 247, 255), width=3)
    # Bottom-Left
    draw.line([margin + 8, HEIGHT - margin, margin + 8 + bracket_len, HEIGHT - margin], fill=(203, 166, 247, 255), width=3)
    draw.line([margin, HEIGHT - margin - 8 - bracket_len, margin, HEIGHT - margin - 8], fill=(203, 166, 247, 255), width=3)
    # Bottom-Right
    draw.line([WIDTH - margin - 8 - bracket_len, HEIGHT - margin, WIDTH - margin - 8, HEIGHT - margin], fill=(203, 166, 247, 255), width=3)
    draw.line([WIDTH - margin, HEIGHT - margin - 8 - bracket_len, WIDTH - margin, HEIGHT - margin - 8], fill=(203, 166, 247, 255), width=3)

    # 4. Typography
    font_path_bold = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-ExtraBold.ttf"
    font_path_reg = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
    font_path_italic = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Italic.ttf"

    main_font = ImageFont.truetype(font_path_bold, 78)
    sub_font = ImageFont.truetype(font_path_bold, 17)
    quote_font = ImageFont.truetype(font_path_italic, 13)

    text = "SYNAPSE  OS"
    bbox = draw.textbbox((0, 0), text, font=main_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = 70

    # Text Shadow & Soft Mauve Glow
    text_glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    tg_draw = ImageDraw.Draw(text_glow)
    for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)]:
        tg_draw.text((text_x + ox, text_y + oy), text, font=main_font, fill=(203, 166, 247, 120))
    text_glow = text_glow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, text_glow)
    draw = ImageDraw.Draw(img)

    # Main Text (Liquid Chrome to Mauve Gradient)
    draw.text((text_x, text_y + 3), text, font=main_font, fill=(24, 24, 37, 255)) # depth
    draw.text((text_x, text_y), text, font=main_font, fill=(245, 224, 220, 255)) # highlight

    # Center Space Singularity Torus Dot
    # Position dot right between SYNAPSE and OS
    space_x = text_x + int(text_w * 0.765)
    space_y = text_y + 40
    draw.ellipse([space_x - 6, space_y - 6, space_x + 6, space_y + 6], fill=(203, 166, 247, 255), outline=(255, 255, 255, 255), width=2)

    # Subtitle Banner
    sub_text = "AI-NATIVE LINUX  ·  BORE SCHEDULER  ·  CYBER RESILIENCE"
    s_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    s_w = s_bbox[2] - s_bbox[0]
    s_x = (WIDTH - s_w) // 2
    s_y = text_y + text_h + 38
    draw.text((s_x, s_y), sub_text, font=sub_font, fill=(205, 214, 244, 255))

    # Philosophy Quote
    quote_text = "“System aims for minimal if not 0 telemetry and prioritises anonymisation without degradation of service.”"
    q_bbox = draw.textbbox((0, 0), quote_text, font=quote_font)
    q_w = q_bbox[2] - q_bbox[0]
    q_x = (WIDTH - q_w) // 2
    q_y = s_y + 32
    draw.text((q_x, q_y), quote_text, font=quote_font, fill=(186, 194, 222, 255))

    img.save(BANNER_PATH, "PNG", optimize=True)
    print(f"Generated banner image at: {BANNER_PATH}")

if __name__ == "__main__":
    create_banner()
