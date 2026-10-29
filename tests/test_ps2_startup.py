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
        self.assertIn("#00a8ff", branding.lower())
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

    def test_ps2_theme_and_ui_handoff(self) -> None:
        """Validate PS2 theme PKGBUILD and Picom configuration when present."""
        ps2_pkg = REPO_ROOT / "packages" / "desktop" / "synapse-theme-ps2" / "PKGBUILD"
        if ps2_pkg.is_file():
            text = ps2_pkg.read_text(encoding="utf-8")
            self.assertIn("ps2-xfce", text)
            self.assertIn("ps2-system-boot", text)

        picom_conf = REPO_ROOT / "overlay" / "etc" / "xdg" / "picom.conf"
        if picom_conf.is_file():
            picom_text = picom_conf.read_text(encoding="utf-8")
            self.assertIn("dual_kawase", picom_text)
            self.assertIn("corner-radius", picom_text)


if __name__ == "__main__":
    unittest.main()
