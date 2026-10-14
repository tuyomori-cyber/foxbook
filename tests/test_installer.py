import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install_host as installer  # noqa: E402


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.browser_dir = self.home / ".local" / "opt" / "foxbook-firefox"
        self.browser_dir.mkdir(parents=True)
        self.firefox = self.browser_dir / "firefox"
        self.firefox.write_text("#!/bin/sh\nprintf 'Mozilla Firefox 157.0\\n'\n")
        self.firefox.chmod(0o700)
        (self.browser_dir / "firefox-bin").write_bytes(b"binary")
        (self.browser_dir / "application.ini").write_text("[App]\nName=Firefox\n")
        self.host = self.home / ".local" / "share" / "foxbook-control" / "foxbook_control.py"
        self.source = self.host.parent / "install_source.json"
        self.manifest = self.home / ".mozilla" / "native-messaging-hosts" / "foxbook_control.json"

    def test_install_and_rerun_update_host_source_and_manifest(self):
        profile = self.host.parent / "firefox-profile"
        profile.mkdir(parents=True)
        marker = profile / "keep.txt"
        marker.write_text("keep")
        self.assertEqual(installer.install(self.firefox, self.home), "mozilla-binary")
        self.assertEqual(installer.install(self.firefox, self.home), "mozilla-binary")
        self.assertTrue(self.host.stat().st_mode & 0o100)
        self.assertEqual(json.loads(self.manifest.read_text())["path"], str(self.host))
        self.assertEqual(json.loads(self.source.read_text()), {"installer": str(installer.SOURCE_INSTALLER), "firefox": str(self.firefox)})
        self.assertEqual(json.loads(self.manifest.read_text())["allowed_extensions"], [installer.EXTENSION_ID])
        self.assertEqual(marker.read_text(), "keep")
        self.assertEqual(list(self.host.parent.glob(".*.tmp")), [])
        self.assertEqual(list(self.manifest.parent.glob(".*.tmp")), [])

    def test_unknown_browser_does_not_create_installation(self):
        unknown = self.home / "other-firefox"
        unknown.write_text("#!/bin/sh\nprintf 'Mozilla Firefox 157.0\\n'\n")
        unknown.chmod(0o700)
        with self.assertRaisesRegex(ValueError, "判定できません"):
            installer.install(unknown, self.home)
        self.assertFalse(self.host.exists())
        self.assertFalse(self.source.exists())
        self.assertFalse(self.manifest.exists())

    def test_snap_wrapper_does_not_create_installation(self):
        self.firefox.write_text("#!/bin/sh\nexec /snap/bin/firefox \"$@\"\n")
        with self.assertRaisesRegex(ValueError, "Snap"):
            installer.install(self.firefox, self.home)
        self.assertFalse(self.host.exists())
        self.assertFalse(self.source.exists())
        self.assertFalse(self.manifest.exists())

    def test_failed_manifest_replace_restores_previous_host(self):
        installer.install(self.firefox, self.home)
        original_host = self.host.read_bytes()
        original_source = self.source.read_bytes()
        original_manifest = self.manifest.read_bytes()
        updated_source = self.home / "updated_host.py"
        updated_source.write_bytes(original_host + b"\n# updated\n")
        real_replace = installer.os.replace

        def fail_manifest_replace(source, target):
            if Path(target) == self.manifest:
                raise OSError("simulated failure")
            return real_replace(source, target)

        with mock.patch.object(installer, "SOURCE_HOST", updated_source), mock.patch.object(installer.os, "replace", side_effect=fail_manifest_replace):
            with self.assertRaisesRegex(OSError, "simulated failure"):
                installer.install(self.firefox, self.home)

        self.assertEqual(self.host.read_bytes(), original_host)
        self.assertEqual(self.source.read_bytes(), original_source)
        self.assertEqual(self.manifest.read_bytes(), original_manifest)
        self.assertEqual(list(self.host.parent.glob(".*.tmp")), [])
        self.assertEqual(list(self.manifest.parent.glob(".*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
