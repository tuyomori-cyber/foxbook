---
relation: REL-VE-FD-001
participants: [fox-voice-editor, focodex]
status: active
updated: 2026-10-26
---

# fox-voice-editor ↔ Focodex

## 共通前提

- 両拡張は同じFirefoxプロファイルに読み込む。

## IF-VE-FD-001: 文章の受信バッファ投入

| 項目 | 内容 |
| --- | --- |
| 送信側 | fox-voice-editor |
| 受信側 | focodex |
| 開始条件 | ユーザーが「Focodexへ貼り付け」を実行する。 |
| 成功時 | FocodexのFIFO受信バッファへ文章を保存する。 |
| 失敗時 | 理由を表示し、入力欄やCodex実行に副作用を起こさない。 |

- 送信元はFirefoxが渡す`sender.id`が`fox-voice-editor@foxbook.example`と一致する場合だけ受理する。
- 要求は`{type:"focodex.buffer.receive", version:1, requestId:UUID, text:string}`だけを受理する。本文は空白だけを除く1〜20,000 UTF-16コード単位とし、空白・改行を変更しない。
- 最大3件のFIFOで保持し、新規受信時に最古の項目を押し出す。受信だけでは指示文、Commit欄、Codex実行を変更しない。
- 応答は`{version:1, requestId, status, reason?}`。`status`は`accepted`、`duplicate`、`rejected`である。

## IF-VE-FD-002: 同一ID・本文による明示再送

- 同一ID・同一本文は重複追加せず、同一ID・異なる本文は拒否する。
- 受理済みIDと本文は直近100件・24時間を上限に保持する。送信側は応答喪失時だけ、同一ID・同一本文を明示再送できる。
- 拒否理由は`unauthorized`、`invalid_message`、`rate_limited`、`request_id_conflict`、`storage_error`の定型値だけを返す。
