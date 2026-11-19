---
repository: foxbook-speech
updated: 2026-11-19
---

# foxbook-speech 横断管理

## このリポジトリの責務

- 許可済みFirefox拡張向けの共通音声認識Native Messaging Hostを提供する。
- ユーザー単位の音声serviceで、マイク排他、録音・変換、Whisper／ReazonSpeech、取消、回収を管理する。
- 共通音声API、systemd運用、導入・検証手順を管理する。
- 共通音声アシスタントを音声基盤と分離した構成要素として設ける方針。第1段階としてContent Scriptによる表示試作を管理する。

音声serviceとHostは、編集、履歴・定型文、認識後のコマンド解釈、Focodex／OSK連携、端末制御、ファイル操作を所有しない。将来のアシスタントによるコマンド解釈は音声基盤とは分離して設計する。

## 正本へのリンク

- [README](../../../foxbook-speech/README.md)
- [仕様書 v0.1](../../../foxbook-speech/specification/foxbook-speech仕様書v0.1.md)
- [TODO](../../../foxbook-speech/TODO.md)
- [共通UI表示試作](../../../foxbook-speech/assistant-ui/README.md)

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-VE-SP-001` | fox-voice-editor | 提供側 | active | [契約](../interfaces/fox-voice-editor--foxbook-speech.md) |

## 変更時の影響確認

- Host名、許可拡張ID、API、IPC、マイク排他、端末設定を変える場合は、利用側と同じ変更単位で契約・導入手順・実機検証を更新する。
- 音声Hostへ端末制御・ファイル操作など別用途の権限を追加しない。
