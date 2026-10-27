# SynapseOS

> **An AI-Native Rolling Linux Distribution**  
> *Engineered for High-Throughput Agentic Development, Cyber Resilience, and Kernel Performance.*

```
   █████████  ███    ███  ███   ███  █████████     ████████   ░██████    ███████
  ███░░░░░███░███   ░░███░███  ░███ ░███░░░░░███  ███░░░░███ ░██░░░░███ ░██░░░░███
 ░███    ░░░ ░███    ░███░███  ░███ ░███    ░███ ░███   ░░░  ░██    ░███░██    ░░░ 
 ░░█████████ ░███    ░███░█████████ ░█████████   ░░████████  ░██    ░███░░█████████
  ░░░░░░░░███░░███   ███ ░░░░░░░███ ░███░░░░░      ░░░░░░███ ░██    ░███ ░░░░░░░░███
  ███    ░███ ░░░█████░    ░███ ░███ ░███        ███   ░███  ░██░░░░███  ███    ░███
 ░░█████████    ░░███      ░░██████  █████      ░░████████   ░████████  ░░█████████
  ░░░░░░░░░      ░░░        ░░░░░░  ░░░░░        ░░░░░░░░    ░░░░░░░░    ░░░░░░░░░ 
```

SynapseOS merges four powerful principles into one seamless operating system:

1. **CachyOS Performance**: Custom BORE / EEVDF CPU schedulers, x86-64-v3 microarchitecture optimization, aggressive ZRAM zstd compression, and Ananicy-CPP process auto-nicing.
2. **EndeavourOS Foundation**: Clean, unbloated upstream Arch Linux rolling foundation, transparent packaging, Calamares installer, and native systemd management.
3. **Omarchy Aesthetic**: Monospace terminal-first environment, unified Catppuccin Mocha Mauve + Liquid Chrome visuals, and instant Super-key command palettes.
4. **Synapse AI Core**: Deeply built into the core OS package (`synapse-core`), providing a localhost:8000 runtime proxy, bidirectional context firewall, 3-layer persistent agent memory, and local LLM routing out of the box.

---

## 📂 Repository Layout

```
synapseOS/
├── .agents/                 # Antigravity agent rules (Gemini 4 Argon configuration)
├── .vscode/                 # Antigravity IDE workspace settings
├── docs/                    # Technical research, architecture & design whitepapers
│   ├── ARCHITECTURE.md
│   ├── RESEARCH_SYNAPSE_INTEGRATION.md
│   ├── INSPIRATIONS_ANALYSIS.md
│   └── GIT_REPO_STRATEGY.md
├── build/                   # OS image generation profiles & ISO recipes (archiso)
├── packages/                # Native Arch Linux PKGBUILD recipes
│   ├── core/synapse-core/   # PKGBUILD for Synapse runtime gateway
│   └── desktop/             # SDDM themes, wallpapers, and desktop configs
├── overlay/                 # Root filesystem overlays (/etc, /etc/skel)
├── AGENTS.md                # System instructions & Prime Directive
├── GEMINI.md                # Gemini workspace settings
└── ROADMAP.md               # Implementation milestones
```

---

## 🚀 Quick Start (Development & Building)

```bash
# Clone the repository
git clone git@github.com:earnerbaymalay/synapseOS.git
cd synapseOS

# Inspect documentation
cat docs/ARCHITECTURE.md
cat docs/RESEARCH_SYNAPSE_INTEGRATION.md
```
