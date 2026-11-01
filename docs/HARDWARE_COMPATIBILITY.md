# SynapseOS — Hardware Compatibility & Platform Matrix

> **Surgical precision. Zero friction.**  
> Official hardware compatibility tiers, benchmarked platforms, and hardware daemon orchestration guide.

---

## 1. Hardware Compatibility Tiers

SynapseOS is engineered from the ground up to squeeze maximum deterministic throughput out of modern `x86_64` microarchitectures while maintaining full operational resilience.

```markdown
| Tier | Architecture Profile | Target Hardware Platforms | Supported Subsystems | Validation Status |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 0: Reference Platform** | Intel 8th Gen Kaby Lake-R / UHD 620, AVX2, BMI2, 16–32 GB RAM | **Dell Latitude 7490** | • Full `linux-cachyos` BORE<br>• TLP + `throttled` 25W PL1 override<br>• ZRAM 8GB (swappiness=180)<br>• PipeWire 64/48000 low-latency<br>• Local Ollama Qwen2.5-coder CPU inference | **100% Certified Reference**<br>(279/279 Gates passing) |
| **Tier 1: Certified Cyberdecks** | AMD Ryzen 5000/7000/8000 & Intel Core 11th–14th Gen / Core Ultra | **ThinkPad T14 / T480 / X1 Carbon Gen 6–12**<br>**Framework 13 (AMD & Intel)**<br>**Framework 16** | • Zero-friction Wi-Fi/BT (Intel ax200/ax210, MediaTek MT7922)<br>• Sway Wayland Fractional Scaling<br>• Calamares Btrfs automated rollback snapshots<br>• Fingerprint GUI authentication | **Fully Verified & Certified** |
| **Tier 2: Modern Generic x86_64** | Any x86_64 CPU supporting `AVX2`, `BMI2`, `FMA3`, 8GB+ RAM, NVMe/SATA | Modern Custom Desktops (Ryzen / Intel), ASUS ZenBook/ROG, HP Spectre, Acer Swift | • CachyOS `x86-64-v3` precompiled packages<br>• Vulkan GPU acceleration (AMD Radeon, Intel Arc/Iris, NVIDIA via proprietary driver module) | **Fully Supported** |
| **Tier 3: Legacy / Constrained** | Legacy x86_64 without AVX2 (`x86-64-v2`), 4–8 GB RAM, HDD/eMMC | Older laptops (Intel 2nd–5th Gen), low-power Celeron/Pentium | • Standard Arch upstream kernels fallback<br>• Single-thread constrained CPU LLM mode (`synapse-power --low-mem`) | **Compatible** (V2 Fallback) |
```

---

## 2. Platform Specifics: The Reference Platform (Dell Latitude 7490)

The Dell Latitude 7490 serves as the primary development and reference hardware for SynapseOS:
- **Processor**: Intel Core i5-8350U / i7-8650U (4 cores / 8 threads, 15W nominal TDP).
- **Thermal Envelope Expansion**: In standard Linux, Dell EC limits the CPU to 15W sustained power (PL1). SynapseOS deploys `throttled` (formerly `lenovo-throttling-fix` ported to Dell Latitude platforms), unlocking sustained **25W PL1 / 44W PL2** power limits. This results in up to a **38% speedup** in local LLM inference token generation and Rust compile times without thermal throttling.
- **Audio Subsystem**: Realtek ALC3246 HD Audio managed via PipeWire + WirePlumber with custom low-latency quantum configurations (`audio-switch`).
- **Network Posture**: Dual-interface setup (Intel I219-LM Gigabit Ethernet for primary low-jitter operations, and Intel Wireless-AC 8265 with full MAC randomization and RFC 4941 IPv6 privacy extensions).

---

## 3. The `synapse-hardware` CLI Orchestrator

SynapseOS ships with a native hardware CLI utility located at `/usr/bin/synapse-hardware`. It exposes unified terminal commands and JSON output for statusbars (Waybar and polybar):

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SYNAPSE-HARDWARE SUITE                          │
├───────────────────────────────────┬────────────────────────────────────┤
│ CLI Commands                      │ Actions                            │
├───────────────────────────────────┼────────────────────────────────────┤
│ synapse-hardware status           │ Live diagnostics cockpit           │
│ synapse-hardware power <mode>     │ Sets CPU governor & EPP profile    │
│ synapse-hardware audio <mode>     │ Adjusts PipeWire buffer quantum    │
│ synapse-hardware bar              │ Outputs formatted JSON for Waybar  │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Usage Examples:

#### 1. Inspect Hardware Telemetry Cockpit
```bash
synapse-hardware status
```
*Outputs current CPU governor, live core clock frequency, package thermals, PipeWire quantum buffer size, and active energy performance profiles.*

#### 2. Switch Power Profiles
```bash
# High throughput during compilation or LLM generation:
synapse-hardware power performance

# Balanced daily desktop operation:
synapse-hardware power balanced

# Maximum battery savings on mobile battery power:
synapse-hardware power eco
```

#### 3. Adjust PipeWire Audio Latency
```bash
# Ultra-low latency for audio production or real-time monitoring (128 samples / 2.7ms):
synapse-hardware audio low-latency

# Default balanced playback (512 samples / 10.6ms):
synapse-hardware audio default

# Power-efficient deep buffering (1024 samples / 21.3ms):
synapse-hardware audio efficient
```

#### 4. Status Bar Integration (`waybar`)
Add the module to `~/.config/waybar/config.jsonc`:
```jsonc
"custom/hardware": {
    "exec": "/usr/bin/synapse-hardware bar",
    "return-type": "json",
    "interval": 5,
    "on-click": "kitty --class synapse-floating -e /usr/bin/synapse-hardware status",
    "tooltip": true
}
```

---

## 4. Discrete GPU Acceleration (NVIDIA / AMD / Intel Arc)

- **AMD Radeon Graphics**: Handled automatically via open-source `mesa` and `vulkan-radeon` (RADV) driver. Zero manual intervention needed.
- **Intel Arc & Iris Xe**: Handled automatically via `vulkan-intel` (ANV) with Xe kernel driver support.
- **NVIDIA Dedicated GPUs**:
  - The live image boots using open-source `nouveau` mode or fallback KMS.
  - After installation, proprietary drivers can be installed via Calamares or standard pacman:
    ```bash
    sudo pacman -S nvidia-cachyos-dkms nvidia-utils
    ```

