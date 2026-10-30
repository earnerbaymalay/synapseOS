#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Verification Harness (build/verify-gates.sh)
# Validates Engineering Gates G1, G2, G3, and G4 across the repository.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

pass() {
    echo "  [PASS] $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

warn() {
    echo "  [WARN] $1"
    WARN_COUNT=$((WARN_COUNT + 1))
}

fail() {
    echo "  [FAIL] $1" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

check_file_contains() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    if [[ ! -f "${file}" ]]; then
        fail "${description} (file missing: ${file#"${REPO_ROOT}/"})"
        return
    fi
    if grep -Eq "${pattern}" "${file}"; then
        pass "${description}"
    else
        fail "${description} (pattern '${pattern}' not found in ${file#"${REPO_ROOT}/"})"
    fi
}

check_file_lacks() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    if [[ ! -f "${file}" ]]; then
        fail "${description} (file missing: ${file#"${REPO_ROOT}/"})"
        return
    fi
    if grep -Pzq "${pattern}" "${file}"; then
        fail "${description} (forbidden pattern '${pattern}' found in ${file#"${REPO_ROOT}/"})"
    else
        pass "${description}"
    fi
}

echo "=============================================================================="
echo " SynapseOS Engineering Verification Harness (Gates G1 - G4)"
echo "=============================================================================="

# ------------------------------------------------------------------------------
# Gate G1: Package Verification (PKGBUILD syntax & metadata)
# ------------------------------------------------------------------------------
echo ""
echo "---> Gate G1: Native Package Verification (PKGBUILDs)"
EXPECTED_PKGBUILDS=(
    "${REPO_ROOT}/packages/core/synapse-core/PKGBUILD"
    "${REPO_ROOT}/packages/desktop/llm-quickfire-panel/PKGBUILD"
    "${REPO_ROOT}/packages/desktop/synapse-themes/PKGBUILD"
    "${REPO_ROOT}/packages/desktop/synapse-greeter/PKGBUILD"
    "${REPO_ROOT}/packages/desktop/synapse-plymouth/PKGBUILD"
)

for pkgbuild in "${EXPECTED_PKGBUILDS[@]}"; do
    rel_path="${pkgbuild#"${REPO_ROOT}/"}"
    if [[ -f "${pkgbuild}" ]]; then
        if bash -n "${pkgbuild}" 2>/dev/null; then
            pass "Syntax valid: ${rel_path}"
        else
            fail "Syntax error in ${rel_path}"
        fi
        check_file_contains "${pkgbuild}" "^pkgname=" "Metadata pkgname defined in ${rel_path}"
        check_file_contains "${pkgbuild}" "^pkgver=" "Metadata pkgver defined in ${rel_path}"
        check_file_contains "${pkgbuild}" "^arch=.*(x86_64|any)" "Architecture (x86_64|any) defined in ${rel_path}"
        check_file_contains "${pkgbuild}" "package\(\)" "package() function defined in ${rel_path}"
    else
        warn "Pending Phase 1 deliverable: ${rel_path} (not yet created in worktree)"
    fi
done

# ------------------------------------------------------------------------------
# Gate G2: Kernel, ZRAM & Stealth Network Posture (Prime Directive)
# ------------------------------------------------------------------------------
echo ""
echo "---> Gate G2: Kernel, Latency & Prime Directive Stealth Configs"
SYSCTL_CONF="${REPO_ROOT}/overlay/etc/sysctl.d/99-synapseos.conf"
if [[ -f "${SYSCTL_CONF}" ]]; then
    check_file_contains "${SYSCTL_CONF}" "vm\.swappiness[[:space:]]*=[[:space:]]*180" "ZRAM swappiness=180 in 99-synapseos.conf"
    check_file_contains "${SYSCTL_CONF}" "vm\.page-cluster[[:space:]]*=[[:space:]]*0" "ZRAM page-cluster=0 in 99-synapseos.conf"
    check_file_contains "${SYSCTL_CONF}" "vm\.vfs_cache_pressure[[:space:]]*=[[:space:]]*50" "vfs_cache_pressure=50 in 99-synapseos.conf"
    check_file_contains "${SYSCTL_CONF}" "tcp_congestion_control[[:space:]]*=[[:space:]]*bbr" "TCP BBR congestion control in 99-synapseos.conf"
else
    warn "Pending Phase 2 deliverable: overlay/etc/sysctl.d/99-synapseos.conf"
fi

