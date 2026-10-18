#!/usr/bin/python3
"""Foxbook Control native messaging host."""

from __future__ import annotations

import json
import logging
import os
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping


MAX_REQUEST_BYTES = 65536
COMMAND_TIMEOUT_SECONDS = 5
UPDATE_TIMEOUT_SECONDS = 30
SYNC_TIMEOUT_SECONDS = 900
LOGGER = logging.getLogger("foxbook_control")
COMMANDS = {
    "system_info": ("/usr/bin/uname", "-a"),
    "network_status": ("/usr/bin/nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"),
    "audio_status": ("/usr/bin/wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"),
    "brightness_status": ("/usr/bin/brightnessctl", "--machine-readable", "--class=backlight", "info"),
    "cage_logout": ("/usr/bin/loginctl", "--no-ask-password", "terminate-session", ""),
}
BATTERY_ROOT = Path("/sys/class/power_supply")
INSTALL_SOURCE_PATH = Path(__file__).resolve().with_name("install_source.json")
SCORE_SYNC_SCRIPT = Path.home() / "bin" / "sync-score.sh"


def response(success: bool, output: str = "", code: str | None = None, message: str = "") -> dict[str, Any]:
    return {
        "success": success,
        "output": output,
        "error": None if success else {"code": code, "message": message},
    }


def battery_status(root: Path = BATTERY_ROOT) -> str:
    batteries = []
    for supply in sorted(root.iterdir()):
        if (supply / "type").read_text(encoding="utf-8").strip() != "Battery":
            continue
        capacity = int((supply / "capacity").read_text(encoding="utf-8").strip())
        if not 0 <= capacity <= 100:
            raise ValueError("battery capacity out of range")
        state = (supply / "status").read_text(encoding="utf-8").strip()
        state_name = {
            "Charging": "充電中", "Discharging": "放電中", "Full": "満充電",
            "Not charging": "充電停止中", "Unknown": "状態不明",
        }.get(state, "状態不明")
        batteries.append(f"{supply.name}: {capacity}%（{state_name}）")
    return "\n".join(batteries) if batteries else "バッテリーが見つかりません。"


def update_command(source_path: Path = INSTALL_SOURCE_PATH) -> list[str]:
    config = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) != {"installer", "firefox"}:
        raise ValueError("invalid install source")
    installer, firefox = config["installer"], config["firefox"]
    if not all(isinstance(value, str) and Path(value).is_absolute() for value in (installer, firefox)):
        raise ValueError("invalid install source paths")
    if Path(installer).name != "install_host.py" or not Path(installer).is_file():
        raise ValueError("installer is unavailable")
    if not (Path(installer).parent.parent / "native_host" / "foxbook_control.py").is_file():
        raise ValueError("host source is unavailable")
    return [sys.executable, installer, "--firefox", firefox]


def score_sync_command(script: Path = SCORE_SYNC_SCRIPT) -> list[str]:
    if not script.is_file():
        raise FileNotFoundError(script)
    if not os.access(script, os.X_OK):
        raise PermissionError(13, "script is not executable", str(script))
    return [str(script)]


