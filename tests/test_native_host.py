import io
import json
import struct
import subprocess
import sys
from pathlib import Path
import unittest


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
