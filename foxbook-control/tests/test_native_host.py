import io
import json
import struct
import subprocess
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "native_host"))
import foxbook_control as host  # noqa: E402


class NativeHostTests(unittest.TestCase):
    @staticmethod
    def display_output(transform="normal"):
        return ("HDMI-A-1 external\n  Enabled: yes\n  Transform: 270\n"
                f"eDP-1 Surface panel\n  Enabled: yes\n  Transform: {transform}\n  Scale: 1.5\n")

    def test_rotation_status_and_both_toggle_directions(self):
        for action, current in (("rotation_status", "normal"), ("toggle_rotation", "normal"), ("toggle_rotation", "90")):
            with self.subTest(action=action, current=current):
                target = "90" if current == "normal" else "normal"
                outputs = [self.display_output(current)]
                expected = [["/usr/bin/wlr-randr"]]
                if action == "toggle_rotation":
                    outputs += ["", self.display_output(target)]
                    expected += [["/usr/bin/wlr-randr", "--output", "eDP-1", "--transform", target], ["/usr/bin/wlr-randr"]]
                runner = mock.Mock(side_effect=[subprocess.CompletedProcess([], 0, stdout=text, stderr="") for text in outputs])
                result = host.process_request({"action": action}, runner, environment={"WAYLAND_DISPLAY": "wrong", "KEEP": "value"})
                self.assertEqual(result, host.response(True, output=target if action == "toggle_rotation" else current))
                self.assertEqual([call.args[0] for call in runner.call_args_list], expected)
                for call in runner.call_args_list:
                    self.assertEqual(call.kwargs["env"]["XDG_RUNTIME_DIR"], f"/run/user/{host.os.getuid()}")
                    self.assertEqual(call.kwargs["env"]["WAYLAND_DISPLAY"], "wayland-0")
                    self.assertEqual(call.kwargs["env"]["LC_ALL"], "C")
                    self.assertEqual(call.kwargs["env"]["KEEP"], "value")

    def test_rotation_never_changes_unknown_disabled_or_missing_output(self):
        outputs = ["", "HDMI-A-1\n  Enabled: yes\n  Transform: normal\n",
                   self.display_output("180"), self.display_output("flipped"),
                   self.display_output().replace("Enabled: yes", "Enabled: no"),
                   self.display_output().replace("Transform: normal", "Transform: normal\n  Transform: 90"),
                   self.display_output() + self.display_output(),
                   self.display_output().replace("Transform: normal", "Scale: 1")]
        for text in outputs:
            with self.subTest(text=text):
                runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0, stdout=text, stderr=""))
                result = host.process_request({"action": "toggle_rotation"}, runner)
                self.assertEqual(result["error"]["code"], "COMMAND_FAILED")
                self.assertEqual(runner.call_count, 1)

    def test_rotation_failed_command_or_verification_is_not_success(self):
        ok = subprocess.CompletedProcess([], 0, stdout=self.display_output(), stderr="")
        bad = subprocess.CompletedProcess([], 1, stdout="", stderr="failed")
        for results in ([bad], [ok, bad], [ok, ok, bad], [ok, ok, ok]):
            with self.subTest(results=results):
                result = host.process_request({"action": "toggle_rotation"}, mock.Mock(side_effect=results))
                self.assertEqual(result["error"]["code"], "COMMAND_FAILED")

    def test_rotation_missing_tool_permission_and_timeout_errors(self):
        for exception, code in ((FileNotFoundError(), "COMMAND_FAILED"), (PermissionError(), "PERMISSION_DENIED"),
                                (subprocess.TimeoutExpired("wlr-randr", 5), "TIMEOUT")):
            with self.subTest(exception=exception):
                result = host.process_request({"action": "rotation_status"}, mock.Mock(side_effect=exception))
                self.assertEqual(result["error"]["code"], code)
                if isinstance(exception, FileNotFoundError):
                    self.assertIn("wlr-randr", result["error"]["message"])

    def test_rotation_rejects_client_commands_and_targets(self):
        runner = mock.Mock()
        for action in ("rotation_status", "toggle_rotation"):
            result = host.process_request({"action": action, "output": "HDMI-A-1"}, runner)
            self.assertEqual(result["error"]["code"], "INVALID_REQUEST")
        runner.assert_not_called()

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
            "brightness_status": ["/usr/bin/brightnessctl", "--machine-readable", "--class=backlight", "info"],
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

    def test_set_brightness_uses_only_backlight_and_integer_percent(self):
        for brightness in (1, 54, 100):
            with self.subTest(brightness=brightness):
                def runner(command, **kwargs):
                    self.assertEqual(command, ["/usr/bin/brightnessctl", "--machine-readable", "--class=backlight", "set", f"{brightness}%"])
                    self.assertEqual(kwargs["timeout"], host.COMMAND_TIMEOUT_SECONDS)
                    self.assertFalse(kwargs["check"])
                    self.assertFalse(kwargs["start_new_session"])
                    return subprocess.CompletedProcess(command, 0, stdout=f"intel_backlight,backlight,{brightness},{brightness}%,100\n", stderr="")

                result = host.process_request({"action": "set_brightness", "brightness": brightness}, runner)
                self.assertTrue(result["success"])
                self.assertIn(f",{brightness}%,", result["output"])

    def test_set_brightness_rejects_invalid_requests_without_command(self):
        runner = mock.Mock(side_effect=AssertionError("invalid brightness must not run a command"))
        invalid = [{"action": "set_brightness"}]
        invalid.extend({"action": "set_brightness", "brightness": value}
                       for value in (None, 0, -1, 101, 54.0, True, "54%", "50%; id"))
        invalid.append({"action": "set_brightness", "brightness": 54, "device": "other"})
        for request in invalid:
            with self.subTest(request=request):
                self.assertEqual(host.process_request(request, runner)["error"]["code"], "INVALID_REQUEST")
        runner.assert_not_called()

    def test_brightness_command_errors(self):
        for action in ("brightness_status", "set_brightness"):
            request = {"action": action}
            if action == "set_brightness":
                request["brightness"] = 54
            for exception, code in ((FileNotFoundError(), "COMMAND_FAILED"),
                                    (PermissionError(), "PERMISSION_DENIED"),
                                    (subprocess.TimeoutExpired("brightnessctl", 5), "TIMEOUT")):
                with self.subTest(action=action, exception=exception):
                    result = host.process_request(request, mock.Mock(side_effect=exception))
                    self.assertEqual(result["error"]["code"], code)
                    if isinstance(exception, FileNotFoundError):
                        self.assertIn("brightnessctl", result["error"]["message"])

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
                self.assertTrue(kwargs["start_new_session"])
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

    def test_normal_score_sync_succeeds_with_real_process(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "sync-score.sh"
            script.write_text("#!/bin/sh\nprintf 'sync complete\\r\\n'\n")
            script.chmod(0o700)
            with mock.patch.object(host, "score_sync_command", return_value=[str(script)]):
                result = host.process_request({"action": "sync_score"})
            self.assertEqual(result, {"success": True, "output": "sync complete\n", "error": None})

    def test_score_sync_timeout_keeps_existing_error_code(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "sync-score.sh"
            script.write_text("#!/bin/sh\nsleep 10\n")
            script.chmod(0o700)
            with mock.patch.object(host, "score_sync_command", return_value=[str(script)]), \
                    mock.patch.object(host, "SYNC_TIMEOUT_SECONDS", 0.2):
                result = host.process_request({"action": "sync_score"})
            self.assertEqual(result["error"]["code"], "TIMEOUT")
            self.assertEqual(result["output"], "")

    def test_timeout_stops_child_process(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "child-finished"
            child = (
                "import time,pathlib; time.sleep(0.5); "
                f"pathlib.Path({str(marker)!r}).write_text('done')"
            )
            parent = (
                "import subprocess,sys,time; "
                f"subprocess.Popen([sys.executable, '-c', {child!r}]); "
                "time.sleep(10)"
            )
            with self.assertRaises(subprocess.TimeoutExpired):
                host.run_command_bounded(
                    [sys.executable, "-c", parent],
                    capture_output=True, text=True, timeout=0.3, check=False,
                    start_new_session=True,
                )
            time.sleep(0.6)
            self.assertFalse(marker.exists())

    def test_timeout_stops_child_after_script_exits(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "child-finished"
            child = (
                "import time,pathlib; time.sleep(0.5); "
                f"pathlib.Path({str(marker)!r}).write_text('done')"
            )
            parent = (
                "import subprocess,sys; "
                f"subprocess.Popen([sys.executable, '-c', {child!r}])"
            )
            with self.assertRaises(subprocess.TimeoutExpired):
                host.run_command_bounded(
                    [sys.executable, "-c", parent],
                    capture_output=True, text=True, timeout=0.3, check=False,
                    start_new_session=True,
                )
            time.sleep(0.6)
            self.assertFalse(marker.exists())

    def test_large_output_has_bounded_memory_and_result(self):
        command = [sys.executable, "-c", "import os; os.write(1, b'x' * 16_000_000); os.write(2, b'y' * 16_000_000)"]
        tracemalloc.start()
        try:
            result = host.run_command_bounded(
                command, capture_output=True, text=True, timeout=5, check=False,
            )
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(result.stdout), host.MAX_STDOUT_BYTES)
        self.assertEqual(len(result.stderr), host.MAX_STDERR_BYTES)
        self.assertLess(peak, 2_000_000)

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
