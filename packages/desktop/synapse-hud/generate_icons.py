#!/usr/bin/env python3
"""generate_icons.py — Generator for SynapseOS 4 Metallic Icon Themes.

Generates:
  1. Synapse-Liquid-Chrome   (Mirror-polished liquid chrome, 45° diamond chamfers)
  2. Synapse-Smoked-Obsidian (Mirror jet-black ceramic, knurled rim, neon mauve conduit)
  3. Synapse-Radial-Tungsten (Anisotropic lathe-milled tungsten, orbital purple donut)
  4. Synapse-Aerospace-Billet(Hairline brushed titanium plate, satin mauve, micro-rivets)

Each theme inherits from Hatter-Purple, Papirus-Dark, hicolor.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DEST = os.path.join(BASE_DIR, "icons")

THEMES = {
    "Synapse-Liquid-Chrome": {
        "comment": "SynapseOS Liquid Mauve Chrome — High-gloss mirror finish & diamond chamfers",
        "style": "chrome"
    },
    "Synapse-Smoked-Obsidian": {
        "comment": "SynapseOS Smoked Obsidian — Mirror black ceramic & neon mauve conduit",
        "style": "obsidian"
    },
    "Synapse-Radial-Tungsten": {
        "comment": "SynapseOS Radial Milled Tungsten — Anisotropic lathe grain & singularity torus",
        "style": "tungsten"
    },
    "Synapse-Aerospace-Billet": {
        "comment": "SynapseOS Aerospace Billet — Brushed titanium slab, satin mauve & micro-bolts",
        "style": "billet"
    }
}

# Core Application & Place Glyphs (Centered in 128x128 canvas)
GLYPHS = {
    "synapse-hud": """
        <!-- Synapse AI Core / Orbital HUD Glyph -->
        <circle cx="64" cy="64" r="26" fill="none" stroke="{accent}" stroke-width="3.5" stroke-dasharray="32 10 16 10"/>
        <circle cx="64" cy="64" r="16" fill="none" stroke="{fg}" stroke-width="2.5"/>
        <circle cx="64" cy="64" r="6" fill="{accent}"/>
        <path d="M 64 24 L 64 34 M 64 94 L 64 104 M 24 64 L 34 64 M 94 64 L 104 64" stroke="{fg}" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "synapse-settings": """
        <!-- Precision Milled Control Center / Gear -->
        <path d="M 64 38 L 68 44 L 76 42 L 78 49 L 85 50 L 84 58 L 91 61 L 88 68 L 93 73 L 88 78 L 91 85 L 84 88 L 85 96 L 78 97 L 76 104 L 68 102 L 64 108 L 60 102 L 52 104 L 50 97 L 43 96 L 44 88 L 37 85 L 40 78 L 35 73 L 40 68 L 37 61 L 44 58 L 43 50 L 50 49 L 52 42 L 60 44 Z" fill="none" stroke="{accent}" stroke-width="3" stroke-linejoin="round"/>
        <circle cx="64" cy="73" r="14" fill="none" stroke="{fg}" stroke-width="3"/>
        <circle cx="64" cy="73" r="6" fill="{accent}"/>
    """,
    "synapse-notes": """
        <!-- Brain Scratchpad / Markdown Note -->
        <rect x="42" y="36" width="44" height="56" rx="4" fill="none" stroke="{fg}" stroke-width="3"/>
        <path d="M 52 50 L 76 50 M 52 62 L 76 62 M 52 74 L 68 74" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
        <polygon points="76,36 86,46 76,46" fill="{accent}"/>
    """,
    "synapse-setup": """
        <!-- System Setup / Hex Tuning Wrench & Spark -->
        <path d="M 44 44 L 84 84 M 54 38 L 90 74 M 84 40 L 92 48 L 86 54 L 78 46 Z" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="48" cy="80" r="10" fill="none" stroke="{fg}" stroke-width="3"/>
        <circle cx="48" cy="80" r="4" fill="{accent}"/>
    """,
    "synapse-welcome": """
        <!-- Welcome Spark / Cyberdeck Compass -->
        <polygon points="64,32 72,56 96,64 72,72 64,96 56,72 32,64 56,56" fill="{accent}" stroke="{fg}" stroke-width="2" stroke-linejoin="round"/>
        <circle cx="64" cy="64" r="5" fill="#ffffff"/>
    """,
    "utilities-terminal": """
        <!-- Cyberdeck Terminal Prompt -->
        <path d="M 42 48 L 56 62 L 42 76" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="62" y1="78" x2="86" y2="78" stroke="{fg}" stroke-width="4" stroke-linecap="round"/>
    """,
    "web-browser": """
        <!-- Hardened Zero-Telemetry Shielded Globe -->
        <circle cx="64" cy="64" r="28" fill="none" stroke="{fg}" stroke-width="3"/>
        <ellipse cx="64" cy="64" rx="14" ry="28" fill="none" stroke="{accent}" stroke-width="2.5"/>
        <line x1="36" y1="64" x2="92" y2="64" stroke="{accent}" stroke-width="2.5"/>
        <line x1="42" y1="50" x2="86" y2="50" stroke="{fg}" stroke-width="1.8"/>
        <line x1="42" y1="78" x2="86" y2="78" stroke="{fg}" stroke-width="1.8"/>
    """,
    "system-file-manager": """
        <!-- Machined Storage Vault -->
        <rect x="36" y="44" width="56" height="42" rx="4" fill="none" stroke="{fg}" stroke-width="3"/>
        <path d="M 36 54 L 92 54" stroke="{accent}" stroke-width="2.5"/>
        <circle cx="64" cy="68" r="6" fill="none" stroke="{accent}" stroke-width="2.5"/>
        <line x1="64" y1="74" x2="64" y2="80" stroke="{fg}" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "galculator": """
        <!-- Precision Arithmetic Node -->
        <rect x="40" y="34" width="48" height="60" rx="5" fill="none" stroke="{fg}" stroke-width="3"/>
        <rect x="46" y="42" width="36" height="12" rx="2" fill="{accent}" opacity="0.3" stroke="{accent}" stroke-width="1.5"/>
        <circle cx="50" cy="64" r="3" fill="{fg}"/>
        <circle cx="64" cy="64" r="3" fill="{fg}"/>
        <circle cx="78" cy="64" r="3" fill="{accent}"/>
        <circle cx="50" cy="76" r="3" fill="{fg}"/>
        <circle cx="64" cy="76" r="3" fill="{fg}"/>
        <circle cx="78" cy="76" r="3" fill="{accent}"/>
        <circle cx="50" cy="86" r="3" fill="{fg}"/>
        <circle cx="64" cy="86" r="3" fill="{fg}"/>
        <rect x="74" y="83" width="8" height="6" rx="2" fill="{accent}"/>
    """,
    "mousepad": """
        <!-- Tabbed Text Editor -->
        <rect x="38" y="36" width="52" height="56" rx="4" fill="none" stroke="{fg}" stroke-width="3"/>
        <path d="M 46 48 L 82 48 M 46 58 L 74 58 M 46 68 L 80 68 M 46 78 L 64 78" stroke="{accent}" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "preferences-system": """
        <!-- System Control Knobs / Sliders -->
        <line x1="46" y1="38" x2="46" y2="90" stroke="{fg}" stroke-width="3" stroke-linecap="round"/>
        <line x1="64" y1="38" x2="64" y2="90" stroke="{fg}" stroke-width="3" stroke-linecap="round"/>
        <line x1="82" y1="38" x2="82" y2="90" stroke="{fg}" stroke-width="3" stroke-linecap="round"/>
        <circle cx="46" cy="54" r="6" fill="{accent}" stroke="{fg}" stroke-width="1.5"/>
        <circle cx="64" cy="74" r="6" fill="{accent}" stroke="{fg}" stroke-width="1.5"/>
        <circle cx="82" cy="48" r="6" fill="{accent}" stroke="{fg}" stroke-width="1.5"/>
    """,
    "folder": """
        <!-- Sheet Titanium / Satin Mauve Folder -->
        <path d="M 32 44 L 52 44 L 58 50 L 96 50 C 98 50 100 52 100 54 L 100 88 C 100 90 98 92 96 92 L 32 92 C 30 92 28 90 28 88 L 28 48 C 28 46 30 44 32 44 Z" fill="none" stroke="{fg}" stroke-width="3"/>
        <path d="M 28 58 L 100 58 L 94 88 C 93.5 90 92 91 90 91 L 38 91 C 36 91 34.5 90 34 88 Z" fill="{accent}" opacity="0.25" stroke="{accent}" stroke-width="2.5"/>
    """,
    "folder-documents": """
        <path d="M 32 44 L 52 44 L 58 50 L 96 50 C 98 50 100 52 100 54 L 100 88 C 100 90 98 92 96 92 L 32 92 C 30 92 28 90 28 88 L 28 48 C 28 46 30 44 32 44 Z" fill="none" stroke="{fg}" stroke-width="3"/>
        <path d="M 52 64 L 76 64 M 52 72 L 76 72 M 52 80 L 68 80" stroke="{accent}" stroke-width="2.5" stroke-linecap="round"/>
    """,
    "folder-download": """
        <path d="M 32 44 L 52 44 L 58 50 L 96 50 C 98 50 100 52 100 54 L 100 88 C 100 90 98 92 96 92 L 32 92 C 30 92 28 90 28 88 L 28 48 C 28 46 30 44 32 44 Z" fill="none" stroke="{fg}" stroke-width="3"/>
        <path d="M 64 62 L 64 80 M 56 74 L 64 82 L 72 74" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    """,
    "folder-projects": """
        <path d="M 32 44 L 52 44 L 58 50 L 96 50 C 98 50 100 52 100 54 L 100 88 C 100 90 98 92 96 92 L 32 92 C 30 92 28 90 28 88 L 28 48 C 28 46 30 44 32 44 Z" fill="none" stroke="{fg}" stroke-width="3"/>
        <polygon points="64,62 74,78 54,78" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linejoin="round"/>
    """,
    "user-home": """
        <!-- Cyberdeck Home Base -->
        <path d="M 38 66 L 64 44 L 90 66 L 90 88 C 90 90 88 92 86 92 L 42 92 C 40 92 38 90 38 88 Z" fill="none" stroke="{fg}" stroke-width="3" stroke-linejoin="round"/>
        <rect x="56" y="70" width="16" height="22" rx="2" fill="{accent}" opacity="0.3" stroke="{accent}" stroke-width="2"/>
    """
}

