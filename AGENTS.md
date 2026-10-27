# SynapseOS — AI-Native Linux Distribution Architecture

## Prime Directive: Security, Stealth & Anonymity First
- **Core Stance**: All architectural decisions, packages, network configurations, and daemons must prioritize security, zero telemetry, and network anonymity.
- **Network Posture**:
  - Full MAC address randomization (scanning and session cloned MAC).
  - Encrypted DNS-over-TLS (DoT via Quad9 `9.9.9.9` on port 853).
  - RFC 4941 IPv6 privacy extensions preferred.
  - Drop-all unsolicited incoming traffic via nftables/firewalld.

## System Model & Engine: Gemini 4 Argon
- **Primary AI Engine**: Gemini 4 Argon with high reasoning budget.
- **Mission**: Architect, construct, package, and test SynapseOS — an AI-native rolling Linux operating system merging:
  - **CachyOS Performance**: Kernel schedulers (BORE/EEVDF), x86-64-v3/v4 optimized repos, ZRAM zstd swappiness=180, BBR TCP.
  - **EndeavourOS Foundation**: Clean upstream Arch Linux base, transparent pacman packaging, Calamares installer, zero bloat.
  - **Omarchy Aesthetics**: Cybernetic, monospace terminal environment, unified Catppuccin / liquid chrome theme, keyboard-centric control.
  - **Synapse Core AI Subsystem**: Native Rust runtime gateway, bidirectional context firewall, 3-layer persistent agent memory, local LLM orchestration.

## Architecture Guidelines
1. **Clean Repository Integrity**: No binary ISO blobs, build artifacts, chroot roots, or credentials in Git.
2. **Modular Layering**:
   - `packages/`: Native Arch Linux `PKGBUILD` specifications.
   - `build/`: Reproducible `archiso` profiles and automation recipes.
   - `overlay/`: System configuration overlays (`/etc`, `/usr/share`, `/etc/skel`).
   - `docs/`: Comprehensive technical specifications and research whitepapers.
3. **Reproducibility**: All packages must build cleanly with `makepkg -si` in isolated chroots (`arch-nspawn` / `extra-x86_64-build`).
