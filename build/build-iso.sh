#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Live ISO Builder (build/build-iso.sh)
# Synchronizes overlays, optionally builds local PKGBUILDs, and invokes mkarchiso.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROFILE_DIR="${SCRIPT_DIR}/archiso"
AIROOTFS_DIR="${PROFILE_DIR}/airootfs"
OVERLAY_DIR="${REPO_ROOT}/overlay"
CALAMARES_SRC="${REPO_ROOT}/packages/installer/calamares"
WORK_DIR="${WORK_DIR:-/tmp/synapseos-archiso-work}"
OUT_DIR="${OUT_DIR:-${REPO_ROOT}/out}"
LOCAL_REPO_DIR="${LOCAL_REPO_DIR:-${OUT_DIR}/repo}"
SYSTEM_REPO_DIR="/var/cache/synapseos-repo"

DRY_RUN=0
BUILD_PKGS=0

usage() {
    cat << 'EOF'
Usage: ./build/build-iso.sh [OPTIONS]

Options:
  --dry-run, --check   Validate profile, stage overlays, and verify readiness without root/mkarchiso
  --build-pkgs         Build native PKGBUILDs under packages/ and populate local [synapseos] repo
  -w, --work-dir DIR   Set archiso working directory (default: /tmp/synapseos-archiso-work)
  -o, --out-dir DIR    Set ISO output directory (default: ./out)
  -h, --help           Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run|--check)
            DRY_RUN=1
            shift
            ;;
        --build-pkgs)
            BUILD_PKGS=1
            shift
            ;;
        -w|--work-dir)
            WORK_DIR="$2"
            shift 2
            ;;
        -o|--out-dir)
            OUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

echo "==> [SynapseOS ISO Builder] Initializing build pipeline..."
echo "    Repository Root : ${REPO_ROOT}"
echo "    Archiso Profile : ${PROFILE_DIR}"
echo "    Output Directory: ${OUT_DIR}"

# 1. Verify core Archiso profile files exist
REQUIRED_PROFILE_FILES=(
    "${PROFILE_DIR}/profiledef.sh"
    "${PROFILE_DIR}/packages.x86_64"
    "${PROFILE_DIR}/pacman.conf"
    "${PROFILE_DIR}/efiboot/loader/loader.conf"
    "${PROFILE_DIR}/efiboot/loader/entries/01-synapseos-x86_64-linux.conf"
    "${PROFILE_DIR}/syslinux/syslinux.cfg"
    "${AIROOTFS_DIR}/root/customize_airootfs.sh"
)

for req in "${REQUIRED_PROFILE_FILES[@]}"; do
    if [[ ! -f "${req}" ]]; then
        echo "[ERROR] Missing required archiso file: ${req}" >&2
        exit 1
    fi
done

# 2. Synchronize overlay/ into build/archiso/airootfs/etc
mkdir -p "${AIROOTFS_DIR}/etc"

if [[ -d "${OVERLAY_DIR}/etc" ]]; then
    echo "==> Syncing ${OVERLAY_DIR}/etc -> ${AIROOTFS_DIR}/etc ..."
    cp -af "${OVERLAY_DIR}/etc/." "${AIROOTFS_DIR}/etc/"
elif [[ -d "${OVERLAY_DIR}" ]]; then
    echo "==> Syncing ${OVERLAY_DIR} -> ${AIROOTFS_DIR}/etc ..."
    cp -af "${OVERLAY_DIR}/." "${AIROOTFS_DIR}/etc/"
else
    echo "==> [WARN] No overlay/ directory found yet; continuing with base airootfs."
fi

if [[ -d "${OVERLAY_DIR}/skel" ]]; then
    echo "==> Syncing ${OVERLAY_DIR}/skel -> ${AIROOTFS_DIR}/etc/skel ..."
    mkdir -p "${AIROOTFS_DIR}/etc/skel"
    cp -af "${OVERLAY_DIR}/skel/." "${AIROOTFS_DIR}/etc/skel/"
fi

# 3. Stage Calamares installer configurations into airootfs
if [[ -d "${CALAMARES_SRC}" ]]; then
    echo "==> Staging Calamares configuration into ${AIROOTFS_DIR}/etc/calamares ..."
    mkdir -p "${AIROOTFS_DIR}/etc/calamares"
    cp -af "${CALAMARES_SRC}/." "${AIROOTFS_DIR}/etc/calamares/"
fi

