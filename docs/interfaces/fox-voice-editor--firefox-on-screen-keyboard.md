---
relation: REL-VE-OSK-001
participants: [fox-voice-editor, Firefox-On-Screen-Keyboard]
status: active
updated: 2026-10-26
---

# fox-voice-editor ↔ Firefox-On-Screen-Keyboard

## IF-VE-OSK-001: 埋め込みキーボード表示とキー入力

| 項目 | 内容 |
| --- | --- |
| 利用側 | fox-voice-editor |
| 提供側 | Firefox-On-Screen-Keyboard |
| 開始条件 | 手入力欄へのフォーカス。 |
| 成功時 | 埋め込みフレームを表示し、キー入力を手入力欄へ反映する。 |
| 終了時 | 閉鎖後は非表示・非受付にし、再フォーカスで再表示する。 |

- FX-OSKの固定拡張IDは`fx-osk-touch@tuyomori-cyber.github.io`。
- voice-editorは`fxosk.frame.request`（version 1）を送り、FX-OSKは`fxosk.frame.response`と埋め込みURLを返す。
- frameは`fxosk.key`と`fxosk.visibility`を親へ通知し、親は`fxosk.show`で再表示を要求する。
- 現行FX-OSKは外部要求の型とversionを検証するが、送信元拡張IDを検証しない。強化は両リポジトリで追跡する。
