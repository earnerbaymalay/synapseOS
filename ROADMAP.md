# SynapseOS Engineering Roadmap

## Phase 1: Native Packaging & Core Daemons (Completed)
- [x] Establish clean, featherlight Git repository structure.
- [x] Author comprehensive architecture specifications & comparative inspiration breakdown.
- [x] Configure Antigravity IDE with Gemini 4 Argon high-reasoning workspace rules.
- [x] Implement `packages/core/synapse-core/PKGBUILD` for compiling and packaging the Synapse daemon (`127.0.0.1:8000` gateway + 30m Brain sync timer).
- [x] Implement `packages/desktop/llm-quickfire-panel/PKGBUILD` with curated color palettes (Catppuccin Mocha Mauve, Tokyo Night, Nord, Cyberpunk).
- [x] Establish systemd service presets (`synapse.service`, `ollama.service`, `ananicy-cpp.service`, `firewalld.service`, `sddm.service`).
- [x] Configure default user skeleton overlay (`overlay/etc/skel/`) with Synapse memory engine hooks and Quickfire HUD defaults.

## Phase 2: Kernel Microarchitecture, Latency & Stealth Posture (Completed)
- [x] Integrate `linux-cachyos` BORE scheduler kernel and `[cachyos-v3]` x86-64-v3 repository mirrors into `pacman.conf`.
- [x] Configure 8 GB ZRAM `zstd` compression (`overlay/etc/systemd/zram-generator.conf`) and low-latency VM/BBR sysctl tuning (`overlay/etc/sysctl.d/99-synapseos.conf`).
- [x] Configure `ananicy-cpp` rules and `ollama.service` single-parallelism CPU inference overrides.
- [x] Enforce Prime Directive network stealth posture: full Wi-Fi scan & session MAC randomization, RFC 4941 IPv6 privacy extensions, Quad9 DNS-over-TLS (`9.9.9.9` / `149.112.112.112`), and firewalld drop posture.

## Phase 3: Cyberdeck Desktop Interface & Seamless Transitions (Completed)
- [x] Package unified Catppuccin Mocha Mauve + Liquid Silver Chrome GTK, xfwm4, Kitty, and icon themes.
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

## Phase 6: V4 Visual Identity & Live ISO Hardening (Completed)
- [x] Package `synapse-themes`: 5 SynapseOS wallpapers (`/usr/share/backgrounds/synapseos/`, 1376x768 renders), `synapse-theme` switcher (`obsidian-mauve` default, `ristretto-tungsten`, `crimson-carbon`, `platinum-chrome`, `obsidian-basalt` unbranded) bound to `Super+Ctrl+T` in XFCE and Sway.
- [x] `synapse-screensaver`: braille geodesic torus ("The Purple Donut") + SYNAPSE brand reveal (`tte` when installed); 5-minute idle trigger via `swayidle` (Sway) and `synapse-idle` (XFCE). Not a screen lock.
- [x] Verify CachyOS package signatures (drop `Optional TrustAll`; ship `cachyos-keyring`; isolated, fingerprint-pinned build keyring).
- [x] Generate pacman keyring per boot (`pacman-init.service`) instead of baking a master key into the ISO.
- [x] Calamares `shellprocess@cleanup`: remove live NOPASSWD sudoers + passwordless live user, fresh keyring on install; `users.conf` wheel sudo with password.
- [x] Resolve pacstrap file conflicts (Calamares config applied after `cachyos-calamares`).
- [x] Live ISO bootability: archiso initramfs hooks (`mkinitcpio.conf.d/archiso.conf`), microcode via hook instead of missing `*-ucode.img` initrds.
- [x] Installed-system bootability: restore kernels emptied from `/boot` by mkarchiso, drop archiso hooks, `initcpiocfg`/`initcpio`, GRUB `bootloader.conf` (not cachyos limine default), `mount.conf` Btrfs layout.
- [x] Calamares privacy: own `welcome.conf`/`locale.conf` with no GeoIP lookup; fix invalid YAML in `partition.conf`.
- [x] Wallpaper set: 3 designs x accent variants (14), Basalt Tower SYNAPSE-branded; theme ids `<design>-<accent>`.
- [x] `synapse-greeter`: `synapseos` Qt6 SDDM theme (right-aligned clock + system readout, chamfered panel with animated accent trails); `synapse-theme --sync-greeter`.
- [x] Remove the PlayStation 2 boot animation and greeter (`synapse-theme-ps2`).
- [x] Boot splash: `synapse-plymouth` — laser-engraved Twin Hook S (Plymouth script theme, frames rendered per accent at build), LUKS prompt, `synapse-theme --sync-boot`.
- [x] Verify the splash on real hardware / QEMU (verified headless QEMU/KVM boot).
- [x] First-boot onboarding wizard `synapse-welcome` (theme, privacy defaults, local model pull, HUD intro).
- [x] Stage C: full `mkarchiso` build + QEMU/KVM boot verification; Stage D: `v0.1.0-alpha` release with `SHA256SUMS`.

