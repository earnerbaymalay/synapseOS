# SynapseOS Engineering Roadmap

## Phase 1: Foundation & Packaging (Current)
- [x] Establish clean, featherlight Git repository structure.
- [x] Author comprehensive architecture specifications & comparative inspiration breakdown.
- [x] Configure Antigravity IDE with Gemini 4 Argon high-reasoning workspace rules.
- [ ] Implement `packages/core/synapse-core/PKGBUILD` for compiling and packaging the Synapse daemon.
- [ ] Establish systemd service presets (`synapse.service`, `ollama.service`, `ananicy-cpp.service`).
- [ ] Configure default user skeleton overlay (`overlay/skel/.synapse`) with memory engine hooks.

## Phase 2: Live ISO Profile & Kernel Integration
- [ ] Create `build/archiso/` profile based on `releng`.
- [ ] Integrate `linux-cachyos` kernel package and x86-64-v3 repository mirrors into `pacman.conf`.
- [ ] Configure ZRAM zstd compression and sysctl tuning in `overlay/etc/sysctl.d/99-synapseos.conf`.
- [ ] Configure NetworkManager stealth posture (MAC randomization, Quad9 DoT).

## Phase 3: Desktop Interface & AI Command Palette
- [ ] Package unified Catppuccin Mocha Mauve + Liquid Chrome GTK and icon themes.
- [ ] Implement PS2-inspired SDDM greeter with seamless desktop hand-off.
- [ ] Build global `synapse-palette` / `agy-palette` Super-key HUD launcher.

## Phase 4: Installer & Release Automation
- [ ] Configure Calamares installer branding and module sequence.
- [ ] Build automated CI/CD pipeline using GitHub Actions to produce verifiable ISO images.
- [ ] Release SynapseOS Developer Preview v0.1.0-alpha.