ZRAM_CONF="${REPO_ROOT}/overlay/etc/systemd/zram-generator.conf"
if [[ -f "${ZRAM_CONF}" ]]; then
    check_file_contains "${ZRAM_CONF}" "compression-algorithm[[:space:]]*=[[:space:]]*zstd" "ZRAM zstd compression in zram-generator.conf"
else
    warn "Pending Phase 2 deliverable: overlay/etc/systemd/zram-generator.conf"
fi

NM_STEALTH_DIR="${REPO_ROOT}/overlay/etc/NetworkManager/conf.d"
if [[ -d "${NM_STEALTH_DIR}" ]]; then
    if grep -Rqs "scan-rand-mac-address=yes" "${NM_STEALTH_DIR}"; then
        pass "NetworkManager Wi-Fi scan MAC randomization enabled"
    else
        fail "NetworkManager scan-rand-mac-address=yes missing in ${NM_STEALTH_DIR}"
    fi
    if grep -Rqs "cloned-mac-address=random" "${NM_STEALTH_DIR}"; then
        pass "NetworkManager per-session cloned MAC randomization enabled"
    else
        fail "NetworkManager cloned-mac-address=random missing in ${NM_STEALTH_DIR}"
    fi
    if grep -Rqs "ip6-privacy=2" "${NM_STEALTH_DIR}"; then
        pass "NetworkManager RFC 4941 IPv6 privacy extensions enabled"
    else
        fail "NetworkManager ip6-privacy=2 missing in ${NM_STEALTH_DIR}"
    fi
else
    warn "Pending Phase 2 deliverable: overlay/etc/NetworkManager/conf.d"
fi

RESOLVED_DIR="${REPO_ROOT}/overlay/etc/systemd"
if [[ -d "${RESOLVED_DIR}" ]] && grep -Rqs "9\.9\.9\.9" "${RESOLVED_DIR}"; then
    pass "Quad9 DNS-over-TLS resolver (9.9.9.9) configured"
else
    warn "Pending Phase 2 deliverable: Quad9 DNS-over-TLS configuration in overlay/etc/systemd"
fi

# ------------------------------------------------------------------------------
# Gate G3: Cyberdeck UI, Picom, SDDM & Quickfire Configs
# ------------------------------------------------------------------------------
echo ""
echo "---> Gate G3: Cyberdeck UI, Picom, SDDM & Quickfire Configs"
PICOM_CONF="${REPO_ROOT}/overlay/etc/xdg/picom.conf"
if [[ -f "${PICOM_CONF}" ]]; then
    check_file_contains "${PICOM_CONF}" "dual_kawase" "Picom dual_kawase blur configured"
    check_file_contains "${PICOM_CONF}" "corner-radius" "Picom rounded corner-radius configured"
else
    warn "Pending Phase 3 deliverable: overlay/etc/xdg/picom.conf"
fi

SDDM_CONF_DIR="${REPO_ROOT}/overlay/etc/sddm.conf.d"
SDDM_CONF_FILE="${REPO_ROOT}/overlay/etc/sddm.conf"
if [[ -d "${SDDM_CONF_DIR}" ]] || [[ -f "${SDDM_CONF_FILE}" ]]; then
    check_file_contains "${REPO_ROOT}/overlay/etc/sddm.conf.d/10-synapseos.conf" "^Current=synapseos$" "SDDM theme set to synapseos (synapse-greeter)"
    check_file_contains "${REPO_ROOT}/overlay/etc/sddm.conf.d/10-synapseos.conf" "HideUsers=git,ollama,synapse-daemon" "SDDM HideUsers excludes live user 'synapse'"
else
    warn "Pending Phase 3 deliverable: SDDM configuration in overlay/etc/sddm*"
fi

SDDM_THEME_CONF="${REPO_ROOT}/packages/desktop/synapse-greeter/theme.conf"
SDDM_MAIN_QML="${REPO_ROOT}/packages/desktop/synapse-greeter/Main.qml"
SYNAPSE_SVC="${REPO_ROOT}/packages/core/synapse-core/synapse.service"
QF_THEME_BIN="${REPO_ROOT}/packages/desktop/llm-quickfire-panel/src/llm-quickfire-panel/bin/quickfire-theme"
QF_DESKTOP_SRC="${REPO_ROOT}/packages/desktop/llm-quickfire-panel/config/llm-quickfire-panel.desktop"