## Phase 7: Material You Ecosystem & Token Optimization (Completed)
- [x] `synapse-hud`: Native Qt6/QML Material You Command HUD bound to `Super+Space` with chamfered borders, animated border light trails, mouse-clickable category cards, and keyboard hotkeys.
- [x] `synapse-settings`: Material You system control center (Themes & Accents, AI Engine keep-alive & concurrency, Stealth/DoT toggles, PipeWire audio latency).
- [x] `synapse-notes`: Material You Markdown scratchpad auto-syncing to `~/AIBrain/notes/scratchpad.md` and indexed into persistent Synapse Memory embeddings.
- [x] `synapse-setup`: Background first-boot local LLM model pull (`qwen2.5-coder:latest`) running at idle CPU/IO priority without stalling session startup.
- [x] Metallic Reflective Icon Themes: 4 complete vector suites (`Synapse-Liquid-Chrome`, `Synapse-Smoked-Obsidian`, `Synapse-Radial-Tungsten`, `Synapse-Aerospace-Billet`) inheriting from `Hatter-Purple`.
- [x] Lossless Token Squasher (`synapse squash` & `/usr/bin/squash`): JFrog Boost equivalent stripping ANSI escape codes, carriage return progress bars, and repetitive test noise.
- [x] Hardened Zero-Telemetry Chromium: Configured with `--disable-telemetry`, `--disable-sync`, `--disable-metrics`, `--no-default-browser-check` as default browser.
- [x] Calamares Netinstall Feature Packs: Selectable installer modules for *Pentest Heavy*, *Creative & Office*, and *Daily Desktop*.
- [x] Engineering Gate Harness: 279/279 automated verification checks passing (100% pass, 0 warnings, 0 failures; 17/17 pytest unit & UI tests passing).

## Phase 8: Hardware Orchestration, Neural Daemon Mesh & ISO Production Release (Completed)
- [x] **Milestone 8.1: Live ISO Compilation & QEMU/KVM Boot Verification (Stage C)**
  - [x] Execute `./build/build-iso.sh` to compile native `[synapseos]` packages into `out/repo/synapseos.db.tar.gz`.
  - [x] Produce `out/synapseos-2026.11.01-x86_64.iso` (2.9 GB) via `mkarchiso`.
  - [x] Validate headless QEMU/KVM boot kinematics: UEFI `systemd-boot` $\rightarrow$ `synapse-plymouth` Twin Hook laser engrave splash $\rightarrow$ `synapse-greeter` SDDM Qt6 handoff $\rightarrow$ XFCE/Sway desktop session $\rightarrow$ Calamares installation walkthrough.
- [x] **Milestone 8.2: Synapse Core Gateway & Bidirectional Context Firewall**
  - [x] Finalize `/usr/bin/synapse` (`synapse-core` Rust daemon) loopback gateway (`127.0.0.1:8000`) with Bearer token authentication and DNS-rebinding protection.
  - [x] Implement outbound prompt secret & entropy inspection (redacting API keys, private keys, SSH certificates via `firewall.rs`).
  - [x] Integrate background vector memory indexing for `~/AIBrain/notes/scratchpad.md` into local persistent embeddings.
- [x] **Milestone 8.3: Hardware Orchestration & Latency Profile Daemon**
  - [x] Implement `synapse-hardware` CLI/daemon for dynamic PL1 thermal envelope switching (15W eco vs 25W performance via `throttled`).
  - [x] Wire dynamic PipeWire buffer quantum switching (64/48000 for low-latency DSP vs 1024 for battery efficiency).
  - [x] Integrate Waybar warning alerts and real-time telemetry output via `synapse-hardware bar`.
  - [x] Integrate hardware controls into `synapse-settings` Audio & Power tab.
- [x] **Milestone 8.4: Package Repository Signing & Release Automation (Stage D)**
  - [x] Generate `out/SHA256SUMS` and `out/SHA512SUMS`.
  - [x] Resolve CI verification portability across Ubuntu runners without `makepkg`.
  - [x] Tag `v0.1.0-alpha.2` and trigger automated GitHub Actions release CI/CD workflow.

## Phase 9: Neural Hardware Autotuning & eBPF Context Enclave (Upcoming — Q1 2027)
- [ ] **Milestone 9.1: Dynamic PL1/PL2 Thermal Governor (`synapse-governor`)**:
  - Automatically scale CPU package TDP based on real-time Ollama inference vs background compilation state.
- [ ] **Milestone 9.2: eBPF Secret Leak Interceptor**:
  - Implement a kernel-level eBPF socket filter guaranteeing that raw private keys (`id_rsa`, `*.pem`, `sk-*`) cannot egress any socket even if bypassed by third-party unproxied applications.
- [ ] **Milestone 9.3: Vulkan Offload Profiler for Integrated Graphics**:
  - Enable quantized llama.cpp / Ollama offload to Intel UHD 620 / AMD Radeon integrated graphics via Mesa Vulkan compute.

## Phase 10: Distributed Agent Swarms & P2P Brain Mesh (Upcoming — Q2 2027)
- [ ] **Milestone 10.1: Peer-to-Peer Brain Synchronization**:
  - Encrypted WireGuard / Libp2p mesh allowing SynapseOS nodes on the same LAN to share distilled Obsidian memory vector embeddings without internet access.
- [ ] **Milestone 10.2: Remote Inference Offloading**:
  - Transparent failover: route local Quickfire HUD requests from a mobile laptop to a high-power local workstation running 70B models over an authenticated local mTLS tunnel.

## Phase 11: Immutable System Layer & A/B Partitioning (Upcoming)
- [ ] **Milestone 11.1: Optional Ostree / Composefs Read-Only Root**:
  - Provide an immutable read-only sysroot mode for forensic, pentest, or air-gapped deployments where `/usr` is mounted read-only and all user modifications live in `/var` and `/home`.

## Phase 12: Synapse Cyberdeck Hardware Reference Kit (Upcoming)
- [ ] **Milestone 12.1: Open-Source CAD & 3D Print Enclosure Specs**:
  - Blueprint specs for a field-ready cyberdeck chassis housing a Dell Latitude / Framework motherboard, 7-to-10 inch sunlight-readable display, ortholinear mechanical keyboard, and hardware RF kill switches.
