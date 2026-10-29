"""SynapseOS Gate G3 & G4 Validation Suite for PS2 Startup, Calamares & Archiso Profile."""

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

    def test_ps2_theme_and_ui_handoff(self) -> None:
        """Validate PS2 theme PKGBUILD, SDDM Main.qml, and Picom configuration."""
        ps2_pkg = REPO_ROOT / "packages" / "desktop" / "synapse-theme-ps2" / "PKGBUILD"
        if ps2_pkg.is_file():
            text = ps2_pkg.read_text(encoding="utf-8")
            self.assertIn("ps2-xfce", text)
            self.assertIn("ps2-system-boot", text)

        sddm_qml = (
            REPO_ROOT
            / "packages"
            / "desktop"
            / "synapse-theme-ps2"
            / "src"
            / "synapse-cli"
            / "ps2-startup"
            / "sddm-theme"
            / "Main.qml"
        )
        if sddm_qml.is_file():
            qml_text = sddm_qml.read_text(encoding="utf-8")
            self.assertNotIn("password.text.length === 0", qml_text)
            for legacy_blue in ("#5fb4ff", "#2b6cc0", "#174a8c", "#7cc2ff"):
                self.assertNotIn(legacy_blue, qml_text.lower())
            for palette_col in ("#cba6f7", "#1e1e2e", "#11111b", "#cdd6f4"):
                self.assertIn(palette_col, qml_text.lower())
            self.assertIn("sway.desktop", qml_text)
            self.assertIn("xfce.desktop", qml_text)
            self.assertIn("toggleSession", qml_text)

        picom_conf = REPO_ROOT / "overlay" / "etc" / "xdg" / "picom.conf"
        if picom_conf.is_file():
            picom_text = picom_conf.read_text(encoding="utf-8")
            self.assertIn("dual_kawase", picom_text)
            self.assertIn("corner-radius", picom_text)

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
