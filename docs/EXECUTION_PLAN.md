# SynapseOS Live Compilation & Release Execution Plan

This document defines the four-stage execution pipeline (`Stage A` – `Stage D`) transitioning SynapseOS from its **86/86 engineering verification gate baseline** into native package compilation, Archiso staging, live ISO image generation, QEMU/KVM validation, and release tagging.

---

## Stage A — Local Custom Repository & Native Package Compilation (`[synapseos]`)

Compile all three native SynapseOS packages into the local `[synapseos]` repository (`out/repo/`) and generate the signed/indexed Pacman database (`synapseos.db.tar.gz`):

1. **`synapse-core` (`packages/core/synapse-core/PKGBUILD`)**:
   - Compiles the Rust `/usr/bin/synapse` runtime gateway with `-C target-cpu=x86-64-v3 -C opt-level=3 -C codegen-units=1`.
   - Bundles `synapse.service` (system unit on `127.0.0.1:8000`), `synapse-sync.service`, `synapse-sync.timer` (30-minute Obsidian knowledge distillation), `/etc/synapse/config.toml`, and shell completions.
2. **`llm-quickfire-panel` (`packages/desktop/llm-quickfire-panel/PKGBUILD`)**:
   - Packages `/usr/bin/quickfire`, `/usr/bin/quickfire-theme`, command palette aliases (`agy-palette`, `llm-quickfire-panel`), 5 curated color palettes (PS2 Cyber Blue, Catppuccin Mocha Mauve, Tokyo Night, Nord, Cyberpunk), and `/etc/xdg/autostart/llm-quickfire-panel.desktop`.
3. **`synapse-theme-ps2` (`packages/desktop/synapse-theme-ps2/PKGBUILD`)**:
   - Packages the PlayStation 2 startup animation (`ps2_xfce_startup.mp4`, `/usr/bin/ps2-startup`, `/usr/local/bin/ps2-system-boot`), `eof-handoff.lua`, `/usr/share/sddm/scripts/Xsetup`, and the Qt6 SDDM theme `/usr/share/sddm/themes/ps2-xfce`.
4. **Repository Indexing**:
   - Run `repo-add -R out/repo/synapseos.db.tar.gz out/repo/*.pkg.tar.*`.
   - Sync `out/repo/` into `build/archiso/airootfs/var/cache/synapseos-repo/` and `/var/cache/synapseos-repo/` for `mkarchiso`.

---

## Stage B — Sync Overlays, CachyOS Mirrorlists & Validate Archiso Staging

1. **RootFS Overlay Synchronization (`./build/build-iso.sh --dry-run`)**:
   - Sync `overlay/etc/` into `build/archiso/airootfs/etc/` (including `99-synapseos.conf` ZRAM/BBR sysctl, `zram-generator.conf`, NetworkManager MAC randomization & RFC 4941 IPv6 stealth posture, Quad9 DoT `resolved.conf.d`, `picom.conf`, and `sddm.conf.d`).
   - Sync `overlay/etc/skel/` into `build/archiso/airootfs/etc/skel/`.
   - Stage Calamares installer configs (`packages/installer/calamares/`) into `build/archiso/airootfs/etc/calamares/`.
2. **CachyOS Mirrorlists & Keyring Preparation**:
   - Verify `/etc/pacman.d/cachyos-mirrorlist` and `/etc/pacman.d/cachyos-v3-mirrorlist` are staged in both `overlay/etc/pacman.d/` and `build/archiso/airootfs/etc/pacman.d/`.
   - Ensure `customize_airootfs.sh` initializes the Pacman keyring and imports/locally signs the CachyOS signing key (`F3B607488DB35A47`).

---

## Stage C — Live ISO Compilation & QEMU/KVM Boot Verification

1. **ISO Generation**:
   - Execute `sudo ./build/build-iso.sh` to invoke `mkarchiso -v -w /tmp/synapseos-archiso-work -o ./out ./build/archiso`.
   - Verify output artifact `out/synapseos-YYYY.MM.DD-x86_64.iso`.
2. **QEMU/KVM Live Boot Test**:
   - Boot the generated ISO using `qemu-system-x86_64 -enable-kvm -m 4096 -smp 4 -cdrom out/synapseos-*.iso`.
   - Verify `systemd-boot` $\rightarrow$ `linux-cachyos` kernel $\rightarrow$ PS2 startup animation $\rightarrow$ `ps2-xfce` SDDM greeter $\rightarrow$ XFCE 4.20 desktop with `synapse.service` and `quickfire` HUD active.

---

## Stage D — Checksums & Release Tagging (`v0.1.0-alpha`)

1. Generate `out/SHA256SUMS` for the ISO image.
2. Re-run `./build/verify-gates.sh` to confirm 86/86 passing checks and clean Git status.
3. Tag `v0.1.0-alpha` to trigger `.github/workflows/build-iso.yml` automated release publishing.
