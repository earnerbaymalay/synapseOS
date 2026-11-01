# SynapseOS — Comprehensive Technical FAQ

> **Surgical precision. Zero friction.**  
> Frequently asked architectural, security, performance, and workflow questions.

---

## 1. Prime Directive: Security, Privacy & Zero Telemetry

### Q: What is the "Prime Directive" of SynapseOS?
> **A:** The guiding principle baked into every configuration file and build script of SynapseOS is:  
> *"System aims for minimal if not 0 telemetry and prioritises anonymisation without degradation of service."*  
> Unlike traditional operating systems that transmit diagnostic beacons, search queries, or user telemetry to cloud servers, SynapseOS operates under a zero-outbound-telemetry default.

### Q: How does SynapseOS enforce network anonymization?
> **A:** Anonymization is implemented at multiple layers of the networking stack:
> 1. **Wi-Fi MAC Address Randomization**:
>    - `/etc/NetworkManager/conf.d/00-synapseos-stealth.conf` enforces `wifi.scan-rand-mac-address=yes`. When scanning for access points, your hardware wireless card broadcasts synthetic randomized MAC addresses.
>    - Active connections use `cloned-mac-address=random`, meaning every Wi-Fi network receives a completely unique, rotating synthetic MAC address.
> 2. **RFC 4941 IPv6 Privacy Extensions**:
>    - Configured with `ipv6.ip6-privacy=2`. Network interfaces generate rotating temporary IPv6 addresses for outbound connections rather than deriving your IP from the hardware interface token (EUI-64).
> 3. **Encrypted DNS-over-TLS (DoT)**:
>    - Plaintext DNS over UDP port 53 is eliminated. `systemd-resolved` routes all hostname lookups to Swiss-based Quad9 DNS servers (`9.9.9.9` and `149.112.112.112`) over encrypted TLS (Port 853) with strict Server Name Indication (SNI) validation.
> 4. **Firewall Default Drop**:
>    - `firewalld` defaults to the `drop` zone. All unsolicited incoming connection attempts, ping sweeps, and port scans are silently dropped.
> 5. **Telemetry-Stripped Chromium**:
>    - The packaged browser defaults with `--disable-telemetry`, `--disable-sync`, `--disable-metrics`, `--disable-background-networking`, and `--no-default-browser-check`.

---

## 2. Synapse AI Engine & Offline Intelligence

### Q: Can I run local AI workflows completely disconnected from the Internet?
> **A:** Yes. SynapseOS is designed as an offline-first cyberdeck:
> - `ollama.service` runs as a native systemd unit bound to `127.0.0.1:11434` with an extended `24h` memory keep-alive.
> - The native First-Boot Wizard (`synapse-welcome`) downloads high-performance local coding models (such as `qwen2.5-coder:latest` 7B Q4_K_M).
> - Once downloaded, all model inference runs 100% locally on your CPU/GPU. No prompts, code snippets, or user data ever leave your machine.

