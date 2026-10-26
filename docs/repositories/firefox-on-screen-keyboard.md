---
repository: Firefox-On-Screen-Keyboard
updated: 2026-10-26
---

# Firefox-On-Screen-Keyboard 横断管理

## このリポジトリの責務

- fox-voice-editorに埋め込み可能なオンスクリーンキーボードとキー入力通知を提供する。

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-VE-OSK-001` | fox-voice-editor | 提供側 | active | [契約](../interfaces/fox-voice-editor--firefox-on-screen-keyboard.md) |

## 正本へのリンク

- [README](../../../Firefox-On-Screen-Keyboard/README.md)
- [現行仕様 v0.2](../../../Firefox-On-Screen-Keyboard/specification/fx-osk仕様書v0.2.md)
- [TODO](../../../Firefox-On-Screen-Keyboard/TODO.md)
- [旧文書](../../../Firefox-On-Screen-Keyboard/old/)

## 変更時の影響確認

- `IF-VE-OSK-001`のメッセージ、フレーム表示、閉鎖、再表示を変える場合はfox-voice-editorと同じ変更単位で確認する。
- 外部メッセージの送信元制限を導入する場合は、既存のfox-voice-editor設定と実機連携を確認する。
