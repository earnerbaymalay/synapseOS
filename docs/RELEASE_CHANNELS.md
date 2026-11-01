# SynapseOS — Release Channels & Update Streams

> **Surgical precision. Zero friction.**  
> Continuous delivery model, release channel definitions, and snapshot-guarded update cycles.

---

## 1. Release Channel Architecture

SynapseOS combines the rapid innovation of Arch Linux rolling packages with deterministic engineering gates. To serve both production mission-critical workstations and bleeding-edge testers, SynapseOS provides three distinct release streams:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        RELEASE CHANNELS                                │
├────────────────────────────────────────────────────────────────────────┤
│  [Nightly / Git CI]   -->   [Canary / Dev]   -->   [Stable Channel]    │
│  Continuous Builds          Bi-Weekly ISOs         Quarterly Milestones│
│  Git commit HEAD            Staged Testing         Signed SHA256 / GPG │
└────────────────────────────────────────────────────────────────────────┘
```

```markdown
| Dimension | Stable Channel (`main`) | Canary / Dev Channel (`canary`) | Nightly Stream (`staging-ci`) |
| :--- | :--- | :--- | :--- |
| **Target Audience** | Primary development workstations, daily drivers | Testers, contributors, hardware porting | Automated headless CI test matrix |
| **Release Cadence** | Quarterly ISO milestones + verified updates | Bi-weekly ISO snapshots | Headless container build per commit |
| **Kernel Stream** | Vetted `linux-cachyos` BORE (LTS or pinned) | Latest upstream `linux-cachyos` BORE | Bleeding-edge kernel branch |
| **Verification Gate** | **100% Pass** across all 279 checks + QEMU | Automated gate pass + basic smoke test | Dry-run & container compilation |
| **Package Repository** | `[synapseos]` (GPG-signed database) | `[synapseos-testing]` | Local chroot builds |
| **Rollback Safety** | Automated Btrfs pre-update snapshot (`snap-pac`) | Automated Btrfs pre-update snapshot | Manual volume rollback |
```

---

## 2. Channel Descriptions

### 2.1 Stable Channel (`synapseos-stable`)
- **Recommended for 95% of users.**
- Delivers polished, fully signed ISO releases (e.g., `v0.1.0-alpha.2`, `v0.1.0-beta`, `v1.0`).
- Packages under `[synapseos]` are audited and cryptographically signed with detached GPG signatures.
- Updates arrive via regular `pacman -Syu`.

### 2.2 Canary / Dev Channel (`synapseos-canary`)
- Built directly from active feature branches in the `synapseOS` repository.
- Receives experimental HUD widgets, bleeding-edge PipeWire latency configurations, and early microarchitecture flags.
- ISO images are uploaded bi-weekly as GitHub Pre-Releases marked with tag suffix `-canary`.

### 2.3 Nightly Stream (`synapseos-nightly`)
- Headless automated builds triggered on every push to `main` and scheduled daily at 02:00 UTC via GitHub Actions.
- Produces ephemeral ISO artifacts retained for 14 days under the GitHub Actions **Artifacts** tab.
- Used by automated verification harnesses to prevent regression leaks into the stable repository.

---

## 3. Configuring Repositories in `/etc/pacman.conf`

The package repository stream is governed by `/etc/pacman.conf`:

### Default (Stable Channel):
```ini
[synapseos]
SigLevel = Required DatabaseOptional
Server = https://raw.githubusercontent.com/earnerbaymalay/synapseOS/main/out/repo

[cachyos-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist

[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist
```

### Switching to Canary / Testing Channel:
```ini
[synapseos-testing]
SigLevel = Optional TrustAll
Server = https://raw.githubusercontent.com/earnerbaymalay/synapseOS/canary/out/repo

[synapseos]
SigLevel = Required DatabaseOptional
Server = https://raw.githubusercontent.com/earnerbaymalay/synapseOS/main/out/repo
```

---

## 4. Automated Rollback & Snapper Integration

SynapseOS installs with Btrfs snapshot hooks pre-activated in pacman (`/usr/share/libalpm/hooks/00-snapper-pre.hook`):
1. **Pre-Transaction Snapshot**: Before `pacman` removes, modifies, or writes a single package file, a read-only Btrfs snapshot of the root subvolume (`@`) is captured into `@snapshots`.
2. **Post-Transaction Snapshot**: A paired snapshot is captured after completion, recording the exact filesystem delta.

### How to Roll Back a Failed Update:

#### Method 1: Graphical Bootloader Menu
1. Reboot the computer.
2. In the GRUB menu, highlight **SynapseOS Snapshots**.
3. Select the snapshot taken right before your last update.
4. The system boots into a pristine, read-only copy of the working state.
5. Launch terminal and run `sudo snapper rollback` to make the current state permanent, then reboot.

#### Method 2: Command Line Rollback
```bash
# 1. View snapshot history with timestamps and descriptions:
sudo snapper list

# 2. Revert root subvolume to snapshot #14:
sudo snapper rollback 14

# 3. Reboot into restored state:
sudo reboot
```