check_file_contains "${SDDM_THEME_CONF}" "^user=$" "SDDM synapseos theme.conf pins no host-specific user"
check_file_contains "${SDDM_THEME_CONF}" "^variant=monolith-mauve$" "SDDM synapseos theme defaults to monolith-mauve"
check_file_contains "${SDDM_MAIN_QML}" "#cba6f7" "SDDM Main.qml uses Catppuccin Mauve (#cba6f7)"
check_file_contains "${SDDM_MAIN_QML}" "#cdd6f4" "SDDM Main.qml uses Liquid Silver Chrome (#cdd6f4)"
check_file_contains "${SDDM_MAIN_QML}" "model: sessionModel" "SDDM Main.qml offers session selection (XFCE/Sway)"
check_file_contains "${SDDM_MAIN_QML}" "sddm\.login\(" "SDDM Main.qml authenticates via sddm.login"
check_file_contains "${SDDM_MAIN_QML}" "strokeStyle: ShapePath\.DashLine" "SDDM panel border carries animated accent trails"
check_file_contains "${REPO_ROOT}/packages/desktop/synapse-greeter/metadata.desktop" "^QtVersion=6$" "SDDM synapseos theme targets the Qt6 greeter"
if grep -Eq "password\.text\.length[[:space:]]*===[[:space:]]*0" "${SDDM_MAIN_QML}"; then
    fail "SDDM Main.qml blocks passwordless live user login"
else
    pass "SDDM Main.qml allows passwordless live user login"
fi
if grep -Eq "#5fb4ff|#2b6cc0|#174a8c|#7cc2ff" "${SDDM_MAIN_QML}"; then
    fail "SDDM Main.qml still contains legacy blue accent colors"
else
    pass "SDDM Main.qml has zero legacy blue accent colors"
fi

check_file_contains "${SYNAPSE_SVC}" "^User=synapse-daemon$" "synapse.service isolates DynamicUser as User=synapse-daemon"
check_file_contains "${SYNAPSE_SVC}" "^Group=synapse-daemon$" "synapse.service isolates DynamicUser as Group=synapse-daemon"
check_file_contains "${QF_DESKTOP_SRC}" "^Exec=/usr/bin/quickfire --autostart$" "llm-quickfire-panel.desktop uses /usr/bin/quickfire --autostart"
if grep -Fq "ps2-cyber-blue" "${QF_THEME_BIN}"; then
    fail "quickfire-theme still contains legacy ps2-cyber-blue option"
else
    pass "quickfire-theme has zero legacy ps2-cyber-blue references"
fi

SWAY_CONF="${REPO_ROOT}/overlay/etc/skel/.config/sway/config"
WAYBAR_CONF="${REPO_ROOT}/overlay/etc/skel/.config/waybar/config.jsonc"
WAYBAR_STYLE="${REPO_ROOT}/overlay/etc/skel/.config/waybar/style.css"

check_file_contains "${SWAY_CONF}" "Mod4\+space.*(/usr/bin/quickfire|\$menu)" "Sway config binds Mod4+space to /usr/bin/quickfire"
check_file_contains "${SWAY_CONF}" "Mod4\+d.*(/usr/bin/quickfire|\$menu)" "Sway config binds Mod4+d to /usr/bin/quickfire"
check_file_contains "${SWAY_CONF}" "Mod4\+Return.*(kitty|foot|\$term)" "Sway config binds Mod4+Return to kitty/foot"
check_file_contains "${SWAY_CONF}" "#11111b" "Sway config uses Obsidian Crust (#11111b)"
check_file_contains "${SWAY_CONF}" "#cba6f7" "Sway config uses Catppuccin Mocha Mauve (#cba6f7)"
check_file_contains "${SWAY_CONF}" "#cdd6f4" "Sway config uses Liquid Silver Chrome (#cdd6f4)"
check_file_contains "${WAYBAR_CONF}" "sway/workspaces" "Waybar config.jsonc defines sway/workspaces"
check_file_contains "${WAYBAR_STYLE}" "#11111b" "Waybar style.css uses Obsidian Crust (#11111b)"
check_file_contains "${WAYBAR_STYLE}" "#1e1e2e" "Waybar style.css uses Catppuccin Base (#1e1e2e)"
check_file_contains "${WAYBAR_STYLE}" "#cba6f7" "Waybar style.css uses Catppuccin Mocha Mauve (#cba6f7)"
check_file_contains "${WAYBAR_STYLE}" "#cdd6f4" "Waybar style.css uses Liquid Silver Chrome (#cdd6f4)"