### Q: What is the "Bidirectional Context Firewall"?
> **A:** When using the Synapse Daemon (`synapse-core` on port 8000), outbound prompts pass through an intelligent entropy scanner implemented in Rust ([`firewall.rs`](file:///home/ebaymlay/work/synapse/packages/core/src/firewall.rs)):
> - **Outbound Egress Pseudonymization**: Hardware MAC addresses, RFC 1918 private IPv4 addresses (`192.168.x.x`, `10.x.x.x`), and high-entropy API keys/tokens are automatically detected and replaced with synthetic placeholder tokens (e.g. `[SYNAPSE_IP_1]`, `[SYNAPSE_MAC_1]`).
> - **Inbound Rehydration**: When model completions or tool calls return, the placeholder tokens are seamlessly swapped back to their real values.
> - This guarantees that sensitive network credentials are never leaked to external inference endpoints or cached model logs.

### Q: What does `synapse squash` (`/usr/bin/squash`) do?
> **A:** Local LLMs operate with limited context windows (e.g., 4,096 to 32,768 tokens). Developer terminal output is filled with ANSI color escapes, progress bars with repeated carriage returns (`\r`), and repetitive test output.  
> `squash` is a high-speed token compression utility that losslessly strips ANSI formatting, condenses repetitive test runs, and optimizes context density, saving up to **60% of context tokens** before feeding terminal outputs into LLMs.

---

## 3. Kernel, Microarchitecture & Low-Latency Performance

### Q: Why use `linux-cachyos` with the BORE scheduler instead of the standard Arch Linux kernel?
> **A:** The standard Linux kernel scheduler (CFS / EEVDF) treats CPU bursts equally. Under heavy agentic compilation or multi-core local LLM inference, standard kernels suffer from dropped frames, audio stutters, and lagging terminals.  
> The **BORE (Burst-Oriented Response Enhancer)** scheduler dynamically calculates task burstiness: interactive applications (such as Kitty terminal, typing in IDEs, or moving windows in XFCE/Sway) receive immediate CPU scheduling priority, maintaining silky-smooth 60–144 FPS responsiveness even with CPU utilization at 100%.

### Q: Why is ZRAM configured with `vm.swappiness = 180`? Isn't swap bad for performance?
> **A:** Traditional swapping to mechanical disks or slow SSDs causes thrashing. However, **ZRAM** is an in-memory block device compressed with the ultra-fast `zstd` algorithm.  
> Setting `vm.swappiness = 180` and `vm.page-cluster = 0` instructs the Linux virtual memory manager to aggressively compress cold, idle memory pages into ZRAM rather than discarding useful filesystem inode/dentry caches (`vm.vfs_cache_pressure = 50`). This provides the equivalent of **24 GB+ usable RAM on a 16 GB machine** without disk wear.

### Q: What is `x86-64-v3` microarchitecture optimization?
> **A:** Upstream Linux distributions compile packages for generic `x86_64` (baseline from 2003) to ensure compatibility with ancient processors. SynapseOS integrates CachyOS `x86-64-v3` package repositories compiled specifically with **AVX, AVX2, BMI1, BMI2, FMA, and MOVBE** instruction sets. This delivers a **10% to 25% throughput speedup** in mathematical operations, cryptographic hashing, and tensor computations.

---

## 4. Desktop Compositor & Cyberdeck Interface

### Q: How do I switch between the traditional desktop (XFCE) and the tiling session (Sway)?
> **A:** SynapseOS ships with two fully tuned environments:
> 1. **Default: XFCE 4.20 + Picom**: Optimized for stability, multi-monitor docking, and classic workflows. Features `dual_kawase` background glass blur, Catppuccin Mocha Mauve GTK styling, and custom titlebar buttons.
> 2. **Optional: Sway Wayland**: Configured at `/etc/skel/.config/sway/config` with matching `waybar` statusbars, animations, and zero-tearing Wayland pipewire screensharing.
> 
> *To switch*: Log out, select the user avatar in `synapse-greeter`, and toggle between **XFCE Session** and **Sway** in the session dropdown. Both sessions share the exact same keybindings:
> - `Super+Space`: Open `synapse-hud` Command Center
> - `Super+Ctrl+T`: Cycle metallic wallpaper & theme palettes (`synapse-theme`)
> - `Super+Enter`: Launch Kitty terminal

### Q: How do I change the accent colors and theme variants?
> **A:** Press **`Super + Ctrl + T`** anywhere in XFCE or Sway to launch the interactive theme switcher. Select between 5 curated accents:
> - 🔮 **Mauve** (`#cba6f7`) — Signature Monolith Mauve
> - ⚡ **Tungsten** (`#fab387`) — Industrial Warm Metallic
> - 🩸 **Crimson** (`#f38ba8`) — High-Alert Cyberdeck
> - 🌊 **Sapphire** (`#74c7ec`) — Deep Space Subsurface
> - 🍃 **Emerald** (`#a6e3a1`) — Low-Power Tactical
> 
> Running `synapse-theme --sync-boot` or `synapse-theme --sync-greeter` synchronizes the selected accent across Plymouth boot splash frames and SDDM login greeters.

---

## 5. Updates & System Maintenance

### Q: How do I update SynapseOS safely?
> **A:** As an Arch Linux rolling release derivative, you update packages using `pacman`:
> ```bash
> sudo pacman -Syu
> ```
> Before any package update is written to disk, `snap-pac` automatically captures a Btrfs pre-update snapshot. If an upstream update ever causes an issue, you can immediately reboot and select the prior snapshot from GRUB or execute `sudo snapper rollback`.
