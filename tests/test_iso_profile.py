"""SynapseOS Gate G3 & G4 Validation Suite for the greeter, Calamares installer and Archiso profile."""

import os
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

        branding_dir = cal_root / "branding" / "synapseos"
        branding = (branding_dir / "branding.desc").read_text(
            encoding="utf-8"
        )
        self.assertIn("componentName:   synapseos", branding)
        self.assertNotIn("#00a8ff", branding.lower())
        self.assertIn("#11111b", branding.lower())
        self.assertIn("#cdd6f4", branding.lower())
        self.assertIn("#cba6f7", branding.lower())

        # Validate that all branding assets referenced in branding.desc exist and are populated
        for asset in (
            "synapseos-logo.svg",
            "synapseos-icon.svg",
            "synapseos-welcome.png",
            "background.png",
            "show.qml",
        ):
            asset_path = branding_dir / asset
            self.assertTrue(asset_path.is_file(), f"Calamares asset {asset} must exist")
            self.assertGreater(asset_path.stat().st_size, 0, f"Calamares asset {asset} cannot be empty")

        # Validate show.qml structure (API 2 lifecycle and 4 slide themes)
        show_qml = (branding_dir / "show.qml").read_text(encoding="utf-8")
        self.assertIn("onActivate", show_qml)
        self.assertIn("onLeave", show_qml)
        self.assertIn("BORE", show_qml)
        self.assertIn("Ollama", show_qml)
        self.assertIn("Quad9", show_qml)
        self.assertIn("Catppuccin", show_qml)

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
        self.assertIn("Mod4+i", sway_conf)
        self.assertIn("Mod4+slash", sway_conf)
        self.assertIn("calamares -d", sway_conf)
        self.assertIn("swaybg -i", sway_conf)
        self.assertIn("Mod4+Ctrl+t", sway_conf)
        self.assertIn("Mod4+Shift+q", sway_conf)
        self.assertIn("Mod4+Shift+e", sway_conf)
        for rule in (
            "synapse-hud",
            "quickfire",
            "calamares",
            "galculator",
            "synapse-settings",
            "synapse-notes",
            "pavucontrol",
            "nm-connection-editor",
            "synapse-welcome",
            "synapse-screensaver",
        ):
            self.assertIn(rule, sway_conf)

        waybar_conf = (
            REPO_ROOT / "overlay" / "etc" / "skel" / ".config" / "waybar" / "config.jsonc"
        ).read_text(encoding="utf-8")
        self.assertNotIn("#00a8ff", waybar_conf.lower())
        self.assertIn("sway/workspaces", waybar_conf)
        self.assertIn("/usr/bin/quickfire", waybar_conf)
        self.assertIn("audio-switch", waybar_conf)
        self.assertIn("sec-status", waybar_conf)
        for widget in (
            "custom/menu",
            "custom/installer",
            "custom/terminal",
            "custom/ai",
            "custom/stealth",
            "custom/help",
            "custom/power",
        ):
            self.assertIn(widget, waybar_conf)

        # Verify audio-switch exists and is executable
        audio_switch = REPO_ROOT / "packages" / "desktop" / "synapse-hud" / "audio-switch"
        self.assertTrue(audio_switch.is_file(), "audio-switch script must exist")
        self.assertTrue(os.access(audio_switch, os.X_OK), "audio-switch must be executable")

        waybar_style = (
            REPO_ROOT / "overlay" / "etc" / "skel" / ".config" / "waybar" / "style.css"
        ).read_text(encoding="utf-8")
        self.assertNotIn("#00a8ff", waybar_style.lower())
        for color in ("#11111b", "#1e1e2e", "#cba6f7", "#cdd6f4"):
            self.assertIn(color, waybar_style.lower())
        for cls in (
            "#custom-menu",
            "#custom-installer",
            "#custom-terminal",
            "#custom-ai",
            "#custom-stealth",
            "#custom-help",
            "#custom-power",
        ):
            self.assertIn(cls, waybar_style)

    def test_sddm_greeter_qml_mock_load(self) -> None:
        """Validate that synapse-greeter Main.qml parses and instantiates cleanly with zero warnings/errors under mock SDDM context."""
        try:
            import os
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
            from PyQt6.QtCore import (
                QAbstractListModel,
                QModelIndex,
                QObject,
                Qt,
                pyqtProperty,
                pyqtSignal,
                pyqtSlot,
                qInstallMessageHandler,
            )
            from PyQt6.QtGui import QGuiApplication
            from PyQt6.QtQml import QQmlApplicationEngine, QQmlComponent
        except ImportError:
            self.skipTest("PyQt6 is required to perform QML offscreen mock validation")

        messages = []

        def msg_handler(msg_type, context, msg):
            messages.append((msg_type, msg))

        qInstallMessageHandler(msg_handler)

        app = QGuiApplication.instance() or QGuiApplication([])
        engine = QQmlApplicationEngine()

        class SessionModel(QAbstractListModel):
            NameRole = Qt.ItemDataRole.UserRole + 1

            def __init__(self):
                super().__init__()
                self._sessions = ["Sway", "XFCE"]
                self._lastIndex = 0

            def roleNames(self):
                return {self.NameRole: b"name"}

            def rowCount(self, parent=QModelIndex()):
                return len(self._sessions)

            def data(self, index, role=Qt.ItemDataRole.DisplayRole):
                if not index.isValid() or not (0 <= index.row() < len(self._sessions)):
                    return None
                if role in (self.NameRole, Qt.ItemDataRole.DisplayRole):
                    return self._sessions[index.row()]
                return None

            @pyqtProperty(int, constant=True)
            def lastIndex(self):
                return self._lastIndex

        class UserModel(QAbstractListModel):
            NameRole = Qt.ItemDataRole.UserRole + 1

            def __init__(self):
                super().__init__()
                self._users = ["synapse"]
                self._lastUser = "synapse"

            def roleNames(self):
                return {self.NameRole: b"name"}

            def rowCount(self, parent=QModelIndex()):
                return len(self._users)

            def data(self, index, role=Qt.ItemDataRole.DisplayRole):
                if not index.isValid() or not (0 <= index.row() < len(self._users)):
                    return None
                if role in (self.NameRole, Qt.ItemDataRole.DisplayRole):
                    return self._users[index.row()]
                return None

            @pyqtProperty(str, constant=True)
            def lastUser(self):
                return self._lastUser

        class LayoutObj(QObject):
            def __init__(self, short_name):
                super().__init__()
                self._shortName = short_name

            @pyqtProperty(str, constant=True)
            def shortName(self):
                return self._shortName

        class MockKeyboard(QObject):
            def __init__(self):
                super().__init__()
                self._capsLock = False
                self._currentLayout = 0
                self._l0 = LayoutObj("us")
                self._layouts = [self._l0]

            @pyqtProperty(bool, constant=True)
            def capsLock(self):
                return self._capsLock

            @pyqtProperty(int, constant=True)
            def currentLayout(self):
                return self._currentLayout

            @pyqtProperty("QVariantList", constant=True)
            def layouts(self):
                return self._layouts

        class MockConfig(QObject):
            @pyqtSlot(str, result=str)
            def stringValue(self, key):
                return {
                    "variant": "monolith-mauve",
                    "animations": "true",
                    "backgrounds": "/usr/share/backgrounds/synapseos",
                    "user": "synapse",
                }.get(key, "")

        class MockSddm(QObject):
            loginFailed = pyqtSignal()
            loginSucceeded = pyqtSignal()

            def __init__(self):
                super().__init__()

            @pyqtProperty(str, constant=True)
            def hostName(self):
                return "synapse"

            @pyqtProperty(bool, constant=True)
            def canReboot(self):
                return True

            @pyqtProperty(bool, constant=True)
            def canPowerOff(self):
                return True

            @pyqtSlot(str, str, int)
            def login(self, u, p, s):
                pass

            @pyqtSlot()
            def reboot(self):
                pass

            @pyqtSlot()
            def powerOff(self):
                pass

        m_sddm = MockSddm()
        m_config = MockConfig()
        m_keyboard = MockKeyboard()
        m_session = SessionModel()
        m_user = UserModel()

        ctx = engine.rootContext()
        ctx.setContextProperty("sddm", m_sddm)
        ctx.setContextProperty("config", m_config)
        ctx.setContextProperty("keyboard", m_keyboard)
        ctx.setContextProperty("sessionModel", m_session)
        ctx.setContextProperty("userModel", m_user)

        qml_path = REPO_ROOT / "packages" / "desktop" / "synapse-greeter" / "Main.qml"
        comp = QQmlComponent(engine, str(qml_path))
        self.assertEqual(comp.status(), QQmlComponent.Status.Ready, f"Errors: {[e.toString() for e in comp.errors()]}")
        obj = comp.create()
        self.assertIsNotNone(obj, "Main.qml component failed to instantiate")
        self.assertEqual(len(comp.errors()), 0, f"Component errors: {[e.toString() for e in comp.errors()]}")

        critical_errors = [m for _, m in messages if "ReferenceError" in m or "TypeError" in m]
        self.assertEqual(critical_errors, [], f"Detected runtime QML JS errors: {critical_errors}")


if __name__ == "__main__":
    unittest.main()