if grep -Rqs -i "#00a8ff" "${REPO_ROOT}/overlay" "${REPO_ROOT}/packages/installer/calamares"; then
    fail "Legacy #00a8ff color found in overlay/ or Calamares branding"
else
    pass "Zero legacy #00a8ff references in overlay/ and Calamares branding"
fi

if [[ -f "${REPO_ROOT}/tests/test_iso_profile.py" ]]; then
    if command -v pytest >/dev/null 2>&1; then
        if pytest -q "${REPO_ROOT}/tests/test_iso_profile.py"; then
            pass "Pytest UI & architecture test suite (tests/test_iso_profile.py)"
        else
            fail "Pytest suite failed (tests/test_iso_profile.py)"
        fi
    elif command -v python3 >/dev/null 2>&1; then
        if python3 "${REPO_ROOT}/tests/test_iso_profile.py" >/dev/null 2>&1; then
            pass "Python unittest UI & architecture test suite (tests/test_iso_profile.py)"
        else
            fail "Python unittest suite failed (tests/test_iso_profile.py)"
        fi
    fi
fi

# ------------------------------------------------------------------------------
# Gate G4: Archiso Profile & Calamares Installer Integrity
# ------------------------------------------------------------------------------
echo ""
echo "---> Gate G4: Archiso Profile & Calamares Installer Integrity"
PROFILEDEF="${REPO_ROOT}/build/archiso/profiledef.sh"
PACKAGES_FILE="${REPO_ROOT}/build/archiso/packages.x86_64"
PACMAN_CONF="${REPO_ROOT}/build/archiso/pacman.conf"
CUSTOMIZE_SH="${REPO_ROOT}/build/archiso/airootfs/root/customize_airootfs.sh"
BUILD_ISO_SH="${REPO_ROOT}/build/build-iso.sh"

if bash -n "${PROFILEDEF}"; then
    pass "Archiso profiledef.sh bash syntax valid"
else
    fail "Archiso profiledef.sh has syntax errors"
fi

check_file_contains "${PROFILEDEF}" 'iso_name="synapseos"' "Archiso iso_name set to synapseos"
check_file_contains "${PROFILEDEF}" 'uefi-x64\.systemd-boot\.esp' "Archiso UEFI systemd-boot mode enabled"
check_file_contains "${PROFILEDEF}" 'bios\.syslinux\.mbr' "Archiso BIOS syslinux mode enabled"
check_file_contains "${PROFILEDEF}" 'zstd' "Archiso squashfs zstd compression enabled"

REQUIRED_PKGS=(
    "linux-cachyos"
    "linux-cachyos-headers"
    "ananicy-cpp"
    "cachyos-ananicy-rules"
    "zram-generator"
    "xfce4"
    "sddm"
    "picom"
    "kitty"
    "rofi"
    "sway"
    "waybar"
    "foot"
    "xorg-xwayland"
    "wl-clipboard"
    "grim"
    "slurp"
    "swayidle"
    "ollama"
    "uv"
    "rust"
    "ripgrep"
    "fd"
    "fzf"
    "bat"
    "eza"
    "jq"
    "lazygit"
    "git-delta"
    "firewalld"
    "wireshark-qt"
    "wireshark-cli"
    "termshark"
    "bettercap"
    "nmap"
    "macchanger"
    "synapse-core"
    "llm-quickfire-panel"
    "synapse-themes"
    "synapse-greeter"
    "synapse-plymouth"
    "plymouth"
)

for pkg in "${REQUIRED_PKGS[@]}"; do
    check_file_contains "${PACKAGES_FILE}" "^${pkg}$" "Package '${pkg}' present in packages.x86_64"
done

if grep -Eq "^(nohang|tshark)$" "${PACKAGES_FILE}"; then
    fail "packages.x86_64 contains unresolvable package names (nohang or tshark)"
else
    pass "packages.x86_64 excludes AUR/alias blockers (nohang, tshark)"
fi

check_file_contains "${PACMAN_CONF}" "^\[synapseos\]" "pacman.conf includes [synapseos] repo"
check_file_contains "${PACMAN_CONF}" "^\[cachyos-v3\]" "pacman.conf includes [cachyos-v3] repo"
check_file_contains "${PACMAN_CONF}" "^\[cachyos-core-v3\]" "pacman.conf includes [cachyos-core-v3] repo"
check_file_contains "${PACMAN_CONF}" "^\[cachyos-extra-v3\]" "pacman.conf includes [cachyos-extra-v3] repo"
check_file_contains "${PACMAN_CONF}" "^\[cachyos\]" "pacman.conf includes [cachyos] repo"
check_file_contains "${PACMAN_CONF}" "^\[core\]" "pacman.conf includes [core] repo"
check_file_contains "${PACMAN_CONF}" "^\[extra\]" "pacman.conf includes [extra] repo"

