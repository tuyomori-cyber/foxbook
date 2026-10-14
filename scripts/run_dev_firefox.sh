#!/bin/sh
set -eu

firefox="$HOME/.local/opt/foxbook-firefox/firefox"
profile="$HOME/.local/share/foxbook-control/firefox-profile"

if [ ! -x "$firefox" ]; then
    printf '%s\n' "検証用Firefoxが見つからないか、実行権限がありません: $firefox" >&2
    exit 1
fi

mkdir -p "$profile"
exec "$firefox" -profile "$profile" --no-remote "$@"
