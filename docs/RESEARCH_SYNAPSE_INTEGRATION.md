# Research: Integrating the Synapse Repository into SynapseOS

## 1. Architectural Challenge

The user needs the `synapse` repository to be deeply embedded into **SynapseOS** as a first-class core OS package. However, in Linux distribution engineering, improper repo coupling leads to:
- Bloated git repositories (mixing large ISO build systems with application source trees).
- Submodule synchronization drift and merge hell.
- Fragile build dependencies where OS ISO compilation fails if application tests break.

---

## 2. Integration Models Evaluated

| Model | Mechanics | Pros | Cons | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **1. Monorepo Copy** | Entire `synapse` source committed inside `synapseOS/src/synapse` | Single repository | Merging upstream updates is chaotic; git history pollution; breaks independent release tags | ❌ Not Recommended |
| **2. Git Submodule** | `packages/core/synapse/src` tracks `earnerbaymalay/synapse.git` | Direct branch tracking; precise commit pinning | Submodule checkout friction for new contributors; dirty worktree states | ⚠️ Secondary Option |
| **3. Native PKGBUILD Package Pipeline** | Dedicated `PKGBUILD` pulling signed releases/commits into binary repo `[synapseos]` | **Distribution standard** (Arch, Fedora, Debian); builds in clean chroots; zero repo bloat; reproducible | Requires package build repository pipeline | ✅ **Strongly Recommended** |

---

## 3. Recommended Approach: The Native OS Package Pipeline

### Step 1: Package Specification (`synapse-core/PKGBUILD`)
Inside `packages/core/synapse-core/PKGBUILD`:

```bash
# Maintainer: SynapseOS Engineering Team
pkgname=synapse-core
pkgver=0.1.0
pkgrel=1
pkgdesc="Core AI runtime gateway, context firewall, and cross-session agent memory daemon"
arch=('x86_64')
url="https://github.com/earnerbaymalay/synapse"
license=('MIT' 'Apache-2.0')
depends=('gcc-libs' 'glibc' 'openssl' 'sqlite')
makedepends=('cargo' 'rust' 'pnpm' 'git')
source=("git+https://github.com/earnerbaymalay/synapse.git#branch=main"
        "synapse.service"
        "synapse-user.service"
        "sysusers.conf"
        "tmpfiles.conf")
sha256sums=('SKIP'
            '...'
            '...'
            '...'
            '...')

prepare() {
  cd "$srcdir/synapse"
  cargo fetch --locked --target "$CARCH-unknown-linux-gnu"
}

build() {
  cd "$srcdir/synapse"
  export RUSTUP_TOOLCHAIN=stable
  export CARGO_TARGET_DIR=target
  RUSTFLAGS="-C target-cpu=x86-64-v3 -C opt-level=3" cargo build --release --locked --bin synapse
}

package() {
  cd "$srcdir/synapse"

  # Install binary
  install -Dm755 target/release/synapse "$pkgdir/usr/bin/synapse"

  # Install systemd service units
  install -Dm644 "$srcdir/synapse.service" "$pkgdir/usr/lib/systemd/system/synapse.service"
  install -Dm644 "$srcdir/synapse-user.service" "$pkgdir/usr/lib/systemd/user/synapse.service"

  # Install default configuration
  install -Dm644 fixtures/default-config.toml "$pkgdir/etc/synapse/config.toml"

  # Shell completions
  install -d "$pkgdir/usr/share/bash-completion/completions"
  "$pkgdir/usr/bin/synapse" completions bash > "$pkgdir/usr/share/bash-completion/completions/synapse" 2>/dev/null || true
}
```

### Step 2: System Integration Hooks
1. **User Profile Skeleton (`/etc/skel/.synapse`)**:
   - Every new user account on SynapseOS automatically has `~/.synapse/` initialized with:
     - `config.toml`: pre-configured loopback gateway (`127.0.0.1:8000`).
     - Memory directory structure (`~/.synapse/memory/`).
     - Pre-configured shell hooks for `UserPromptSubmit`, `PostToolUse`, and `SessionStart`.
2. **System Service Activation (`preset`)**:
   - In `/usr/lib/systemd/system-preset/50-synapseos.preset`:
     ```ini
     enable synapse.service
     enable ollama.service
     enable ananicy-cpp.service
     ```
3. **Claude Code & Agent Autowiring**:
   - When a user launches an AI CLI (`claude`, `antigravity`, or terminal chat), SynapseOS's global environment (`/etc/profile.d/synapse-agent.sh`) auto-detects and points agent hooks directly to the local daemon without manual user setup!