# 4. Optionally build local SynapseOS PKGBUILDs
build_local_packages() {
    echo "==> Building local SynapseOS native packages into ${LOCAL_REPO_DIR}..."
    mkdir -p "${LOCAL_REPO_DIR}"

    # Pre-seed local sources when available on workstation to avoid redundant network clones
    if [[ -d "/home/ebaymlay/work/synapse" ]]; then
        local sc_dir="${REPO_ROOT}/packages/core/synapse-core"
        mkdir -p "${sc_dir}/src"
        rm -rf "${sc_dir}/src/synapse"
        cp -al "/home/ebaymlay/work/synapse" "${sc_dir}/src/synapse"
        cp -f "${sc_dir}/synapse.service" "${sc_dir}/synapse-sync.service" "${sc_dir}/synapse-sync.timer" "${sc_dir}/src/"
    fi

    if [[ -d "${REPO_ROOT}/../llm-quickfire-panel" ]]; then
        local qf_dir="${REPO_ROOT}/packages/desktop/llm-quickfire-panel"
        mkdir -p "${qf_dir}/src"
        rm -rf "${qf_dir}/src/llm-quickfire-panel"
        cp -af "${REPO_ROOT}/../llm-quickfire-panel" "${qf_dir}/src/llm-quickfire-panel"
    fi

    if [[ -d "${REPO_ROOT}/../ps2-startup" ]]; then
        local ps2_dir="${REPO_ROOT}/packages/desktop/synapse-theme-ps2"
        mkdir -p "${ps2_dir}/src/synapse-cli"
        rm -rf "${ps2_dir}/src/synapse-cli/ps2-startup"
        cp -af "${REPO_ROOT}/../ps2-startup" "${ps2_dir}/src/synapse-cli/ps2-startup"
    fi

    local pkg_dirs=(
        "${REPO_ROOT}/packages/core/synapse-core"
        "${REPO_ROOT}/packages/desktop/llm-quickfire-panel"
        "${REPO_ROOT}/packages/desktop/synapse-theme-ps2"
    )

    for pkg_dir in "${pkg_dirs[@]}"; do
        if [[ -f "${pkg_dir}/PKGBUILD" ]]; then
            echo "    -> Building PKGBUILD in ${pkg_dir}..."
            (
                cd "${pkg_dir}"
                local makepkg_flags=("-sf" "--noconfirm")
                if [[ -d "${pkg_dir}/src" ]] && [[ -n "$(ls -A "${pkg_dir}/src" 2>/dev/null)" ]]; then
                    makepkg_flags=("-ef" "--noconfirm" "--nodeps")
                fi
                if [[ "${EUID}" -eq 0 ]]; then
                    chown -R nobody:nobody "${pkg_dir}"
                    sudo -u nobody makepkg "${makepkg_flags[@]}"
                else
                    makepkg "${makepkg_flags[@]}"
                fi
                cp -f ./*.pkg.tar.* "${LOCAL_REPO_DIR}/"
            )
        else
            echo "    -> [SKIP] ${pkg_dir}/PKGBUILD not present."
        fi
    done

    if compgen -G "${LOCAL_REPO_DIR}/*.pkg.tar.*" > /dev/null; then
        repo-add -R "${LOCAL_REPO_DIR}/synapseos.db.tar.gz" "${LOCAL_REPO_DIR}"/*.pkg.tar.*
    fi

    # Stage local repository into airootfs so live/installed environment has cached packages
    mkdir -p "${AIROOTFS_DIR}${SYSTEM_REPO_DIR}"
    cp -af "${LOCAL_REPO_DIR}/." "${AIROOTFS_DIR}${SYSTEM_REPO_DIR}/"
}

if [[ "${BUILD_PKGS}" -eq 1 ]]; then
    build_local_packages
fi

# 5. Dry-run check mode (non-root safe)
if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo "==> [DRY-RUN] Validating profiledef.sh and customize_airootfs.sh syntax..."
    bash -n "${PROFILE_DIR}/profiledef.sh"
    bash -n "${AIROOTFS_DIR}/root/customize_airootfs.sh"
    echo "==> [DRY-RUN] Archiso profile, CachyOS mirrorlists & RootFS overlay staged and validated."
    echo "    Would execute: mkarchiso -v -w \"${WORK_DIR}\" -o \"${OUT_DIR}\" \"${PROFILE_DIR}\""
    exit 0
fi

# 6. Prepare host CachyOS mirrorlists & [synapseos] repo for mkarchiso
prepare_host_build_env() {
    local priv_cmd=()
    if [[ "${EUID}" -ne 0 ]]; then
        priv_cmd=(sudo)
    fi

    if [[ -d "${OVERLAY_DIR}/etc/pacman.d" ]]; then
        echo "==> Installing CachyOS mirrorlists to host /etc/pacman.d/ for mkarchiso..."
        "${priv_cmd[@]}" mkdir -p /etc/pacman.d
        "${priv_cmd[@]}" cp -af "${OVERLAY_DIR}/etc/pacman.d/." /etc/pacman.d/
    fi

    if [[ -d "${LOCAL_REPO_DIR}" ]]; then
        echo "==> Syncing local [synapseos] repository to ${SYSTEM_REPO_DIR}..."
        "${priv_cmd[@]}" mkdir -p "${SYSTEM_REPO_DIR}"
        "${priv_cmd[@]}" cp -af "${LOCAL_REPO_DIR}/." "${SYSTEM_REPO_DIR}/"
    fi
}

# 7. Execute mkarchiso (requires root privileges)
if ! command -v mkarchiso >/dev/null 2>&1; then
    echo "[ERROR] mkarchiso not found. Install 'archiso' (sudo pacman -S archiso)." >&2
    exit 1
fi

prepare_host_build_env
mkdir -p "${OUT_DIR}"

if [[ "${EUID}" -ne 0 ]]; then
    echo "==> Elevating privileges via sudo to run mkarchiso..."
    sudo mkarchiso -v -w "${WORK_DIR}" -o "${OUT_DIR}" "${PROFILE_DIR}"
else
    mkarchiso -v -w "${WORK_DIR}" -o "${OUT_DIR}" "${PROFILE_DIR}"
fi

echo "==> [SynapseOS ISO Builder] ISO generation complete. Artifacts in ${OUT_DIR}:"
ls -lh "${OUT_DIR}"
