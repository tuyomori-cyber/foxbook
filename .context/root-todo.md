# Auto ToDo Root

> 現在のNow/Nextだけを記載。各プロジェクトの詳細・保留事項は各TODO.mdへ。

## Now

- Done: GNOME KeyringのLoginコレクションがGDM/PAMで自動解除されることをSurface再起動後に確認。
- Done: 固定宛先・専用Agent・最小known_hosts・中継を統合した読み取り専用SSH接続試験を実装・回帰確認。
- Done: Surfaceでfoxbookログイン後の専用Agent再生成・鍵自動登録が`ready`になることを確認。
- Done: 終了未確認の安全停止解除、明示SSH URL化、専用Agent・直接`ls-remote`・中継事前試験をSurfaceで確認。
- Pending: Focodex固定中継経路では`wrapper-command`後に中継未到達。実upstream読み取り専用試験は未成功。

## Next

- Surface実機のCodex CLIへ開発を移管し、固定SSHラッパーからProxyCommandが開始されない原因を安全な内部診断で解決する。Fetch/Pushは実装・実行しない。
