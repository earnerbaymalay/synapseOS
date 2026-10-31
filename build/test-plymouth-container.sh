#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Visible Plymouth Test Container Runner
# ==============================================================================
# Spawns a visible systemd-nspawn container targeting the SynapseOS airootfs,
# bridges the host X11 display, and renders the native Plymouth boot splash.
# ==============================================================================

set -euo pipefail

ROOTFS="${ROOTFS:-/var/tmp/synapseos-archiso-work/x86_64/airootfs}"
THEME="${1:-synapseos-mauve}"
DISPLAY="${DISPLAY:-:0.0}"

if [[ ! -d "$ROOTFS" ]]; then
    echo "[!] Error: Rootfs not found at $ROOTFS"
    echo "    Run ./build/build-iso.sh to stage the airootfs first."
    exit 1
fi

echo "[+] Preparing X11 credentials for container..."
XAUTH_CONTAINER="/tmp/xauth_synapseos_container"
rm -f "$XAUTH_CONTAINER"
touch "$XAUTH_CONTAINER"
chmod 666 "$XAUTH_CONTAINER"

# Extract cookie from active display and register for localhost/airootfs
COOKIE=$(xauth list "$DISPLAY" 2>/dev/null | head -n 1 | awk '{print $3}')
if [[ -n "$COOKIE" ]]; then
    xauth -f "$XAUTH_CONTAINER" add :0 MIT-MAGIC-COOKIE-1 "$COOKIE"
    xauth -f "$XAUTH_CONTAINER" add airootfs/unix:0 MIT-MAGIC-COOKIE-1 "$COOKIE"
    xauth -f "$XAUTH_CONTAINER" add localhost:0 MIT-MAGIC-COOKIE-1 "$COOKIE"
fi

# Build MIT-SHM bypass shim if needed (prevents X11 BadAccess across UID boundaries)
SHIM_SO="/tmp/synapseos_noshm.so"
if [[ ! -f "$SHIM_SO" ]]; then
    echo "[+] Compiling X11 SHM compatibility shim..."
    cat << 'EOF' > /tmp/synapseos_noshm.c
int XShmQueryExtension(void *dpy) { return 0; }
int XShmAttach(void *dpy, void *shminfo) { return 0; }
EOF
    gcc -shared -fPIC -o "$SHIM_SO" /tmp/synapseos_noshm.c
    rm -f /tmp/synapseos_noshm.c
fi

# Runner payload executed inside container
RUNNER="/tmp/synapseos_plymouth_exec.sh"
cat << EOF > "$RUNNER"
#!/usr/bin/env bash
set -e
echo "[+] Starting Plymouth daemon (theme: $THEME)..."
plymouth-set-default-theme "$THEME" 2>/dev/null || true
plymouthd --debug --mode=boot --kernel-command-line="splash" --graphical-boot &
DAEMON_PID=\$!
sleep 0.8

echo "[+] Launching splash screen on active display..."
plymouth --show-splash

stages=(
  "0:Initializing Synapse Monolith Kernel..."
  "15:Hardening Quad9 DoT Resolvers & Randomizing MAC..."
  "30:Calibrating Twin-Hook Laser Optics..."
  "50:Dielectric Arc Convergence (Spark Gap Active)..."
  "70:Loading Resident Neural Models (Qwen2.5-Coder)..."
  "85:Spinning up Sway & XFCE Catppuccin Compositors..."
  "98:SynapseOS Ready."
)

for stage in "\${stages[@]}"; do
  msg="\${stage#*:}"
  plymouth --update="\$msg" || true
  sleep 1.0
done

sleep 1.5
echo "[+] Concluding splash sequence..."
plymouth --quit || true
wait \$DAEMON_PID 2>/dev/null || true
echo "[✓] Container splash execution completed."
EOF
chmod +x "$RUNNER"

echo "[+] Spawning visible Plymouth test container..."
sudo systemd-nspawn -D "$ROOTFS" \
    --setenv=DISPLAY="$DISPLAY" \
    --setenv=XAUTHORITY="$XAUTH_CONTAINER" \
    --setenv=LD_PRELOAD="$SHIM_SO" \
    --bind=/tmp/.X11-unix \
    --bind="$XAUTH_CONTAINER" \
    --bind="$SHIM_SO" \
    --bind="$RUNNER" \
    "$RUNNER"

echo "[✓] Test container session finished."
