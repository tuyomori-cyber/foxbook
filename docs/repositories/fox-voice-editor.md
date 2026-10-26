---
repository: fox-voice-editor
updated: 2026-10-26
---

# fox-voice-editor 横断管理

## このリポジトリの責務

- 音声、手入力、定型、記号を文章ブロックとして編集する。

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-VE-FD-001` | focodex | 送信側 | active | [契約](../interfaces/fox-voice-editor--focodex.md) |
| `IF-VE-FD-002` | focodex | 再送側 | active | [契約](../interfaces/fox-voice-editor--focodex.md) |
| `IF-VE-OSK-001` | Firefox-On-Screen-Keyboard | 利用側 | active | [契約](../interfaces/fox-voice-editor--firefox-on-screen-keyboard.md) |
| `IF-SV-001` | foxbook-firefox | 利用側 | experimental | [契約](../interfaces/split-view-operation.md) |
