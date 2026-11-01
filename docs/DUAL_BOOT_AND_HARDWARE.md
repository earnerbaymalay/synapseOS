# SynapseOS — Installation & Hardware Setup Guide

> **Surgical precision. Zero friction.**  
> Definitive instructions for installing SynapseOS either as a standalone primary operating system or side-by-side alongside existing operating systems (Windows 11/10 / Linux).

---

## 1. Choosing Your Installation Strategy

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   INSTALLATION STRATEGY COMPARISON                       │
├────────────────────────────────────┬─────────────────────────────────────┤
│      FULL OS REPLACEMENT (A++)     │          DUAL-BOOT COEXISTENCE      │
├────────────────────────────────────┼─────────────────────────────────────┤
│ • Complete NVMe drive allocation   │ • Preserves Windows / secondary OS  │
│ • Btrfs zstd @ subvolumes          │ • Reuses existing EFI partition     │
│ • Zero Windows telemetry residue   │ • Requires Fast Startup disabled   │
│ • Automated snapshot rollbacks     │ • Clock synced to UTC (Windows RTC) │
│ • Optional full LUKS encryption    │ • Independent OS choice via GRUB    │
└────────────────────────────────────┴─────────────────────────────────────┘
```

---

## 2. Pre-Installation Hardware & Firmware Checklist

Before booting the installer, review these vendor-specific requirements to avoid firmware-level conflicts:

### 2.1 Dell (Reference Platform: Latitude 7490, XPS 13/15/17, Precision)
- [ ] **SATA Operation / Storage Controller**:
  - Navigate to `System Configuration` $\rightarrow$ `SATA Operation`.
  - **CRITICAL**: Change from **RAID On** (Intel RST) to **AHCI / NVMe**.  
    *(If keeping Windows, see Section 3 below to switch Windows to AHCI before changing BIOS).*
- [ ] **Secure Boot**: Set `Secure Boot Enable` to `Disabled`.
- [ ] **Fastboot**: Set to `Thorough` (ensures full USB and PCIe bus initialization on every boot).
- [ ] **Thunderbolt Security**: Set to `No Security` or `User Authorization` for docking stations.

### 2.2 Lenovo ThinkPad (T14, T480, T490, X1 Carbon Gen 6–12, P-series)
- [ ] **Security Chip**: Ensure `Security` $\rightarrow$ `Secure Boot` is `Disabled`.
- [ ] **Sleep State**: Set `Config` $\rightarrow$ `Power` $\rightarrow$ `Sleep State` to `Linux` (S3) or `Modern Standby` depending on generation.
- [ ] **ThinkShield / USB Access**: Set `Security` $\rightarrow$ `USB UEFI BIOS Support` to `Enabled`.

### 2.3 Framework Laptop (Laptop 13 Intel/AMD, Laptop 16)
- [ ] **Storage Mode**: Native NVMe (zero proprietary controller shims).
- [ ] **Secure Boot**: In InsydeH2O setup, toggle `Secure Boot` to `Disabled`.
- [ ] **Expansion Ports**: Ensure USB flash drive is connected directly to a high-speed Type-C or Type-A module.

### 2.4 HP (EliteBook, ZBook, ProBook, Spectre)
- [ ] **Fast Boot**: In BIOS (`F10`), set `Fast Boot` to `Disabled`.
- [ ] **Intel VMD Technology**: On 11th–14th Gen Intel platforms, set `Intel VMD Controller` to `Disabled` to expose NVMe block devices directly to the Linux kernel.

### 2.5 Custom Desktop Motherboards (ASUS, MSI, Gigabyte, ASRock)
- [ ] **CSM (Compatibility Support Module)**: Keep `Disabled` (Pure UEFI mode).
- [ ] **Secure Boot OS Type**: Set to `Other OS` instead of `Windows UEFI mode`.
- [ ] **XMP / EXPO**: Ensure memory profiles are stable prior to OS deployment.

---

## 3. Preparing Windows for Dual-Boot Coexistence

If you plan to install SynapseOS alongside an existing Windows installation, complete these steps in Windows first:

### Step 1: Disable Windows Fast Startup
Windows "Fast Startup" puts the filesystem into a hibernated, locked state that prevents Linux from safely reading partitions or mounting storage:
1. Open Windows Control Panel $\rightarrow$ **Power Options**.
2. Click **Choose what the power buttons do**.
3. Click **Change settings that are currently unavailable**.
4. Uncheck **Turn on fast startup (recommended)** and click **Save changes**.

### Step 2: Suspend BitLocker Disk Encryption
1. Open PowerShell or Command Prompt as Administrator.
2. Execute:
   ```cmd
   manage-bde -protectors -disable C:
   ```
   *(This ensures the partition can be safely shrunk without triggering recovery keys).*

### Step 3: Switch Windows from RAID/RST to AHCI (If Required)
If your Dell or laptop was set to RAID/Intel RST by default:
1. Run `cmd.exe` as Administrator.
2. Force Windows to boot in Safe Mode on next restart:
   ```cmd
   bcdedit /set {current} safeboot minimal
   ```
3. Restart your computer and enter BIOS setup (`F2` or `F12`).
4. Change SATA Operation from **RAID On** to **AHCI**.
5. Save changes and boot into Windows (it will load Safe Mode and automatically install AHCI drivers).
6. Run `cmd.exe` as Administrator again and remove the Safe Mode flag:
   ```cmd
   bcdedit /deletevalue {current} safeboot
   ```
7. Reboot into normal Windows. AHCI is now permanently active.

### Step 4: Shrink Windows Partition
1. Press `Win + X` and select **Disk Management** (`diskmgmt.msc`).
2. Right-click your main Windows volume (`C:`) and select **Shrink Volume...**.
3. Allocate unallocated space for SynapseOS:
   - Minimum: `64 GB` (65536 MB)
   - Recommended: `128 GB+` (131072 MB) for local LLM weights and container builds.
4. Click **Shrink**. Leave the resulting space as **Unallocated**.

---

## 4. Calamares Installation Walkthrough

Boot your Ventoy or installation media and open the **Install SynapseOS** shortcut from the desktop or HUD (`Super+i`).

```
┌────────────────────────────────────────────────────────────────────────┐
│                      CALAMARES PARTITIONING CHOICES                    │
├───────────────────────────────────┬────────────────────────────────────┤
│ Option A: Full OS Replacement     │ Option B: Dual-Boot Coexistence    │
│ (Automated Btrfs @ subvolumes)    │ (Manual Partitioning)              │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Strategy A: Full OS Replacement (Clean Wipe)
1. In the **Partitions** screen, select **Erase disk**.
2. Choose **Btrfs** filesystem.
3. Select whether to enable **Encrypt system** (LUKS full-disk encryption with passphrase prompt at Plymouth boot splash).
4. Calamares will automatically construct the optimized SynapseOS subvolume scheme:
   ```
   /dev/nvme0n1p1   1024 MB   FAT32   /boot/efi    (boot, esp)
   /dev/nvme0n1p2   Rest      Btrfs   /            (zstd:3)
                    ├── @           -> Mounted at /
                    ├── @home       -> Mounted at /home
                    ├── @snapshots  -> Mounted at /.snapshots
                    └── @var_log    -> Mounted at /var/log
   ```
