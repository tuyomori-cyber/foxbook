---
relation: REL-AST-TST-001
participants: [foxbook-speech, THE-SESSION-TOOLS]
status: experimental
updated: 2026-11-19
---

# IF-AST-TST-001: 音声管理拡張 → THE SESSION TOOLS（実験）

## 目的と範囲

共通音声アシスタントの第2段階として、独立したFirefox拡張からTHE SESSION TOOLSが同梱するJSON定義を取得し、限定した一操作を要求する。現段階では実験用の操作管理拡張による手動操作のみで、音声認識・語彙の解釈・自動実行は含まない。利用者がFirefoxでBPMが5増えることを確認した。

## 接続と認可

- 送信側: `foxbook-speech/assistant-ui/exchange-probe/manager`、拡張ID `foxbook-exchange-manager@foxbook.example`。このIDは実験用で、正式な管理拡張IDは未決定。
- 受信側: THE SESSION TOOLS、拡張ID `the-session-tools@example.invalid`。`runtime.onMessageExternal`で送信元`sender.id`を検証し、上記以外は`UNAUTHORIZED`を返す。Webページへ操作APIは公開しない。
- Firefoxの拡張間`runtime.sendMessage`を使用する。対象の未導入・無効化・応答不能は送信側の通信エラーとなる。操作要求の再送は自動で行わない。
- 試作は対象IDを管理側に固定登録し、利用者が選択して定義取得を試みる。取得成功はその時点での到達を示すだけで、その後の生存を保証しない。未導入・無効化・応答不能は区別しない。動的発見・登録、正式な認証と許可UIは未決定。
- 定義取得をやり直す際は以前の選択を無効化し、古い応答は採用しない。操作要求中は試作UIで再操作・対象切替を防ぐ。操作の通信失敗時は実行済みか不明と表示し、自動再送しない。試作では5秒で時間切れとし、定義取得失敗時も操作を無効化する。時間切れは対象側の処理を取り消さず、遅延実行し得るため配送保証はない。詳細は[登録と配送の検討](../decisions/音声操作対象の登録と配送_検討.md)を参照。

## 要求と応答

要求の`version`は数値`1`。要求ごとに示したキー以外を受け取らず、未対応操作・追加引数・不正な形式には`{ "ok": false, "error": "INVALID_REQUEST" }`を返す。返却された定義や結果は対象アプリ自身が所有する。

### 定義取得

要求: `{ "version": 1, "type": "getCommands" }`

成功時は`{ "ok": true, "definition": ... }`を返す。定義はTHE SESSION TOOLSに同梱した`extension/voice-commands.json`を読み込み、`version`、`appId`、名前・別名、操作`tempo.increase.small`の識別子・名称・発話例を含む。取得失敗は`DEFINITION_UNAVAILABLE`を返す。定義取得そのものはメトロノームを操作せず、対象タブの前面状態を要求しない。

### テンポを5上げる

要求: `{ "version": 1, "type": "execute", "commandId": "tempo.increase.small" }`

操作可能なTHE SESSION TOOLSのタブがフォーカスされた非最小化ウィンドウでアクティブと判定される場合に限り、既存のBPM調整処理を呼び、現在の値に5を加える。上限は300 BPM。試作では対象外・非アクティブ時に`TARGET_INACTIVE`を返し、変更しない。既存のオフライン判定上、オフライン画面は再生所有タブとして管理されている場合にアクティブ判定に含まれる。背景・未表示状態の対象へ実行するかは将来の設計事項である。

成功時は`{ "ok": true, "result": { "bpm": 115, "changed": true } }`のように変更後のBPMと変更の有無を返す。既に上限の場合は`changed: false`。異常時は`OPERATION_FAILED`。内部処理・保存・応答の途中で失敗した場合、実際の変更有無は応答だけでは確定できない。送信失敗やタイムアウト後に自動再送すると二重に変更するおそれがあるため、再送・重複排除方式が定まるまで自動再送しない。

## 互換性と検証

- 既存のTHE SESSION TOOLSの画面、従来の音声認識とチューナー、Voice Editorの直接音声APIは変更しない。
- 実験用JSON定義と操作の一部だけが対象であり、再生・停止、BPM個別設定、音量、分割、チューナーの外部操作は未実装。発話例は現行の音声認識結果を自動的に解釈することを意味しない。
- 自動試験: 定義取得、許可外ID・追加キー・未知操作の拒否、アクティブ時のBPM +5、非アクティブ拒否、上限を検証。利用者がFirefoxで定義取得後のBPM +5を確認し、The Sessionドメインを開いていない場合は失敗したと報告した。失敗時の表示文言は未記録。利用者は対象拡張を無効化した場合に操作ボタンが無効となり接続エラーが表示されること、対象タブを非アクティブにした場合に `操作失敗：TARGET_INACTIVE` が表示されることを確認した。端末・Firefoxバージョン、非アクティブ時のBPM値は未記録。
- 正式版の拡張ID、動作対象、操作の冪等性・要求識別子、再接続・配送の確実性、定義形式の版管理を設計したうえで、必要に応じて別の契約IDを発行する。