check_file_contains "${REPO_ROOT}/build/archiso/efiboot/loader/loader.conf" "01-synapseos-x86_64-linux\.conf" "UEFI loader.conf points to SynapseOS entry"
check_file_contains "${REPO_ROOT}/build/archiso/efiboot/loader/entries/01-synapseos-x86_64-linux.conf" "vmlinuz-linux-cachyos" "UEFI entry boots vmlinuz-linux-cachyos"
check_file_contains "${REPO_ROOT}/build/archiso/syslinux/syslinux.cfg" "vmlinuz-linux-cachyos" "BIOS syslinux.cfg boots vmlinuz-linux-cachyos"

if [[ -x "${CUSTOMIZE_SH}" ]] && bash -n "${CUSTOMIZE_SH}"; then
    pass "customize_airootfs.sh is executable and syntactically valid"
else
    fail "customize_airootfs.sh is not executable or has syntax errors"
fi

if [[ -x "${BUILD_ISO_SH}" ]] && bash -n "${BUILD_ISO_SH}"; then
    pass "build/build-iso.sh is executable and syntactically valid"
else
    fail "build/build-iso.sh is not executable or has syntax errors"
fi

if "${BUILD_ISO_SH}" --dry-run >/dev/null 2>&1; then
    pass "build/build-iso.sh --dry-run stages airootfs and validates profile"
else
    fail "build/build-iso.sh --dry-run failed to stage airootfs"
fi

if command -v shellcheck >/dev/null 2>&1; then
    if shellcheck "${BUILD_ISO_SH}" "${REPO_ROOT}/build/verify-gates.sh" "${PROFILEDEF}" "${CUSTOMIZE_SH}"; then
        pass "ShellCheck validation passed for all build & archiso scripts"
    else
        fail "ShellCheck reported warnings/errors in build scripts"
    fi
fi

# Stage A & B: Local [synapseos] repo, CachyOS mirrorlists, keyring & staged airootfs checks
if [[ -d "${REPO_ROOT}/out/repo" ]]; then
    for repo_artifact in \
        "${REPO_ROOT}/out/repo/synapseos.db.tar.gz" \
        "${REPO_ROOT}/build/archiso/airootfs/var/cache/synapseos-repo/synapseos.db.tar.gz"; do
        rel_art="${repo_artifact#"${REPO_ROOT}/"}"
        if [[ -f "${repo_artifact}" ]]; then
            pass "Repository database present: ${rel_art}"
        else
            fail "Repository database missing: ${rel_art}"
        fi
    done

    for built_pkg in "synapse-core" "llm-quickfire-panel" "synapse-themes" "synapse-greeter" "synapse-plymouth"; do
        if compgen -G "${REPO_ROOT}/out/repo/${built_pkg}-*.pkg.tar.*" >/dev/null; then
            pass "Compiled package archive in out/repo/: ${built_pkg}"
        else
            fail "Compiled package archive missing in out/repo/: ${built_pkg}"
        fi
    done
fi

check_file_contains "${REPO_ROOT}/build/archiso/airootfs/etc/pacman.d/cachyos-mirrorlist" "mirror\.cachyos\.org/repo/x86_64" "Staged airootfs CachyOS x86_64 mirrorlist"
check_file_contains "${REPO_ROOT}/build/archiso/airootfs/etc/pacman.d/cachyos-v3-mirrorlist" "mirror\.cachyos\.org/repo/x86_64_v3" "Staged airootfs CachyOS x86-64-v3 mirrorlist"
check_file_contains "${CUSTOMIZE_SH}" "F3B607488DB35A47" "customize_airootfs.sh imports and signs CachyOS key (F3B607488DB35A47)"
check_file_contains "${REPO_ROOT}/build/archiso/airootfs/etc/skel/.config/sway/config" "Mod4\+space.*(/usr/bin/quickfire|\$menu)" "Staged airootfs includes Sway config"
check_file_contains "${REPO_ROOT}/build/archiso/airootfs/etc/skel/.config/waybar/style.css" "#cba6f7" "Staged airootfs includes Waybar style.css"

