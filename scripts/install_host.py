#!/usr/bin/python3
"""Install the user-level Foxbook Native Messaging host."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


HOST_NAME = "foxbook_control"
EXTENSION_ID = "foxbook-control@foxbook.example"
SOURCE_HOST = Path(__file__).resolve().parents[1] / "native_host" / "foxbook_control.py"


def package_name(command: list[str]) -> str | None:
    if shutil.which(command[0]) is None:
        return None
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def firefox_kind(path: Path, home: Path) -> str:
    if not path.is_absolute():
        raise ValueError("--firefox には絶対パスを指定してください。")
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError("指定されたFirefoxが存在しないか、実行権限がありません。")
    resolved = path.resolve(strict=True)
    parts = set(path.parts) | set(resolved.parts)
    if "snap" in parts or "flatpak" in parts:
        raise ValueError("Snap／Flatpak版Firefoxは対象外です。")

    # Ubuntu's firefox DEB can be a small script that launches the Snap build.
    try:
        with path.open("rb") as stream:
            prefix = stream.read(4096)
    except OSError as exc:
        raise ValueError("Firefoxの実体を読み取れません。") from exc
    if prefix.startswith(b"#!") and (b"/snap/bin/firefox" in prefix or b"flatpak run" in prefix):
        raise ValueError("Snap／Flatpak版Firefoxの起動ラッパーは対象外です。")

    official_dir = home / ".local" / "opt" / "foxbook-firefox"
    if resolved == official_dir / "firefox":
        if not (official_dir / "firefox-bin").is_file() or not (official_dir / "application.ini").is_file():
            raise ValueError("Mozilla公式バイナリのディレクトリ構造を確認できません。")
        kind = "mozilla-binary"
    else:
        rpm_owner = package_name(["rpm", "-qf", str(resolved)])
        deb_owner = package_name(["dpkg-query", "-S", str(resolved)])
        if rpm_owner and re.match(r"^firefox-\d", rpm_owner):
            kind = "rpm"
        elif deb_owner and deb_owner.split(":", 1)[0] == "firefox":
            version = package_name(["dpkg-query", "-W", "-f=${Version}", "firefox"])
            if not version or "snap" in version.lower():
                raise ValueError("Snap版Firefoxの移行用パッケージは対象外です。")
            kind = "deb"
        else:
            raise ValueError("Firefoxの導入形態を判定できません。")

    try:
        result = subprocess.run([str(path), "--version"], text=True, capture_output=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Firefoxのバージョンを確認できません。") from exc
    if result.returncode != 0 or "Firefox" not in (result.stdout + result.stderr):
        raise ValueError("指定された実行ファイルがFirefoxであることを確認できません。")
    return kind


def check_target(path: Path) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(f"更新先が通常のファイルではありません: {path}")
    parent = path.parent
    while not parent.exists():
        parent = parent.parent
    if not parent.is_dir() or not os.access(parent, os.W_OK | os.X_OK):
        raise ValueError(f"更新先ディレクトリに書き込めません: {parent}")


def staged_file(directory: Path, content: bytes, mode: int) -> Path:
    fd, name = tempfile.mkstemp(prefix=f".{HOST_NAME}.", suffix=".tmp", dir=directory)
    path = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), mode)
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    return staged_file(path.parent, path.read_bytes(), path.stat().st_mode & 0o777)


def install(firefox: Path, home: Path) -> str:
    kind = firefox_kind(firefox, home)
    if not SOURCE_HOST.is_file():
        raise ValueError("インストール元のNative Hostが見つかりません。")
    host_bytes = SOURCE_HOST.read_bytes()
    compile(host_bytes, str(SOURCE_HOST), "exec")

    host_path = home / ".local" / "share" / "foxbook-control" / "foxbook_control.py"
    manifest_path = home / ".mozilla" / "native-messaging-hosts" / f"{HOST_NAME}.json"
    check_target(host_path)
    check_target(manifest_path)
    manifest = {
        "name": HOST_NAME,
        "description": "Foxbook Control Native Host",
        "path": str(host_path),
        "type": "stdio",
        "allowed_extensions": [EXTENSION_ID],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    json.loads(manifest_bytes)

    # All checks above complete before the first installation write.
    host_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    staged: list[Path] = []
    old_host: Path | None = None
    old_manifest: Path | None = None
    host_replaced = False
    manifest_replaced = False
    try:
        new_host = staged_file(host_path.parent, host_bytes, 0o700)
        staged.append(new_host)
        new_manifest = staged_file(manifest_path.parent, manifest_bytes, 0o600)
        staged.append(new_manifest)
        old_host = backup(host_path)
        if old_host:
            staged.append(old_host)
        old_manifest = backup(manifest_path)
        if old_manifest:
            staged.append(old_manifest)
        os.replace(new_host, host_path)
        host_replaced = True
        os.replace(new_manifest, manifest_path)
        manifest_replaced = True
    except BaseException:
        if manifest_replaced:
            if old_manifest:
                os.replace(old_manifest, manifest_path)
            else:
                manifest_path.unlink(missing_ok=True)
        if host_replaced:
            if old_host:
                os.replace(old_host, host_path)
            else:
                host_path.unlink(missing_ok=True)
        raise
    finally:
        for path in staged:
            path.unlink(missing_ok=True)
    return kind


def main() -> int:
    parser = argparse.ArgumentParser(description="Foxbook Native Messaging Host をユーザー単位で登録します。")
    parser.add_argument("--firefox", required=True, type=Path, help="検査対象Firefox実行ファイルの絶対パス")
    args = parser.parse_args()
    try:
        kind = install(args.firefox, Path.home())
    except (ValueError, OSError) as exc:
        print(f"インストール失敗: {exc}", file=sys.stderr)
        return 1
    print(f"Native Hostを登録しました（Firefox: {kind}）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
