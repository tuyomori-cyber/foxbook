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

## IF-VE-FD-002: 同一ID・本文による明示再送

- 同一ID・同一本文は重複追加せず、同一ID・異なる本文は拒否する。
- 正確なメッセージ形式、送信元検証、公開操作は両実装の現行仕様と照合して追記する。