if grep -Rqs -i "#00a8ff" "${REPO_ROOT}/build/archiso/airootfs/etc"; then
    fail "Legacy #00a8ff color found in staged build/archiso/airootfs/etc"
else
    pass "Zero legacy #00a8ff references in staged build/archiso/airootfs/etc"
fi

# Calamares checks
CAL_SETTINGS="${REPO_ROOT}/packages/installer/calamares/settings.conf"
CAL_BRANDING="${REPO_ROOT}/packages/installer/calamares/branding/synapseos/branding.desc"
CAL_PARTITION="${REPO_ROOT}/packages/installer/calamares/modules/partition.conf"
CAL_SERVICES="${REPO_ROOT}/packages/installer/calamares/modules/services-systemd.conf"
CAL_UNPACKFS="${REPO_ROOT}/packages/installer/calamares/modules/unpackfs.conf"

check_file_contains "${CAL_SETTINGS}" "branding:[[:space:]]*synapseos" "Calamares settings.conf uses synapseos branding"
check_file_contains "${CAL_SETTINGS}" "unpackfs" "Calamares settings.conf exec sequence includes unpackfs"
check_file_contains "${CAL_SETTINGS}" "services-systemd" "Calamares settings.conf exec sequence includes services-systemd"
check_file_contains "${CAL_BRANDING}" "componentName:[[:space:]]*synapseos" "Calamares branding.desc defines synapseos component"
check_file_contains "${CAL_BRANDING}" "#11111b" "Calamares branding.desc includes Obsidian Crust (#11111b)"
check_file_contains "${CAL_BRANDING}" "#cdd6f4" "Calamares branding.desc includes Liquid Silver Chrome (#cdd6f4)"
check_file_contains "${CAL_BRANDING}" "#cba6f7" "Calamares branding.desc includes Catppuccin Mauve (#cba6f7)"
check_file_contains "${CAL_PARTITION}" 'defaultFileSystemType:[[:space:]]*"btrfs"' "Calamares partition.conf defaults to Btrfs"
check_file_contains "${CAL_PARTITION}" "/@snapshots" "Calamares partition.conf defines @snapshots subvolume"
check_file_contains "${CAL_SERVICES}" "synapse" "Calamares services-systemd.conf enables synapse service"
check_file_contains "${CAL_SERVICES}" "sddm" "Calamares services-systemd.conf enables sddm service"
check_file_contains "${CAL_SERVICES}" "firewalld" "Calamares services-systemd.conf enables firewalld service"
check_file_contains "${CAL_UNPACKFS}" "/run/archiso/bootmnt/synapseos/x86_64/airootfs\.sfs" "Calamares unpackfs.conf targets /run/archiso/bootmnt/synapseos/x86_64/airootfs.sfs"
check_file_contains "${CAL_UNPACKFS}" 'sourcefs:[[:space:]]*"squashfs"' "Calamares unpackfs.conf specifies squashfs sourcefs"

# Package trust & live-session credential isolation
check_file_lacks "${REPO_ROOT}/build/archiso/pacman.conf" '\[cachyos[^]]*\]\nSigLevel = Optional TrustAll' "Archiso pacman.conf verifies CachyOS package signatures"
check_file_lacks "${REPO_ROOT}/overlay/etc/pacman.conf" '\[cachyos[^]]*\]\nSigLevel = Optional TrustAll' "Installed pacman.conf verifies CachyOS package signatures"
check_file_contains "${REPO_ROOT}/build/archiso/packages.x86_64" '^cachyos-keyring$' "Live ISO ships cachyos-keyring"
check_file_lacks "${REPO_ROOT}/build/archiso/airootfs/root/customize_airootfs.sh" '(?m)^[[:space:]]*pacman-key --init' "No pacman master key baked into the ISO at build time"
check_file_contains "${REPO_ROOT}/build/archiso/airootfs/root/customize_airootfs.sh" 'systemctl enable pacman-init\.service' "Live session generates its pacman keyring per boot"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/settings.conf" 'shellprocess@cleanup' "Calamares runs live-session cleanup"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/shellprocess@cleanup.conf" '00-synapse-live' "Calamares cleanup removes live NOPASSWD sudoers"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/shellprocess@cleanup.conf" 'userdel -r synapse' "Calamares cleanup removes passwordless live user"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/users.conf" '^sudoersGroup: wheel' "Installed users get password-protected wheel sudo"
check_file_contains "${REPO_ROOT}/build/build-iso.sh" 'mkarchiso -v -C' "ISO build uses isolated build pacman.conf/keyring"

