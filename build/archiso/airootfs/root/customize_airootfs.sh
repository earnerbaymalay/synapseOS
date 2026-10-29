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

# Create live user 'synapse' with passwordless sudo for live environment
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

# Ensure SDDM display-manager symlink is established
ln -sf /usr/lib/systemd/system/sddm.service /etc/systemd/system/display-manager.service

# Link systemd-resolved stub resolv.conf for Quad9 DoT
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# Initialize Pacman Keyring & CachyOS Signing Key (F3B607488DB35A47)
if command -v pacman-key >/dev/null 2>&1; then
    echo "[SynapseOS] Initializing pacman keyring and CachyOS repository key..."
    pacman-key --init || true
    pacman-key --populate archlinux || true
    pacman-key --recv-keys F3B607488DB35A47 --keyserver keyserver.ubuntu.com 2>/dev/null || true
    pacman-key --lsign-key F3B607488DB35A47 2>/dev/null || true
fi

echo "[SynapseOS] customize_airootfs.sh completed successfully."
