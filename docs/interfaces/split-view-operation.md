---
relation: REL-SV-001
participants: [foxbook-firefox, fox-voice-editor, focodex]
status: experimental
updated: 2026-10-26
---

# Firefox Split View運用

## IF-SV-001: 保存済み比率のAutoConfig適用

| 項目 | 内容 |
| --- | --- |
| 提供側 | foxbook-firefox |
| 利用側 | fox-voice-editor、focodexを並べて使うFirefox利用者 |
| 開始条件 | Split View作成、または比率スライダーの操作。 |
| 成功時 | 保存した左ペイン比率を新規Split Viewへ適用する。 |
| 制約 | Firefox本体へAutoConfigを導入できる環境だけが対象。 |

- Firefox更新後の自己診断、タッチ操作、ツールバー再配置、環境差を検証対象とする。
