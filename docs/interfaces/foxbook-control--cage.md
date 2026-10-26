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
| 成功時 | 固定対象の向きを確認・切替、または呼び出し元Cageセッションを終了する。 |
| 安全境界 | 任意コマンド・任意出力・任意セッションを受け付けない。 |

- 対象出力、環境変数、許可条件、変更後の再確認は実装仕様と照合して追記する。
