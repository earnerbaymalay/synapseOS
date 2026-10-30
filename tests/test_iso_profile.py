"""SynapseOS Gate G3 & G4 Validation Suite for the greeter, Calamares installer and Archiso profile."""

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSynapseOSGates(unittest.TestCase):
    """Zero-dependency validation tests compatible with both pytest and unittest."""

    def test_archiso_profile_exists(self) -> None:
        """Verify core Archiso files are present and configured for x86_64 + zstd."""
        profiledef = REPO_ROOT / "build" / "archiso" / "profiledef.sh"
        self.assertTrue(profiledef.is_file(), "build/archiso/profiledef.sh must exist")
        content = profiledef.read_text(encoding="utf-8")
        self.assertIn('iso_name="synapseos"', content)
        self.assertIn('arch="x86_64"', content)
        self.assertIn("zstd", content)

    def test_calamares_configuration_integrity(self) -> None:
        """Verify Calamares settings, branding, partition, and services configurations."""
        cal_root = REPO_ROOT / "packages" / "installer" / "calamares"
        settings = (cal_root / "settings.conf").read_text(encoding="utf-8")
        self.assertIn("branding: synapseos", settings)
        self.assertIn("unpackfs", settings)
        self.assertIn("services-systemd", settings)

        branding = (cal_root / "branding" / "synapseos" / "branding.desc").read_text(
            encoding="utf-8"
        )
        self.assertIn("componentName:   synapseos", branding)
        self.assertNotIn("#00a8ff", branding.lower())
        self.assertIn("#11111b", branding.lower())
        self.assertIn("#cdd6f4", branding.lower())
        self.assertIn("#cba6f7", branding.lower())

        partition = (cal_root / "modules" / "partition.conf").read_text(encoding="utf-8")
        self.assertIn('defaultFileSystemType:  "btrfs"', partition)
        for subvol in ("/@", "/@home", "/@snapshots", "/@var_log"):
            self.assertIn(subvol, partition)

        services = (cal_root / "modules" / "services-systemd.conf").read_text(
            encoding="utf-8"
        )
        for svc in (
            "sddm",
            "NetworkManager",
            "firewalld",
            "ananicy-cpp",
            "ollama",
            "synapse",
        ):
            self.assertIn(f'"{svc}"', services)

        unpackfs = (cal_root / "modules" / "unpackfs.conf").read_text(encoding="utf-8")
        self.assertIn("/run/archiso/bootmnt/synapseos/x86_64/airootfs.sfs", unpackfs)
        self.assertIn('sourcefs: "squashfs"', unpackfs)

    def test_greeter_and_compositor(self) -> None:
        """Validate the synapseos SDDM greeter, its SDDM config, and Picom configuration."""
        greeter = REPO_ROOT / "packages" / "desktop" / "synapse-greeter"
        qml = (greeter / "Main.qml").read_text(encoding="utf-8")
        self.assertIn("sddm.login(", qml)
        self.assertIn("model: sessionModel", qml)
        self.assertIn("#cba6f7", qml.lower())
        self.assertIn("variant=monolith-mauve", (greeter / "theme.conf").read_text(encoding="utf-8"))

        sddm_conf = (REPO_ROOT / "overlay" / "etc" / "sddm.conf.d" / "10-synapseos.conf").read_text(
            encoding="utf-8"
        )
        self.assertIn("Current=synapseos", sddm_conf)
        self.assertNotIn("Xsetup-synapseos", sddm_conf)

        picom_text = (REPO_ROOT / "overlay" / "etc" / "xdg" / "picom.conf").read_text(encoding="utf-8")
        self.assertIn("dual_kawase", picom_text)
        self.assertIn("corner-radius", picom_text)
        self.assertNotIn("PS2", picom_text)

    def test_boot_splash(self) -> None:
        """Validate the Plymouth Twin Hook splash package and its boot wiring."""
        ply = REPO_ROOT / "packages" / "desktop" / "synapse-plymouth"
        script = (ply / "synapseos.script.in").read_text(encoding="utf-8")
        for hook in ("SetRefreshFunction", "SetDisplayPasswordFunction", "SetDisplayNormalFunction", "SetQuitFunction"):
            self.assertIn(f"Plymouth.{hook}", script)
        pkgbuild = (ply / "PKGBUILD").read_text(encoding="utf-8")
        for accent in ("mauve", "tungsten", "crimson", "sapphire", "emerald"):
            self.assertIn(f"'{accent}:", pkgbuild)
        hooks = (REPO_ROOT / "build" / "archiso" / "airootfs" / "etc" / "mkinitcpio.conf.d" / "archiso.conf").read_text(
            encoding="utf-8"
        )
        self.assertIn(" kms plymouth ", hooks)
        conf = (REPO_ROOT / "overlay" / "etc" / "plymouth" / "plymouthd.conf").read_text(encoding="utf-8")
        self.assertIn("Theme=synapseos-mauve", conf)

    def test_sway_and_waybar_session_configs(self) -> None:
        """Validate Sway and Waybar dual-session configs and package list."""
        pkgs_text = (REPO_ROOT / "build" / "archiso" / "packages.x86_64").read_text(
            encoding="utf-8"
        )
        pkg_lines = {line.strip() for line in pkgs_text.splitlines()}
        self.assertNotIn("nohang", pkg_lines)
        self.assertNotIn("tshark", pkg_lines)
        self.assertIn("wireshark-cli", pkg_lines)
        for pkg in (
            "sway",
            "waybar",
            "foot",
            "xorg-xwayland",
            "wl-clipboard",
            "grim",
            "slurp",
            "swayidle",
        ):
            self.assertIn(pkg, pkg_lines)

        sway_conf = (
            REPO_ROOT / "overlay" / "etc" / "skel" / ".config" / "sway" / "config"
        ).read_text(encoding="utf-8")
        self.assertNotIn("#00a8ff", sway_conf.lower())
        for color in ("#11111b", "#1e1e2e", "#cba6f7", "#cdd6f4"):
            self.assertIn(color, sway_conf.lower())
        self.assertIn("/usr/bin/quickfire", sway_conf)
        self.assertIn("Mod4+space", sway_conf)
        self.assertIn("Mod4+d", sway_conf)
        self.assertIn("Mod4+Return", sway_conf)

        waybar_conf = (
            REPO_ROOT / "overlay" / "etc" / "skel" / ".config" / "waybar" / "config.jsonc"
        ).read_text(encoding="utf-8")
        self.assertNotIn("#00a8ff", waybar_conf.lower())
        self.assertIn("sway/workspaces", waybar_conf)
        self.assertIn("/usr/bin/quickfire", waybar_conf)

        waybar_style = (
            REPO_ROOT / "overlay" / "etc" / "skel" / ".config" / "waybar" / "style.css"
        ).read_text(encoding="utf-8")
        self.assertNotIn("#00a8ff", waybar_style.lower())
        for color in ("#11111b", "#1e1e2e", "#cba6f7", "#cdd6f4"):
            self.assertIn(color, waybar_style.lower())


if __name__ == "__main__":
    unittest.main()