# Theme Aliases to map Linux desktop standard icon names
ALIASES = {
    "kitty": "utilities-terminal",
    "foot": "utilities-terminal",
    "chromium": "web-browser",
    "browser": "web-browser",
    "thunar": "system-file-manager",
    "org.xfce.thunar": "system-file-manager",
    "synapse-palette": "synapse-hud"
}

def render_svg(name, glyph_template, style):
    if style == "chrome":
        # Liquid Mauve Chrome: 45° diamond chamfers, pure white specular glint, liquid silver chrome
        accent = "#cba6f7"
        fg = "#ffffff"
        svg = f"""<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Soft Contact Drop Shadow -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="7" stdDeviation="6" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
    
    <!-- Chamfered Chrome Rim Gradient (45 degree specular reflection) -->
    <linearGradient id="chrome-rim" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>
      <stop offset="18%" stop-color="#cdd6f4" stop-opacity="0.9"/>
      <stop offset="38%" stop-color="#45475a" stop-opacity="0.8"/>
      <stop offset="65%" stop-color="#cba6f7" stop-opacity="0.9"/>
      <stop offset="85%" stop-color="#ffffff" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#181825" stop-opacity="1"/>
    </linearGradient>

    <!-- Liquid Metal Face (Subsurface Mauve Sheen) -->
    <radialGradient id="metal-face" cx="35%" cy="30%" r="75%">
      <stop offset="0%" stop-color="#313244"/>
      <stop offset="45%" stop-color="#1e1e2e"/>
      <stop offset="78%" stop-color="#181825"/>
      <stop offset="100%" stop-color="#11111b"/>
    </radialGradient>

    <!-- High-Gloss Horizon Reflection -->
    <linearGradient id="horizon" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.35"/>
      <stop offset="48%" stop-color="#cba6f7" stop-opacity="0.15"/>
      <stop offset="50%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.2"/>
    </linearGradient>
  </defs>

  <!-- Base Plate with Drop Shadow -->
  <rect x="12" y="12" width="104" height="104" rx="28" fill="url(#chrome-rim)" filter="url(#shadow)"/>

  <!-- Inner Machined Metal Inset -->
  <rect x="16" y="16" width="96" height="96" rx="24" fill="url(#metal-face)"/>

  <!-- Horizon Specular Gloss Sheen -->
  <path d="M 16 40 C 16 26 26 16 40 16 L 88 16 C 102 16 112 26 112 40 L 112 60 Q 64 74 16 60 Z" fill="url(#horizon)"/>

  <!-- Specular Chamfer Highlight Wire (Top-Left Gleam) -->
  <path d="M 22 40 C 22 30 30 22 40 22 L 88 22" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" opacity="0.85"/>

  <!-- Core Icon Glyph -->
  {glyph_template.format(accent=accent, fg=fg)}
</svg>"""

    elif style == "obsidian":
        # Smoked Obsidian: Mirror black ceramic, knurled outer rim, glowing neon mauve conduit
        accent = "#cba6f7"
        fg = "#cdd6f4"
        svg = f"""<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="7" stdDeviation="6" flood-color="#000000" flood-opacity="0.75"/>
    </filter>

    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3.5" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Milled Titanium Perimeter Rim -->
    <linearGradient id="knurled-rim" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#585b70"/>
      <stop offset="35%" stop-color="#313244"/>
      <stop offset="70%" stop-color="#181825"/>
      <stop offset="100%" stop-color="#45475a"/>
    </linearGradient>

    <!-- Deep Obsidian Ceramic Dish -->
    <radialGradient id="obsidian-dish" cx="40%" cy="35%" r="70%">
      <stop offset="0%" stop-color="#181825"/>
      <stop offset="50%" stop-color="#11111b"/>
      <stop offset="100%" stop-color="#07070a"/>
    </radialGradient>
  </defs>

  <!-- Outer Milled Metal Rim -->
  <rect x="12" y="12" width="104" height="104" rx="28" fill="url(#knurled-rim)" filter="url(#shadow)"/>
  
  <!-- Outer Knurl Tick Marks -->
  <rect x="14" y="14" width="100" height="100" rx="26" fill="none" stroke="#6c7086" stroke-width="1.5" stroke-dasharray="3 3"/>

  <!-- Jet Black Obsidian Inset -->
  <rect x="17" y="17" width="94" height="94" rx="23" fill="url(#obsidian-dish)"/>

  <!-- Internal Glass Edge Reflection -->
  <rect x="18" y="18" width="92" height="92" rx="22" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.35"/>

  <!-- Glowing Neon Conduit Glyph Group -->
  <g filter="url(#neon-glow)">
    {glyph_template.format(accent=accent, fg=fg)}
  </g>
</svg>"""

    elif style == "tungsten":
        # Radial Milled Tungsten: Anisotropic lathe brush marks, singularity donut rim
        accent = "#cba6f7"
        fg = "#f5e0dc"
        svg = f"""<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="7" stdDeviation="6" flood-color="#000000" flood-opacity="0.65"/>
    </filter>

    <!-- Concentric Lathe Ring Specular Cross Reflection -->
    <radialGradient id="tungsten-radial" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#45475a"/>
      <stop offset="25%" stop-color="#313244"/>
      <stop offset="55%" stop-color="#181825"/>
      <stop offset="85%" stop-color="#313244"/>
      <stop offset="100%" stop-color="#11111b"/>
    </radialGradient>

    <!-- Chrome Outer Stepped Bevel -->
    <linearGradient id="stepped-bevel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cdd6f4"/>
      <stop offset="30%" stop-color="#585b70"/>
      <stop offset="70%" stop-color="#cba6f7"/>
      <stop offset="100%" stop-color="#181825"/>
    </linearGradient>
  </defs>

  <!-- Stepped Outer Rim -->
  <rect x="12" y="12" width="104" height="104" rx="28" fill="url(#stepped-bevel)" filter="url(#shadow)"/>

  <!-- Lathe Machined Concentric Face -->
  <rect x="16" y="16" width="96" height="96" rx="24" fill="url(#tungsten-radial)"/>

  <!-- Concentric Lathe Tool Lines -->
  <circle cx="64" cy="64" r="42" fill="none" stroke="#585b70" stroke-width="0.8" opacity="0.6"/>
  <circle cx="64" cy="64" r="34" fill="none" stroke="#6c7086" stroke-width="0.8" opacity="0.5"/>
  <circle cx="64" cy="64" r="26" fill="none" stroke="#585b70" stroke-width="0.8" opacity="0.4"/>

  <!-- 4-Point Anisotropic Specular Flairs -->
  <path d="M 64 16 L 64 112 M 16 64 L 112 64" stroke="#ffffff" stroke-width="1.2" opacity="0.2"/>

  <!-- Core Glyph -->
  {glyph_template.format(accent=accent, fg=fg)}
</svg>"""

    elif style == "billet":
        # Aerospace Billet: Brushed titanium plate, satin mauve pocket, stainless steel micro-rivets
        accent = "#cba6f7"
        fg = "#cdd6f4"
        svg = f"""<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="7" stdDeviation="5" flood-color="#000000" flood-opacity="0.55"/>
    </filter>

    <!-- Brushed Titanium Hairline Grain -->
    <linearGradient id="brushed-base" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e1e2e"/>
      <stop offset="20%" stop-color="#2a2b3d"/>
      <stop offset="40%" stop-color="#181825"/>
      <stop offset="65%" stop-color="#2a2b3d"/>
      <stop offset="85%" stop-color="#181825"/>
      <stop offset="100%" stop-color="#11111b"/>
    </linearGradient>

    <!-- Bead-Blasted Satin Mauve Front Plate -->
    <linearGradient id="satin-plate" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#3b334d"/>
      <stop offset="40%" stop-color="#282236"/>
      <stop offset="100%" stop-color="#1b1724"/>
    </linearGradient>

    <!-- Micro Stainless Steel Rivet -->
    <radialGradient id="rivet" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="50%" stop-color="#a6adc8"/>
      <stop offset="100%" stop-color="#313244"/>
    </radialGradient>
  </defs>

  <!-- Titanium Base Chassis -->
  <rect x="12" y="12" width="104" height="104" rx="26" fill="url(#brushed-base)" filter="url(#shadow)"/>

  <!-- Satin Mauve Inset Plate -->
  <rect x="18" y="18" width="92" height="92" rx="20" fill="url(#satin-plate)" stroke="#cba6f7" stroke-width="1.2" stroke-opacity="0.6"/>

  <!-- 4 Corner Stainless Micro-Rivets -->
  <circle cx="26" cy="26" r="3" fill="url(#rivet)"/>
  <circle cx="102" cy="26" r="3" fill="url(#rivet)"/>
  <circle cx="26" cy="102" r="3" fill="url(#rivet)"/>
  <circle cx="102" cy="102" r="3" fill="url(#rivet)"/>

  <!-- Core Glyph -->
  {glyph_template.format(accent=accent, fg=fg)}
</svg>"""

    return svg


