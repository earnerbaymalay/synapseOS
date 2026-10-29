# SynapseOS Engineering Roadmap

## Phase 1: Native Packaging & Core Daemons (Completed)
- [x] Establish clean, featherlight Git repository structure.
- [x] Author comprehensive architecture specifications & comparative inspiration breakdown.
- [x] Configure Antigravity IDE with Gemini 4 Argon high-reasoning workspace rules.
- [x] Implement `packages/core/synapse-core/PKGBUILD` for compiling and packaging the Synapse daemon (`127.0.0.1:8000` gateway + 30m Brain sync timer).
- [x] Implement `packages/desktop/llm-quickfire-panel/PKGBUILD` with curated color palettes (PS2 Cyber Blue, Catppuccin Mocha Mauve, Tokyo Night, Nord, Cyberpunk).
- [x] Implement `packages/desktop/synapse-theme-ps2/PKGBUILD` for the procedural PlayStation 2 startup animation and `ps2-xfce` Qt6 SDDM theme.
- [x] Establish systemd service presets (`synapse.service`, `ollama.service`, `ananicy-cpp.service`, `firewalld.service`, `sddm.service`).
- [x] Configure default user skeleton overlay (`overlay/etc/skel/`) with Synapse memory engine hooks and Quickfire HUD defaults.

## Phase 2: Kernel Microarchitecture, Latency & Stealth Posture (Completed)
- [x] Integrate `linux-cachyos` BORE scheduler kernel and `[cachyos-v3]` x86-64-v3 repository mirrors into `pacman.conf`.
- [x] Configure 8 GB ZRAM `zstd` compression (`overlay/etc/systemd/zram-generator.conf`) and low-latency VM/BBR sysctl tuning (`overlay/etc/sysctl.d/99-synapseos.conf`).
- [x] Configure `ananicy-cpp` rules and `ollama.service` single-parallelism CPU inference overrides.
- [x] Enforce Prime Directive network stealth posture: full Wi-Fi scan & session MAC randomization, RFC 4941 IPv6 privacy extensions, Quad9 DNS-over-TLS (`9.9.9.9` / `149.112.112.112`), and firewalld drop posture.

## Phase 3: Cyberdeck Desktop Interface & Seamless Transitions (Completed)
- [x] Package unified Catppuccin Mocha Mauve + Liquid Silver Chrome GTK, xfwm4, Kitty, and icon themes.
- [x] Implement PS2 BIOS -> SDDM (`ps2-xfce`) -> XFCE 4.20 zero-blackout visual hand-off.
- [x] Configure Picom compositor (`overlay/etc/xdg/picom.conf`) with `dual_kawase` blur and rounded corners.
- [x] Configure optional Sway/Wayland tiling session (`overlay/etc/skel/.config/sway/config` & `waybar/{config.jsonc,style.css}`).
- [x] Bind standalone Super-key HUD toggle (`xcape` / `Mod4+space` / `Mod4+d`) and autostart `llm-quickfire-panel`.

## Phase 4: Archiso Live ISO Profile & Build Tooling (Completed)
- [x] Create `build/archiso/` profile (`profiledef.sh`, `packages.x86_64`, `pacman.conf`, UEFI `systemd-boot` & BIOS `syslinux` bootloaders, `customize_airootfs.sh`).
- [x] Build automated ISO builder script (`build/build-iso.sh`) with `--dry-run` / `--check` and `--build-pkgs` support.
- [x] Implement automated Engineering Gate G1–G4 verification harness (`build/verify-gates.sh`).

## Phase 5: Calamares Installer & Release Automation (Completed)
- [x] Configure Calamares installer module sequence (`packages/installer/calamares/settings.conf`).
- [x] Author SynapseOS Calamares branding (`branding/synapseos/branding.desc`) with Catppuccin Mocha Mauve (`#cba6f7`), Liquid Silver Chrome (`#cdd6f4`), and Obsidian Crust (`#11111b`) styling.
- [x] Configure Btrfs (`zstd` subvolumes `@`, `@home`, `@snapshots`, `@var_log`) and Ext4 (`noatime`) partitioning presets (`modules/partition.conf`) and mandatory systemd services (`modules/services-systemd.conf`).
- [x] Build automated GitHub Actions CI/CD workflow (`.github/workflows/build-iso.yml`) running Gate G1–G4 verification, container ISO builds, `SHA256SUMS`, and tagged GitHub Releases.
