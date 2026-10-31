# SynapseOS Review Brief: Brand Identity & Monolithic Laser Boot Splash

**Date:** 2026-10-31  
**Target:** Claude Code Review / AI Team Cross-Evaluation  
**Repository:** `synapseOS` (Submodule: commit [`17f0cab`](https://github.com/earnerbaymalay/synapseOS/commit/17f0cab), Parent: [`652287d`](https://github.com/earnerbaymalay/synapse-cli/commit/652287d))  
**Harness Status:** **279/279 Gates Passing** | **17/17 pytest UI/UX Tests Passing**

---

## 1. Executive Summary & Design Paradigm

The workshop/hazard-tape boot aesthetic has been completely replaced with a **Sleek, Monolithic Cyberdeck Laser Fabrication** sequence. The branding language now adheres strictly to the **Catppuccin Mocha Mauve + Liquid Silver Chrome + Obsidian Crust** identity across the entire OS lifecycle:

```
[UEFI systemd-boot / GRUB]
           │
           ▼
[Plymouth Boot Splash] ───► Monolithic Laser Fabrication (Twin-Hook Cipher)
           │
           ▼
[SDDM Greeter]         ───► Chamfered Obsidian Glass, Animated Mauve Trails
           │
           ▼
[Desktop Session]      ───► XFCE 4.20 / Sway Dual Compositor (Picom dual_kawase)
                            ├─ Material You Command HUD (synapse-hud, Super+Space)
                            ├─ First-Boot Onboarding (synapse-welcome)
                            ├─ System Settings (synapse-settings)
                            ├─ Markdown Scratchpad (synapse-notes)
                            └─ 4 Metallic Vector Icon Packs (Liquid Chrome, Smoked Obsidian, Tungsten, Aerospace Billet)
           │
           ▼
[Calamares Installer]  ───► Branded QML Slideshow, Btrfs zstd subvolumes, Zero GeoIP
```

---

## 2. Plymouth Laser Boot Splash Deep-Dive

### Architectural Overview
- **Location:** [`packages/desktop/synapse-plymouth/`](file:///home/ebaymlay/Desktop/AI%20CLI%20WORK/synapseOS/packages/desktop/synapse-plymouth/)
- **Generator:** [`render_frames.py`](file:///home/ebaymlay/Desktop/AI%20CLI%20WORK/synapseOS/packages/desktop/synapse-plymouth/render_frames.py) (Pillow, numpy, ProcessPoolExecutor)
- **Driver Script:** [`synapseos.script.in`](file:///home/ebaymlay/Desktop/AI%20CLI%20WORK/synapseOS/packages/desktop/synapse-plymouth/synapseos.script.in) $\rightarrow$ `synapseos.script`
- **Output:** 120 pre-rendered PNG frames per accent (`frame-000.png` ... `frame-119.png`), 480x448 base asset scaled and centered on active display.
- **Accent Variants:** `mauve` (`#cba6f7`), `tungsten` (`#fab387`), `crimson` (`#f38ba8`), `sapphire` (`#74c7ec`), `emerald` (`#a6e3a1`).

### Kinematic Sequence Breakdown
1. **Phase 1: Precision Monolith Setup & Dual Laser Cutting (Frames 000–045)**
   - Obsidian floating wafer plate with corner fiducial reticles (`MONOLITH // SPEC-01`) and subtle atmospheric mauve bloom.
   - Dual aerospace optical collimators trace the authentic **Twin-Hook Cipher** curves extracted mathematically from [`synapseos-icon.svg`](file:///home/ebaymlay/Desktop/AI%20CLI%20WORK/synapseOS/packages/installer/calamares/branding/synapseos/synapseos-icon.svg).
   - Dynamic laser beam rendering with relativistic photonic sparks, incandescent white kerf, and immediate crystallization into liquid chrome.
2. **Phase 2: Convergence & Dielectric Ion Arc (Frames 045–065)**
   - Left and right cutter heads converge at the central spark gap `(59.5, 70.3)` ↔ `(68.5, 57.7)`.
   - Dielectric arc discharge erupts across the gap, generating an expanding radial plasma shockwave ring and igniting the glowing core pip.
3. **Phase 3: Liquid Chrome Typography Reveal (Frames 065–095)**
   - The engraved metal letters fade in: Liquid Silver Chrome **`SYNAPSE`** + Neon Mauve **`OS`**.
   - Subtitle stamp: `INTELLIGENT CYBERDECK · PRIME DIRECTIVE STEALTH` with tracked technical telemetry.
4. **Phase 4: Stabilization & Telemetry Sync (Frames 095–120)**
   - Permanent specular core spark glow and pulse.
   - Hairline bottom progress track with leading-edge pip responsive to live `plymouth --update="..."` boot telemetry.

### Visible Container Validation
- **Runner:** [`build/test-plymouth-container.sh`](file:///home/ebaymlay/Desktop/AI%20CLI%20WORK/synapseOS/build/test-plymouth-container.sh)
- **Container Technology:** `systemd-nspawn` on the live `airootfs`.
- **Display Bridging:** X11 passthrough on `DISPLAY=:0.0` with `XShm` interception shim ([`/tmp/synapseos_noshm.so`](file:///tmp/synapseos_noshm.so)) allowing non-root/root UID compatibility without Xorg crashes.
- **Verification Result:** Clean graphical initialization, window creation on host X11 display, 7-stage boot simulation, and clean exit code `0`.

---

## 3. Brand Identity & UI/UX Ecosystem Review

### A. Calamares Installer Branding
- **Path:** [`packages/installer/calamares/branding/synapseos/`](file:///home/ebaymlay/Desktop/AI%20CLI%20WORK/synapseOS/packages/installer/calamares/branding/synapseos/)
- **Components:**
  - `synapseos-icon.svg`: Master mathematical vector bezier definition for the twin-hook cipher.
  - `synapseos-logo.svg`: Horizontal badge with Liquid Chrome wordmark.
  - `show.qml` & `calamares/slideshow/`: Material You slides highlighting Stealth Posture (MAC randomization, Quad9 DoT), Neural Concurrency (Ollama), and Metallic Themes.
  - `welcome.conf` & `locale.conf`: Zero GeoIP lookups, privacy-preserving defaults.

### B. SDDM Greeter (`synapse-greeter`)
- **Path:** [`packages/desktop/synapse-greeter/`](file:///home/ebaymlay/Desktop/AI%20CLI%20WORK/synapseOS/packages/desktop/synapse-greeter/)
- **Features:** Right-aligned digital clock + system readout, chamfered obsidian credentials card with animated mauve border glow, responsive user switcher and session selector (XFCE / Sway).
- **Theme Sync:** Automatic synchronization via `synapse-theme --sync-greeter`.

### C. Metallic Reflective Icon Themes
- **Path:** `packages/desktop/synapse-themes/` (and `/usr/share/icons/`)
- **4 Vector Suites:**
  1. `Synapse-Liquid-Chrome`: High-contrast polished chrome gradient with specular white rim.
  2. `Synapse-Smoked-Obsidian`: Darkened titanium with deep mauve edge bevels.
  3. `Synapse-Radial-Tungsten`: Brushed circular tungsten finish with warm amber accents.
  4. `Synapse-Aerospace-Billet`: Matte aerospace CNC aluminum with technical hairline markings.

### D. Material You Suite
- **`synapse-hud`**: Native Qt6/QML HUD bound to `Super+Space` with fuzzy search, categorized cards, and AI shell shortcut launching.
- **`synapse-welcome`**: 4-step first-boot onboarding wizard guiding wallpaper, theme, privacy, and LLM setup.
- **`synapse-settings`**: Material You control panel for system tweaks, audio latency, and local models.
- **`synapse-notes`**: Markdown scratchpad with auto-save to `~/AIBrain/notes/scratchpad.md`.

---

## 4. Test Suite & Verification Status

```bash
# Automated UI/UX Pytest Suite (Offscreen Qt6 Application Testing)
uv run pytest tests/
# Output: 17 passed in 0.77s (synapse-hud, synapse-welcome, synapse-settings, synapse-notes, synapse-screensaver)

# Full SynapseOS Verification Harness
./build/verify-gates.sh
# Output: 279 passed, 0 warnings, 0 failed
```

---

## 5. Review Checklist for Claude

Claude, please review the implementation and verify:
1. **Visual Cohesion**: Does the transition from Plymouth splash $\rightarrow$ SDDM greeter $\rightarrow$ XFCE/Sway desktop feel seamless and unified under the Catppuccin Mauve/Obsidian theme?
2. **Kinetics & Timing**: Is the 120-frame (4.0s @ 30 FPS) loop duration optimal for both fast NVMe boots and slower USB live boots?
3. **Stealth & Anonymity**: Confirm that all Calamares modules, greeter configurations, and network daemons adhere strictly to Prime Directive stealth (Zero GeoIP, Quad9 DoT, MAC randomization).
4. **Readiness for Stage C Full ISO Build**: Does the updated tree satisfy requirements for building the final release ISO via `./build/build-iso.sh`?
