---
relation: REL-VE-SP-001
participants: [fox-voice-editor, foxbook-speech]
status: implemented-pending-firefox-verification
updated: 2026-11-16
---

# fox-voice-editor ↔ foxbook-speech

## IF-VE-SP-001: 共通ローカル音声認識

| 項目 | 内容 |
| --- | --- |
| 状態 | 実装済み・Firefox実機確認待ち |
| 利用側 | fox-voice-editor Firefox拡張 |
| 提供側 | foxbook-speech Native Messaging Hostと音声service |
| 開始条件 | Voice Editorが許可済み拡張IDとして`connectNative("foxbook_speech")`を接続し、マイク・engine準備後に録音開始を要求する。 |
| 成功時 | 提供側がサービス発行の`recordingId`付き認識テキストと計測値を返す。Voice Editorは照合後にブロックと履歴へ反映する。 |
| 失敗時 | 提供側は固定エラーコードを返し、Voice Editorは既存ブロック・履歴を変更しない。 |

### 契約

- API v1の操作は`prepare_microphone`、`prepare_engine`、`start_recording`、`stop_recording(recordingId)`、`cancel_recording(recordingId)`、`get_status`だけとする。`load_library`と`save_library`は含めない。
- 提供側は`start_recording`から終端イベントまでの全phaseを一件の録音リースとして扱い、同時開始を待ち行列へ入れず`BUSY`で拒否する。録音リースは結果、エラー、取消、接続切断、service停止、タイムアウトのいずれでも回収する。
- 要求元の認可はNative Messaging manifestの許可済み拡張ID、adapterの起動元ID検証、adapterとserviceを結ぶsocket sessionで行う。本文内の利用者IDは受理・認可しない。停止・取消・イベント配送は録音を所有するsessionに限定する。
- Voice Editorは音声用`speechPort`と、編集固有の履歴・定型文を扱う`fox_voice_editor`への`libraryPort`を分離する。speechPort切断は録音だけを停止し、libraryPort切断は既存どおり編集開始を抑止する。
- ReazonSpeechはservice側でengine名とモデル設定revisionごとに最大一つのWorkerを保持する。Voice Editorのengine切替は他sessionのWorkerを停止しない。
- Focodex配送、FX-OSK、編集状態の保存はこの契約の対象外であり、既存契約を維持する。

### 互換性と検証

- 移行中だけ旧Hostの音声要求を共通APIへ変換してよい。最終構成ではVoice Editorが`foxbook_speech`へ直接接続する。
- 単独録音、停止、取消、空結果、二重要求、Host切断、タブ再読み込み、service再起動、Surface上の連続録音・Worker回収を自動試験と実機試験に分けて確認する。
