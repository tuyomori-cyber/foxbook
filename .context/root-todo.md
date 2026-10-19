# Auto ToDo Root

> `llmctx` が更新する、現在取り組んでいる作業だけの作業用 ToDo。
> 他プロジェクトの保留事項や完了済みの経緯は各リポジトリの `TODO.md` に置く。正本へのマージは手動。

## Now

- fox-voice-editorの仕様書v0.1.2を作成済み。名称と10件の設計方針を反映した。
- Xubuntuで10秒のマイク録音を16kHz・モノラルPCM WAVへ変換し、whisper.cppの日本語baseモデルで文字起こしできた。CLI実行の実時間は1.757秒（ユーザー報告）。
- Firefox拡張とNative Hostの録音制御試作を実装し、Host単体の試験3件と実コマンド連携を確認済み。Firefox画面でも実マイクから3件の認識結果を確認。初版画面で1.31秒を表示し、計測開始位置を修正してHost処理・モデル読み込みを分けて表示するよう変更済み。
- ブロック編集・ローカル保存・履歴・ピン留め・区切りなしのプレビューとコピーを実装し、状態操作テスト4件が成功。モデル常駐の判断はSurface実測後に行う。
- 録音開始・停止を単一ボタンに統合し、Host状態照会で表示のずれを修正済み。Firefox画面での確認は未実施。
- ブロック編集と履歴を横並びにし、角丸ブロックのタッチ操作・ドラッグ並べ替え・履歴選択による前後挿入を実装済み。Firefox画面での確認は未実施。
- 現行仕様：`../../fox-voice-editor/fox-voice-editor_仕様書_v0.1.2.md`

## Next

1. Firefoxの拡張とタブを再読み込みし、録音ボタン・時間表示・キャンセル・タッチでの並べ替え・履歴選択と挿入・保存と復元・コピーを確認する。
2. タブ終了・接続断時の録音プロセス終了と、Surfaceでの認識時間・メモリ・品質を検証する。

## プロジェクト別の保留事項

- Foxbook Control：`../TODO.md`
- Firefox-On-Screen-Keyboard：`../../Firefox-On-Screen-Keyboard/TODO.md`
- THE SESSION TOOLS：`../../THE-SESSION-TOOLS/TODO.md`
- fox-voice-editorの詳細：`../../fox-voice-editor/TODO.md`
