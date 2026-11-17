---
relation: REL-TST-SP-001
participants: [THE-SESSION-TOOLS, foxbook-speech]
status: experimental
updated: 2026-11-17
---

# IF-TST-SP-001: THE SESSION TOOLS音声操作

THE SESSION TOOLSは`the-session-tools@example.invalid`として`foxbook_speech`へ接続する。The Sessionタブ利用中、serviceはC++ KWSで`FOX`を待機する。検出時はKWSを停止してマイクを解放し、同一sessionのReazonSpeech録音を3秒で停止する。結果後はKWSを再開する。

拡張は認識テキストを許可済みコマンドだけに解釈する。再生・停止、BPM 30〜300、BPM±5、音量0〜150%、音量±10%、Division 4種が対象であり、音色、任意テキスト、The Session以外への操作は対象外である。KWS待機・検出・認識中・障害はLEDで表示する。

serviceはマイクの単一リースを維持する。Voice Editorの手動録音と競合した場合は待機・録音の同時実行を許さず、切断時にはKWS・録音を回収する。Voice EditorのAPIとUIは変更しない。
