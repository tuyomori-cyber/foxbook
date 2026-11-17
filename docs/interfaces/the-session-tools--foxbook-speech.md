---
relation: REL-TST-SP-001
participants: [THE-SESSION-TOOLS, foxbook-speech]
status: experimental
updated: 2026-11-17
---

# IF-TST-SP-001: THE SESSION TOOLS音声操作

THE SESSION TOOLSは`the-session-tools@example.invalid`として`foxbook_speech`へ接続する。The Sessionタブ利用中、serviceはC++ KWSで`FOX`を待機する。検出時はKWSを停止してマイクを解放し、同一sessionのReazonSpeech録音を3秒で停止する。結果後はKWSを再開する。

拡張は認識テキストを許可済みコマンドだけに解釈する。再生・停止、BPM 30〜300、BPM±5、音量0〜150%、音量±10%、Division 4種が対象であり、音色、任意テキスト、The Session以外への操作は対象外である。KWS待機・検出・認識中・障害はLEDで表示する。

serviceは録音とチューナーに共通の単一leaseを保持する。通常KWS待機はまだleaseに含まれず、Voice Editorとの完全なマイク排他・切断回収は未検証である。Voice EditorのAPIとUIは変更しない。

## チューナー起動・終了の初期段階

THE SESSION TOOLSは、`FOX`検出後のReazonSpeech結果が正規化済み「チューナー」「チューナー起動して」「チューナーを起動して」「十七」のいずれかに完全一致した場合に`start_tuner`を送る。serviceは通常待機KWSを停止し、チューナーleaseを保持したまま終了検出用KWSを起動して、所有sessionへ`tuner_started`と`tunerId`を返す。拡張は既存パネルの表示をTunerへ切り替える。

Tuner表示への切替は`start_tuner`を送り、Metronomeへ戻る操作または非アクティブ化は`stop_tuner`（`tunerId`必須）を送る。`start_tuner`はservice全体の単一leaseを`kind: tuner`、`state: tuning`として予約する。同一のネイティブ入力でKWSと単音ピッチ解析を実行し、`tuner_pitch`で`tunerId`と周波数（無音時はnull）だけを通知する。所有タブの復帰時は取得を一度だけ試み、`BUSY`ならユーザーによる再開を待つ。

チューナー中のKWSは起動から1.5秒間の検出を無視し、その後の`FOX`単独検出時に`tuner_wakeword_detected`と`tunerId`を返す。拡張は同じ`tunerId`を確認して`stop_tuner`を送り、Metronomeへ戻る。非アクティブ化時の一時停止・自動再開は実装済み、実機確認待ち。
