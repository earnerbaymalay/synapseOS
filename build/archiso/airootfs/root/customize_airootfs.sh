#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Archiso Post-Install RootFS Customization Hook
# Executed inside the chroot during mkarchiso image generation.
# ==============================================================================
set -euo pipefail

echo "[SynapseOS] Configuring locale, timezone, and hostname..."
sed -i 's/#\(en_US\.UTF-8\)/\1/' /etc/locale.gen
locale-gen
ln -sf /usr/share/zoneinfo/UTC /etc/localtime
echo "synapseos" > /etc/hostname

# Merge staged /overlay/etc if present inside airootfs
if [[ -d /overlay/etc ]]; then
    echo "[SynapseOS] Merging /overlay/etc into root filesystem..."
    cp -af /overlay/etc/. /etc/
    rm -rf /overlay
fi

# Apply SynapseOS Calamares config over the cachyos-calamares defaults
if [[ -d /etc/synapseos/calamares ]]; then
    echo "[SynapseOS] Installing Calamares configuration..."
    cp -af /etc/synapseos/calamares/. /etc/calamares/
    rm -rf /etc/synapseos/calamares
fi

# Create live user 'synapse' with passwordless sudo for live environment
# (live-only: Calamares shellprocess@cleanup deletes both on install)
if ! id -u synapse >/dev/null 2>&1; then
    echo "[SynapseOS] Creating live user 'synapse'..."
    useradd -m -G wheel,video,audio,input,network,storage,wireshark -s /bin/bash synapse
    passwd -d synapse
fi

install -d -m 0750 /etc/sudoers.d
cat << 'EOF' > /etc/sudoers.d/00-synapse-live
%wheel ALL=(ALL:ALL) NOPASSWD: ALL
EOF
chmod 0440 /etc/sudoers.d/00-synapse-live

# Ensure /etc/skel is synced into /home/synapse
if [[ -d /etc/skel ]]; then
    cp -af /etc/skel/. /home/synapse/
    chown -R synapse:synapse /home/synapse
fi

# Set default systemd target to graphical
echo "[SynapseOS] Setting default target to graphical.target..."
systemctl set-default graphical.target

# Enable core system, security, performance, and AI services
SERVICES=(
    "sddm.service"
    "NetworkManager.service"
    "systemd-resolved.service"
    "firewalld.service"
    "ananicy-cpp.service"
    "ollama.service"
    "synapse.service"
)

for svc in "${SERVICES[@]}"; do
    echo "[SynapseOS] Enabling service: ${svc}"
    systemctl enable "${svc}" 2>/dev/null || ln -sf "/usr/lib/systemd/system/${svc}" "/etc/systemd/system/multi-user.target.wants/${svc}" || true
done

# NetworkManager owns networking. systemd presets also enable systemd-networkd, whose
# wait-online unit times out (~2 min) and stalls network-online.target consumers.
systemctl disable systemd-networkd.service systemd-networkd.socket systemd-networkd-wait-online.service 2>/dev/null || true

# Ensure SDDM display-manager symlink is established
ln -sf /usr/lib/systemd/system/sddm.service /etc/systemd/system/display-manager.service

# /etc/resolv.conf -> systemd-resolved stub (Quad9 DoT) ships as a symlink in the profile
# airootfs: inside arch-chroot it is bind-mounted from the build host and can't be replaced.

# Pacman Keyring: generated per boot on a tmpfs, never at build time, so no two
# SynapseOS machines share a pacman master signing key. `--populate` picks up the
# CachyOS key (F3B607488DB35A47) from the cachyos-keyring package; no keyserver fetch.
# Calamares (shellprocess@cleanup) removes these units and builds a fresh keyring on install.
echo "[SynapseOS] Installing per-boot pacman keyring units..."
rm -rf /etc/pacman.d/gnupg
cat << 'EOF' > /etc/systemd/system/etc-pacman.d-gnupg.mount
[Unit]
Description=Temporary /etc/pacman.d/gnupg directory

[Mount]
What=tmpfs
Where=/etc/pacman.d/gnupg
Type=tmpfs
Options=mode=0755,noswap
EOF
cat << 'EOF' > /etc/systemd/system/pacman-init.service
[Unit]
Description=Initializes Pacman keyring
Requires=etc-pacman.d-gnupg.mount
After=etc-pacman.d-gnupg.mount time-sync.target
BindsTo=etc-pacman.d-gnupg.mount

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/pacman-key --init
ExecStart=/usr/bin/pacman-key --populate

[Install]
WantedBy=multi-user.target
EOF
systemctl enable pacman-init.service

echo "[SynapseOS] customize_airootfs.sh completed successfully."
