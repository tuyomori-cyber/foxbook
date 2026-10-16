import io
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "native_host"))
import foxbook_control as host  # noqa: E402


class NativeHostTests(unittest.TestCase):
    def test_unknown_action_returns_framed_json_without_running_command(self):
        calls = []

        def forbidden_runner(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("OS command must not run")

        result = host.process_request({"action": "not_registered"}, forbidden_runner)
        self.assertEqual(calls, [])
        self.assertEqual(result["success"], False)
        self.assertEqual(result["output"], "")
        self.assertEqual(result["error"]["code"], "UNKNOWN_ACTION")
        self.assertIsInstance(result["error"]["message"], str)

        stream = io.BytesIO()
        host.write_message(stream, result)
        packet = stream.getvalue()
        self.assertEqual(struct.unpack("=I", packet[:4])[0], len(packet) - 4)
        self.assertEqual(json.loads(packet[4:].decode("utf-8")), result)

    def test_system_info_uses_only_fixed_command(self):
        def runner(command, **kwargs):
            self.assertEqual(command, ["/usr/bin/uname", "-a"])
            self.assertEqual(kwargs["timeout"], 5)
            self.assertFalse(kwargs["check"])
            return subprocess.CompletedProcess(command, 0, stdout="Linux test\n", stderr="")

        self.assertEqual(
            host.process_request({"action": "system_info"}, runner),
            {"success": True, "output": "Linux test\n", "error": None},
        )

    def test_status_actions_use_fixed_commands(self):
        expected = {
            "network_status": ["/usr/bin/nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
            "audio_status": ["/usr/bin/wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
        }
        for action, command in expected.items():
            with self.subTest(action=action):
                def runner(actual, **kwargs):
                    self.assertEqual(actual, command)
                    self.assertEqual(kwargs["timeout"], 5)
                    return subprocess.CompletedProcess(actual, 0, stdout="status\n", stderr="")

                self.assertEqual(host.process_request({"action": action}, runner)["output"], "status\n")

    def test_set_volume_uses_fixed_sink_and_percent(self):
        def runner(command, **kwargs):
            self.assertEqual(command, ["/usr/bin/wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "54%"])
            self.assertEqual(kwargs["timeout"], host.COMMAND_TIMEOUT_SECONDS)
            self.assertFalse(kwargs["check"])
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        self.assertEqual(
            host.process_request({"action": "set_volume", "volume": 54}, runner),
            {"success": True, "output": "", "error": None},
        )

    def test_set_volume_rejects_invalid_values_without_running_command(self):
        def forbidden_runner(*args, **kwargs):
            raise AssertionError("invalid volume must not run a command")

        invalid_requests = [
            {"action": "set_volume"},
            {"action": "set_volume", "volume": -1},
            {"action": "set_volume", "volume": 101},
            {"action": "set_volume", "volume": 55.0},
            {"action": "set_volume", "volume": True},
            {"action": "set_volume", "volume": "55%"},
            {"action": "set_volume", "volume": 55, "command": "id"},
        ]
        for request in invalid_requests:
            with self.subTest(request=request):
                self.assertEqual(
                    host.process_request(request, forbidden_runner)["error"]["code"], "INVALID_REQUEST"
                )

    def test_battery_status_reads_only_battery_supplies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            battery = root / "BAT0"
            battery.mkdir()
            (battery / "type").write_text("Battery\n")
            (battery / "capacity").write_text("73\n")
            (battery / "status").write_text("Charging\n")
            mains = root / "AC"
            mains.mkdir()
            (mains / "type").write_text("Mains\n")

            def forbidden_runner(*args, **kwargs):
                raise AssertionError("OS command must not run")

            result = host.process_request({"action": "battery_status"}, forbidden_runner, root)
            self.assertEqual(result["output"], "BAT0: 73%（充電中）")

    def test_battery_status_without_battery(self):
        with tempfile.TemporaryDirectory() as directory:
            result = host.process_request({"action": "battery_status"}, battery_root=Path(directory))
            self.assertEqual(result["output"], "バッテリーが見つかりません。")

    def test_cage_logout_is_rejected_outside_marked_session(self):
        def forbidden_runner(*args, **kwargs):
            raise AssertionError("logout must not run outside Cage")

        result = host.process_request({"action": "cage_logout"}, forbidden_runner, environment={})
        self.assertEqual(result["error"]["code"], "PERMISSION_DENIED")

    def test_cage_logout_targets_only_callers_session(self):
        def runner(command, **kwargs):
            self.assertEqual(command, ["/usr/bin/loginctl", "--no-ask-password", "terminate-session", ""])
            self.assertEqual(kwargs["timeout"], 5)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        result = host.process_request({"action": "cage_logout"}, runner, environment={"FOXBOOK_CAGE_SESSION": "1"})
        self.assertEqual(result, {"success": True, "output": "", "error": None})

    def test_host_update_uses_recorded_installer_and_firefox(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            source_host = root / "native_host" / "foxbook_control.py"
            scripts.mkdir()
            source_host.parent.mkdir()
            installer = scripts / "install_host.py"
            installer.write_text("# installer\n")
            source_host.write_text("# host\n")
            firefox = root / "firefox"
            config = root / "install_source.json"
            config.write_text(json.dumps({"installer": str(installer), "firefox": str(firefox)}))
            self.assertEqual(host.update_command(config), [sys.executable, str(installer), "--firefox", str(firefox)])

            def runner(command, **kwargs):
                self.assertEqual(command, [sys.executable, str(installer), "--firefox", str(firefox)])
                self.assertEqual(kwargs["timeout"], host.UPDATE_TIMEOUT_SECONDS)
                return subprocess.CompletedProcess(command, 0, stdout="Native Hostを登録しました。\n", stderr="")

            with mock.patch.object(host, "update_command", return_value=host.update_command(config)):
                self.assertTrue(host.process_request({"action": "update_host"}, runner)["success"])

    def test_host_update_without_recorded_source_fails_without_command(self):
        def forbidden_runner(*args, **kwargs):
            raise AssertionError("installer must not run")

        with mock.patch.object(host, "update_command", side_effect=FileNotFoundError()):
            result = host.process_request({"action": "update_host"}, forbidden_runner)
        self.assertEqual(result["error"]["code"], "COMMAND_FAILED")

    def test_score_sync_runs_only_home_script_and_reports_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "sync-score.sh"
            script.write_text("#!/bin/bash\n")
            script.chmod(0o700)

            def runner(command, **kwargs):
                self.assertEqual(command, [str(script)])
                self.assertEqual(kwargs["timeout"], host.SYNC_TIMEOUT_SECONDS)
                self.assertFalse(kwargs["check"])
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="sync failed")

            with mock.patch.object(host, "score_sync_command", return_value=host.score_sync_command(script)):
                result = host.process_request({"action": "sync_score"}, runner)
            self.assertEqual(result["error"]["code"], "COMMAND_FAILED")
            self.assertEqual(result["error"]["message"], "楽譜の同期に失敗しました。")

    def test_score_sync_missing_script_never_runs_command(self):
        with tempfile.TemporaryDirectory() as directory:
            def forbidden_runner(*args, **kwargs):
                raise AssertionError("missing script must not run")

            with mock.patch.object(host, "score_sync_command", side_effect=FileNotFoundError()):
                result = host.process_request({"action": "sync_score"}, forbidden_runner)
            self.assertEqual(result["error"]["code"], "COMMAND_FAILED")
            self.assertIn("sync-score.sh", result["error"]["message"])

    def test_extra_fields_are_rejected_without_running_command(self):
        def forbidden_runner(*args, **kwargs):
            raise AssertionError("OS command must not run")

        result = host.process_request({"action": "system_info", "command": "id"}, forbidden_runner)
        self.assertEqual(result["error"]["code"], "INVALID_REQUEST")

    def test_permission_error_is_explicit(self):
        def runner(*args, **kwargs):
            raise PermissionError(13, "Permission denied")

        self.assertEqual(host.process_request({"action": "system_info"}, runner)["error"]["code"], "PERMISSION_DENIED")

    def test_ambiguous_command_failure_is_not_permission_denied(self):
        def runner(command, **kwargs):
            return subprocess.CompletedProcess(command, 1, stdout="", stderr="Permission denied")

        self.assertEqual(host.process_request({"action": "system_info"}, runner)["error"]["code"], "COMMAND_FAILED")


if __name__ == "__main__":
    unittest.main()
