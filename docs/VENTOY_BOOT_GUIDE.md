# SynapseOS — Ventoy Multi-Boot Installation Guide

> **Surgical precision. Zero friction.**  
> Comprehensive end-to-end walkthrough for burning, configuring, and booting SynapseOS from a multi-ISO Ventoy flash drive.

---

## 1. Overview: Why Ventoy?

[Ventoy](https://www.ventoy.net/) is an open-source tool that allows you to write the bootloader to a USB drive once, after which you simply copy `.iso` files directly onto the drive like files on a standard thumb drive.

### Advantages for SynapseOS:
- **Multi-Boot**: Keep `synapseos-2026.11.01-x86_64.iso` alongside recovery distros (Clonezilla, GParted, Arch Linux, Windows PE) on a single drive.
- **Integrity**: Ventoy boots directly from the ISO file without extracting or altering filesystem permissions.
- **UEFI & Legacy Support**: Compatible with modern UEFI GPT systems as well as legacy BIOS MBR motherboards.
- **Persistence**: Storage partition remains usable for general file transfers, model weights, and offline toolkits.

---

## 2. Phase 1: Creating the Ventoy USB Drive

### Option A: Using Linux CLI (Recommended for Developers)
1. Install `ventoy` from your distribution repository:
   ```bash
   # Arch Linux / EndeavourOS / SynapseOS:
   sudo pacman -S ventoy

   # Debian / Ubuntu:
   sudo apt install ventoy
   ```
   *(Or download the official tarball from [github.com/ventoy/Ventoy/releases](https://github.com/ventoy/Ventoy/releases).)*

2. Identify your USB drive's block device name:
   ```bash
   lsblk -d -o NAME,SIZE,MODEL,TRAN
   ```
   *Example: `/dev/sdb` (Ensure you target the whole device, not a partition like `/dev/sdb1`).*

3. Format the drive with GPT partition table and UEFI support:
   ```bash
   # -i = install, -g = GPT partition table (essential for modern UEFI)
   sudo ventoy -i -g /dev/sdX
   ```
   > [!CAUTION]
   > Replace `/dev/sdX` with your exact drive identifier. All existing data on the target USB will be wiped.

### Option B: Using Graphical Installer (Windows or Linux GUI)
1. Download `ventoy-x.x.xx-windows.zip` or `ventoy-x.x.xx-linux.tar.gz`.
2. Extract and launch `Ventoy2Disk.exe` (Windows) or `VentoyGUI.x86_64` (Linux).
3. Under **Option** $\rightarrow$ **Partition Style**, select **GPT**.
4. Under **Option** $\rightarrow$ **Secure Boot Support**, ensure it is checked.
5. Select your USB device from the dropdown and click **Install**.

---

## 3. Phase 2: Copying the SynapseOS ISO & Verifying Checksums

1. Download or locate your compiled SynapseOS ISO image:
   - File: `synapseos-2026.11.01-x86_64.iso`
   - Release: `v0.1.0-alpha.2` or latest channel build

2. Compute the cryptographic hash and compare against official `SHA256SUMS`:
   ```bash
   sha256sum synapseos-2026.11.01-x86_64.iso
   ```
   *Verify that the output exactly matches the hash published on the release page.*

3. Mount the newly created `Ventoy` storage partition (formatted as exFAT) and copy the ISO file:
   ```bash
   cp synapseos-2026.11.01-x86_64.iso /run/media/$USER/Ventoy/
   sync
   ```
   *(On Windows, simply drag and drop the `.iso` file into the `Ventoy` drive letter).*

---

## 4. Phase 3: Hardware Boot Override Keys

Insert the Ventoy USB drive into your powered-down computer. Power on the machine and immediately tap the vendor-specific Boot Menu key until the boot selection menu appears:

| Hardware Vendor | Boot Menu Key | BIOS/UEFI Setup Key | Hardware Notes |
| :--- | :--- | :--- | :--- |
| **Dell** (Latitude, XPS, Inspiron, Precision) | **`F12`** | `F2` | Reference platform (`F12` One-Time Boot Menu) |
| **Lenovo** (ThinkPad T/X/P, IdeaPad) | **`F12`** | `F1` (or `Enter`) | On select ThinkPads, press `Fn + F12` |
| **Framework** (Laptop 13 & 16) | **`F12`** | `F2` | Native InsydeH2O UEFI bootloader |
| **HP** (EliteBook, ProBook, ZBook, Spectre) | **`F9`** | `F10` (or `Esc`) | Tap `Esc` first to view the Startup Menu |
| **ASUS** (ROG, TUF, ZenBook, Motherboards) | **`F8`** or **`Esc`** | `Del` or `F2` | Motherboards use `F8`; laptops often use `Esc` |
| **MSI** (Laptops & Motherboards) | **`F11`** | `Del` | Tap rapidly during POST |
| **Acer** (Swift, Predator, Aspire) | **`F12`** | `F2` | May require enabling `F12 Boot Menu` in BIOS |
| **Apple** (Intel-based Mac) | **`Option` / `Alt`** | N/A | Hold `Option` immediately after chime |

From the menu, select your USB drive (marked as `UEFI: <Device Name>, Partition 1`).

---

## 5. Phase 4: Secure Boot & Ventoy MOK Enrollment

SynapseOS runs the custom high-performance `linux-cachyos` BORE kernel.

### Recommended Path: Disable Secure Boot
For maximum hardware acceleration, kernel module compiling (`dkms`), and zero friction:
1. Enter BIOS/UEFI Setup (e.g. `F2` on Dell, `F1` on ThinkPad).
2. Navigate to **Security** $\rightarrow$ **Secure Boot**.
3. Toggle **Secure Boot Enable** to **Disabled**.
4. Save and reboot (`F10`).

### Alternative Path: Enroll Ventoy MOK Key
If your device firmware is locked by institutional policy or requires Secure Boot enabled:
1. When booting into Ventoy, if you see the blue screen stating `Verification failed: (0x1A) Security Violation`, press `Enter`.
2. This launches the **Shim UEFI Key Management (MOK)** menu:
   - Select **Enroll Key from Disk**
   - Select the `VTOYEFI` partition
   - Select `ENROLL_THIS_KEY_IN_MOKLIST.cer`
   - Select **Continue** $\rightarrow$ **Yes**
   - Enter password: `ventoy` (all lowercase)
3. Select **Reboot**. Ventoy will now boot with Secure Boot enabled.

---

## 6. Phase 5: Ventoy Boot Mode Selection

Once inside the Ventoy graphical boot menu:
1. Use arrow keys to select `synapseos-2026.11.01-x86_64.iso` and press `Enter`.
2. A secondary menu will appear asking for the launch mode:
   - **Boot in Normal Mode** *(Default & Recommended)*: Passes direct kernel execution to `systemd-boot`.
   - **Boot in Grub2 Mode**: Fallback mode if your UEFI implementation has quirks with native PE loaders.
   - **Boot in Memdisk Mode**: Do NOT use (SynapseOS live image is ~3 GB and does not require memdisk loading).
3. The laser-engraved `synapse-plymouth` boot splash will initialize, followed by the chamfered `synapse-greeter` login screen.

---

## 7. Troubleshooting Ventoy Boot Issues

| Symptom | Root Cause | Resolution |
| :--- | :--- | :--- |
| **Black screen after selecting ISO** | Kernel modesetting conflict with older Intel or discrete GPU | In the boot menu, press `e` to edit kernel command line, append `nomodeset` or `i915.modeset=1`, and press `Ctrl+X`. |
| **Ventoy menu does not appear; boots straight to Windows** | Windows Fast Startup locked the EFI controller or USB boot priority is low | In Windows, disable Fast Startup (`Power Options`). In BIOS, move USB Storage above Windows Boot Manager. |
| **"No media found" during pacstrap/live mount** | Slow USB 2.0 handshake or corrupted ISO copy | Re-copy ISO to the Ventoy partition and run `sync` before unmounting. Ensure USB is plugged into a USB 3.0/3.1 port. |
| **Resolution is stretched or low** | UEFI fallback resolution selected | In BIOS setup, ensure Video/Display mode is set to Native resolution or UEFI High-Resolution mode. |