def process_request(
    request: Any, run_command: Callable[..., Any] = subprocess.run, battery_root: Path = BATTERY_ROOT,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if not isinstance(request, dict) or not isinstance(request.get("action"), str):
        return response(False, code="INVALID_REQUEST", message="要求の形式が正しくありません。")

    action = request["action"]
    if action in ("set_volume", "set_brightness"):
        field, label, minimum = ("volume", "音量", 0) if action == "set_volume" else ("brightness", "輝度", 1)
        if (set(request) != {"action", field} or type(request[field]) is not int
                or not minimum <= request[field] <= 100):
            return response(False, code="INVALID_REQUEST", message=f"{label}は{minimum}から100の整数で指定してください。")
    elif set(request) != {"action"}:
        return response(False, code="INVALID_REQUEST", message="要求の形式が正しくありません。")
    if action not in COMMANDS and action not in ("battery_status", "update_host", "set_volume", "set_brightness", "sync_score"):
        return response(False, code="UNKNOWN_ACTION", message="未登録の操作です。")
    if action == "cage_logout" and (environment if environment is not None else os.environ).get("FOXBOOK_CAGE_SESSION") != "1":
        return response(False, code="PERMISSION_DENIED", message="Cageセッションからのみログアウトできます。")

    try:
        if action == "battery_status":
            return response(True, output=battery_status(battery_root))
        if action == "update_host":
            try:
                command = update_command()
            except (OSError, ValueError) as exc:
                LOGGER.warning("host update source unavailable: %s", exc)
                return response(False, code="COMMAND_FAILED", message="更新元が見つかりません。端末からインストーラーを再実行してください。")
        elif action == "sync_score":
            try:
                command = score_sync_command()
            except FileNotFoundError:
                return response(False, code="COMMAND_FAILED", message="~/bin/sync-score.sh が見つかりません。")
        elif action == "set_volume":
            command = ["/usr/bin/wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{request['volume']}%"]
        elif action == "set_brightness":
            command = ["/usr/bin/brightnessctl", "--machine-readable", "--class=backlight", "set", f"{request['brightness']}%"]
        else:
            command = list(COMMANDS[action])
        result = run_command(
            command, capture_output=True, text=True,
            timeout=(SYNC_TIMEOUT_SECONDS if action == "sync_score" else
                     UPDATE_TIMEOUT_SECONDS if action == "update_host" else COMMAND_TIMEOUT_SECONDS),
            check=False,
        )
    except subprocess.TimeoutExpired:
        LOGGER.warning(
            "command timeout: action=%s seconds=%s", action,
            (SYNC_TIMEOUT_SECONDS if action == "sync_score" else
             UPDATE_TIMEOUT_SECONDS if action == "update_host" else COMMAND_TIMEOUT_SECONDS),
        )
        return response(False, code="TIMEOUT", message="操作が時間内に完了しませんでした。")
    except PermissionError as exc:
        LOGGER.warning("permission denied: action=%s errno=%s", request["action"], exc.errno)
        return response(False, code="PERMISSION_DENIED", message="この操作を実行する権限がありません。")
    except FileNotFoundError as exc:
        LOGGER.error("command not found: action=%s errno=%s", action, exc.errno)
        message = "brightnessctlが見つかりません。インストールしてください。" if action in ("brightness_status", "set_brightness") else "操作を完了できませんでした。"
        return response(False, code="COMMAND_FAILED", message=message)
    except OSError as exc:
        LOGGER.error("command start failed: action=%s errno=%s", request["action"], exc.errno)
        return response(False, code="COMMAND_FAILED", message="操作を完了できませんでした。")
    except Exception:
        LOGGER.exception("unexpected command error: action=%s", request["action"])
        return response(False, code="INTERNAL_ERROR", message="内部エラーが発生しました。")

    if result.returncode != 0:
        LOGGER.error(
            "command failed: action=%s returncode=%s stderr=%r",
            request["action"], result.returncode, result.stderr[:4096],
        )
        return response(False, code="COMMAND_FAILED", message="楽譜の同期に失敗しました。" if action == "sync_score" else "操作を完了できませんでした。")
    return response(True, output=result.stdout)


def read_exact(stream: Any, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = stream.read(size - len(chunks))
        if not chunk:
            raise EOFError("incomplete native message")
        chunks.extend(chunk)
    return bytes(chunks)


def read_message(stream: Any) -> Any:
    header = stream.read(4)
    if not header:
        raise EOFError("no native message")
    if len(header) < 4:
        header += read_exact(stream, 4 - len(header))
    size = struct.unpack("=I", header)[0]
    if size > MAX_REQUEST_BYTES:
        raise ValueError("native message too large")
    return json.loads(read_exact(stream, size).decode("utf-8"))


def write_message(stream: Any, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    stream.write(struct.pack("=I", len(data)))
    stream.write(data)
    stream.flush()


def main() -> int:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="foxbook-control %(levelname)s: %(message)s")
    try:
        request = read_message(sys.stdin.buffer)
    except EOFError:
        return 1
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        LOGGER.warning("invalid native request: %s", exc)
        write_message(sys.stdout.buffer, response(False, code="INVALID_REQUEST", message="要求の形式が正しくありません。"))
        return 0

    write_message(sys.stdout.buffer, process_request(request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
