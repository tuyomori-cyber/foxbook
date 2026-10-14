#!/usr/bin/python3
"""Foxbook Control native messaging host."""

from __future__ import annotations

import json
import logging
import struct
import subprocess
import sys
from typing import Any, Callable


MAX_REQUEST_BYTES = 65536
COMMAND_TIMEOUT_SECONDS = 5
LOGGER = logging.getLogger("foxbook_control")
COMMANDS = {"system_info": ("/usr/bin/uname", "-a")}


def response(success: bool, output: str = "", code: str | None = None, message: str = "") -> dict[str, Any]:
    return {
        "success": success,
        "output": output,
        "error": None if success else {"code": code, "message": message},
    }


def process_request(request: Any, run_command: Callable[..., Any] = subprocess.run) -> dict[str, Any]:
    if not isinstance(request, dict) or set(request) != {"action"} or not isinstance(request["action"], str):
        return response(False, code="INVALID_REQUEST", message="要求の形式が正しくありません。")

    command = COMMANDS.get(request["action"])
    if command is None:
        return response(False, code="UNKNOWN_ACTION", message="未登録の操作です。")

    try:
        result = run_command(
            list(command), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SECONDS, check=False
        )
    except subprocess.TimeoutExpired:
        LOGGER.warning("command timeout: action=%s seconds=%s", request["action"], COMMAND_TIMEOUT_SECONDS)
        return response(False, code="TIMEOUT", message="操作が時間内に完了しませんでした。")
    except PermissionError as exc:
        LOGGER.warning("permission denied: action=%s errno=%s", request["action"], exc.errno)
        return response(False, code="PERMISSION_DENIED", message="この操作を実行する権限がありません。")
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
        return response(False, code="COMMAND_FAILED", message="操作を完了できませんでした。")
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