5. Set your User Account details:
   - Live user password defaults to your choice.
   - Sudo privileges are granted via `wheel` group.
6. Click **Install**. Installation completes in ~3–5 minutes.

---

### Strategy B: Side-by-Side Dual-Boot (Manual Partitioning)
1. In the **Partitions** screen, select **Manual partitioning**.
2. Locate your existing **EFI System Partition (ESP)**:
   - Usually partition 1 (`/dev/nvme0n1p1` or `/dev/sda1`, ~100–512 MB, FAT32, `boot, esp` flags).
   - Click **Edit**.
   - Set **Mount Point**: `/boot/efi`.
   - **CRITICAL**: Ensure **Format** checkbox is **UNCHECKED**. *(Do not format your existing Windows bootloader!)*.
3. Locate the **Free Space** (unallocated space shrunk in Step 3):
   - Click **Create**.
   - Size: Use all remaining free space (or desired amount).
   - Filesystem: **Btrfs** (or **ext4**).
   - Mount Point: `/`.
   - Flags: leave default.
4. Set the **Boot Loader Location** dropdown to the drive's master MBR or EFI System Partition (e.g. `/dev/nvme0n1`).
5. Proceed through User Setup and begin installation.
6. Calamares will install SynapseOS and configure GRUB with `os-prober`, automatically adding a **Windows Boot Manager** boot option.

---

## 5. Post-Installation Clock & RTC Synchronization

Linux and Windows interpret hardware clock (RTC) timestamps differently by default:
- Linux assumes hardware RTC is stored in **UTC**.
- Windows assumes hardware RTC is stored in **Local Time**.

To prevent clock desynchronization in dual-boot systems:

### Recommended: Configure Windows to use UTC
In Windows, open PowerShell as Administrator and run:
```powershell
reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /t REG_DWORD /d 1 /f
```
Both operating systems will now agree on UTC timestamps.

### Alternative: Configure SynapseOS to use Local Time
If you cannot modify Windows registry keys, run this command in SynapseOS:
```bash
timedatectl set-local-rtc 1 --adjust-system-clock
```

---

## 6. Snapshot Rollback Safety

All SynapseOS installations configured with Btrfs include automated pre-update snapshots (`snap-pac` + `snapper`). If any rolling update or kernel experiment ever destabilizes your configuration:

1. In GRUB, choose **SynapseOS Snapshots** to boot into any read-only snapshot directly.
2. Or from a terminal:
   ```bash
   # List existing snapshots:
   sudo snapper list

   # Roll back to snapshot before the update:
   sudo snapper rollback <snapshot_number>
   sudo reboot
   ```