# Package file-ownership conflicts (pacstrap aborts on these)
if grep -RqsiE "ps2|playstation|Xsetup-synapseos" "${REPO_ROOT}/overlay" "${REPO_ROOT}/build/archiso/packages.x86_64" "${REPO_ROOT}/build/build-iso.sh"; then
    fail "No PS2 boot/greeter remnants in overlay, package list or build script"
else
    pass "No PS2 boot/greeter remnants in overlay, package list or build script"
fi
check_file_lacks "${REPO_ROOT}/build/build-iso.sh" 'AIROOTFS_DIR\}/etc/calamares/' "Calamares config not staged over cachyos-calamares files"

# Live boot & installed-system bootability
check_file_contains "${REPO_ROOT}/build/archiso/airootfs/etc/mkinitcpio.conf.d/archiso.conf" '^HOOKS=\(.* archiso .*\)$' "Live initramfs includes archiso hooks"
check_file_lacks "${REPO_ROOT}/build/archiso/efiboot/loader/entries/01-synapseos-x86_64-linux.conf" '(intel|amd)-ucode\.img' "systemd-boot entry has no external microcode (microcode hook embeds it)"
check_file_lacks "${REPO_ROOT}/build/archiso/syslinux/syslinux.cfg" '(intel|amd)-ucode\.img' "syslinux entries have no external microcode"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/shellprocess@cleanup.conf" 'install -Dm644 .*/vmlinuz' "Calamares restores kernels emptied from /boot by mkarchiso"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/shellprocess@cleanup.conf" 'rm -f /etc/mkinitcpio.conf.d/archiso.conf' "Calamares drops live archiso initramfs hooks"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/settings.conf" '^      - initcpio$' "Calamares rebuilds the installed initramfs"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/bootloader.conf" '^efiBootLoader: "grub"$' "Calamares installs GRUB (not cachyos-calamares limine default)"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/mount.conf" 'subvolume: /@snapshots' "Calamares mount.conf defines @snapshots subvolume"
if grep -Rqs "geoip" "${REPO_ROOT}/packages/installer/calamares"; then
    fail "Calamares configs perform no GeoIP lookup"
else
    pass "Calamares configs perform no GeoIP lookup"
fi
for module in welcome locale; do
    check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/${module}.conf" '^---$' "Calamares ${module}.conf overrides cachyos-calamares default (GeoIP)"
done
if python3 -c 'import yaml' 2>/dev/null; then
    for yml in "${REPO_ROOT}"/packages/installer/calamares/modules/*.conf "${REPO_ROOT}/packages/installer/calamares/settings.conf"; do
        if python3 -c 'import sys, yaml; yaml.safe_load(open(sys.argv[1]))' "${yml}" 2>/dev/null; then
            pass "Valid YAML: ${yml#"${REPO_ROOT}/"}"
        else
            fail "Valid YAML: ${yml#"${REPO_ROOT}/"}"
        fi
    done
else
    warn "python3-yaml unavailable; skipping Calamares YAML validation"
fi
if [[ "$(readlink "${REPO_ROOT}/build/archiso/airootfs/etc/resolv.conf" 2>/dev/null)" == "/run/systemd/resolve/stub-resolv.conf" ]]; then
    pass "Live resolv.conf links to the systemd-resolved stub (Quad9 DoT)"
else
    fail "Live resolv.conf links to the systemd-resolved stub (Quad9 DoT)"
fi
check_file_lacks "${REPO_ROOT}/build/archiso/airootfs/etc/mkinitcpio.conf.d/archiso.conf" 'archiso_pxe' "Live initramfs has no PXE hooks (nbd/nfs helpers not shipped)"
check_file_lacks "${REPO_ROOT}/build/archiso/airootfs/root/customize_airootfs.sh" '(?m)^ln .*/etc/resolv\.conf' "customize_airootfs.sh does not replace chroot-bind-mounted resolv.conf"
check_file_lacks "${REPO_ROOT}/packages/core/synapse-core/synapse.service" 'ExecStart=.*--config' "synapse.service passes only flags 'synapse serve' accepts"
check_file_lacks "${REPO_ROOT}/packages/core/synapse-core/synapse.service" 'network-online\.target' "synapse.service does not wait on network-online (localhost gateway)"
check_file_contains "${REPO_ROOT}/build/archiso/airootfs/root/customize_airootfs.sh" 'systemctl disable systemd-networkd\.service' "systemd-networkd disabled (NetworkManager owns networking)"