def main():
    os.makedirs(ICONS_DEST, exist_ok=True)

    for theme_name, theme_info in THEMES.items():
        theme_dir = os.path.join(ICONS_DEST, theme_name)
        apps_dir = os.path.join(theme_dir, "scalable", "apps")
        places_dir = os.path.join(theme_dir, "scalable", "places")
        os.makedirs(apps_dir, exist_ok=True)
        os.makedirs(places_dir, exist_ok=True)

        # 1. index.theme
        index_theme_content = f"""[Icon Theme]
Name={theme_name}
Comment={theme_info['comment']}
Inherits=Hatter-Purple,Papirus-Dark,hicolor
Directories=scalable/apps,scalable/places

[scalable/apps]
Context=Applications
Size=128
MinSize=16
MaxSize=512
Type=Scalable

[scalable/places]
Context=Places
Size=128
MinSize=16
MaxSize=512
Type=Scalable
"""
        with open(os.path.join(theme_dir, "index.theme"), "w", encoding="utf-8") as f:
            f.write(index_theme_content)

        # 2. Render all glyphs
        style = theme_info["style"]
        for glyph_name, glyph_svg in GLYPHS.items():
            dest_dir = places_dir if glyph_name.startswith("folder") or glyph_name == "user-home" else apps_dir
            out_path = os.path.join(dest_dir, f"{glyph_name}.svg")
            content = render_svg(glyph_name, glyph_svg, style)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)

        # 3. Create symlinks / aliases
        for alias, target in ALIASES.items():
            alias_path = os.path.join(apps_dir, f"{alias}.svg")
            target_path = f"{target}.svg"
            if os.path.lexists(alias_path):
                os.remove(alias_path)
            os.symlink(target_path, alias_path)

        print(f"Generated theme: {theme_name} -> {theme_dir}")

if __name__ == "__main__":
    main()
