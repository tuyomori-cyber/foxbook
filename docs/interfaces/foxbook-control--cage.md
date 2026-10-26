---
relation: REL-CTL-CAGE-001
participants: [foxbook-control, cage]
status: active
updated: 2026-10-26
---

# foxbook-control ↔ cage

## IF-CTL-CAGE-001: Cageでの画面回転とログアウト

| 項目 | 内容 |
| --- | --- |
| 利用側 | foxbook-control Native Host |
| 提供側 | Cage／Waylandセッション |
| 開始条件 | ユーザーが回転またはCageログアウトを明示操作する。 |
| 成功時 | `eDP-1`の`normal`／`90`を確認・切替、または呼び出し元Cageセッションを終了する。 |
| 安全境界 | 任意コマンド・任意出力・任意セッションを受け付けない。 |

- cage側の改造`e7e88b1`は、単一出力キオスクで`90`／`180`／`270`回転時のタッチdown／motion座標を補正する。複数出力は対象外。
- foxbook-controlは`wlr-randr`で`eDP-1`だけを操作し、`normal`と`90`以外は拒否する。変更後は状態を再取得する。
- `cage_logout`は`FOXBOOK_CAGE_SESSION=1`がある時だけ呼出元ログインセッションを終了する。Cage自体にはログアウト改造を加えない。