# Boot splash (Plymouth, Twin Hook)
PLY_DIR="${REPO_ROOT}/packages/desktop/synapse-plymouth"
check_file_contains "${REPO_ROOT}/build/archiso/airootfs/etc/mkinitcpio.conf.d/archiso.conf" '^HOOKS=\(.* kms plymouth .*\)$' "Live initramfs runs the plymouth hook"
check_file_contains "${REPO_ROOT}/overlay/etc/plymouth/plymouthd.conf" '^Theme=synapseos-mauve$' "Plymouth defaults to synapseos-mauve"
check_file_contains "${REPO_ROOT}/build/archiso/efiboot/loader/entries/01-synapseos-x86_64-linux.conf" '^options .* splash' "Live boot entry passes splash"
check_file_contains "${REPO_ROOT}/packages/installer/calamares/modules/bootloader.conf" '"splash"' "Installed systems boot with splash"
check_file_contains "${PLY_DIR}/synapseos.script.in" 'Plymouth\.SetDisplayPasswordFunction' "Splash handles the LUKS passphrase prompt"
check_file_contains "${PLY_DIR}/synapseos.script.in" 'Plymouth\.SetRefreshFunction' "Splash script drives frame playback"
check_file_contains "${REPO_ROOT}/packages/desktop/synapse-themes/synapse-theme" 'plymouth-set-default-theme -R' "synapse-theme can sync the boot splash accent"
for accent in mauve tungsten crimson sapphire emerald; do
    check_file_contains "${PLY_DIR}/PKGBUILD" "'${accent}:[0-9a-f]{6}:" "Boot splash renders the ${accent} accent"
done
if python3 -m py_compile "${PLY_DIR}/render_frames.py" 2>/dev/null; then
    pass "render_frames.py compiles"
else
    fail "render_frames.py compiles"
fi

# V4 theme pack & screensaver
THEMES_DIR="${REPO_ROOT}/packages/desktop/synapse-themes"
for wp in synapse-monolith-{mauve,tungsten,sapphire,emerald} synapse-tower-{mauve,tungsten,crimson,sapphire,emerald} synapse-carbon-{crimson,mauve,tungsten,sapphire,emerald}; do
    check_file_contains "${THEMES_DIR}/PKGBUILD" "^  .${wp}\\.jpg.$" "synapse-themes ships ${wp}.jpg"
done
check_file_contains "${THEMES_DIR}/synapse-theme" '^DEFAULT_THEME="monolith-mauve"$' "Default system theme is monolith-mauve"
check_file_contains "${THEMES_DIR}/synapse-theme" 'pkexec tee .*GREETER_CONF' "synapse-theme can sync the login screen variant (pkexec)"
check_file_contains "${THEMES_DIR}/synapse-theme" '<Primary><Super>t' "XFCE Super+Ctrl+T opens the theme menu"
check_file_contains "${REPO_ROOT}/overlay/etc/skel/.config/sway/config" 'Ctrl\+t exec synapse-theme --menu' "Sway Super+Ctrl+T opens the theme menu"
check_file_contains "${REPO_ROOT}/overlay/etc/skel/.config/sway/config" "synapse-screensaver --launch" "Sway idle launches the torus screensaver"
if (cd "${THEMES_DIR}" && makepkg -f --verifysource --skippgpcheck >/dev/null 2>&1); then
    pass "synapse-themes sha256sums match sources"
else
    fail "synapse-themes sha256sums match sources (run updpkgsums in ${THEMES_DIR#"${REPO_ROOT}/"})"
fi

# GitHub Actions workflow check
GH_WORKFLOW="${REPO_ROOT}/.github/workflows/build-iso.yml"
check_file_contains "${GH_WORKFLOW}" "verify-gates\.sh" "GitHub workflow runs verify-gates.sh"
check_file_contains "${GH_WORKFLOW}" "SHA256SUMS" "GitHub workflow generates SHA256SUMS"

echo ""
echo "=============================================================================="
echo " Verification Summary: ${PASS_COUNT} passed, ${WARN_COUNT} warnings, ${FAIL_COUNT} failed"
echo "=============================================================================="

if [[ "${FAIL_COUNT}" -gt 0 ]]; then
    exit 1
fi
exit 0
