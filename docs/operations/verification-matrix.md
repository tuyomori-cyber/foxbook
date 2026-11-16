# 検証マトリクス

`実装済み`、`自動試験済み`、`実機確認済み`を同じ意味として扱わない。

| 対象 | 契約ID／機能 | 自動試験 | 実機環境 | 最終確認日 | 未確認範囲 |
| --- | --- | --- | --- | --- | --- |
| voice-editor → focodex | `IF-VE-FD-001`, `IF-VE-FD-002` | 送受信契約・受信バッファ試験済み | 未実施 | 2026-10-26 | Firefox実配送、最大3件FIFO、明示再送、受信側操作。 |
| voice-editor → OSK | `IF-VE-OSK-001` | bridge試験2件、OSK ZIP生成・10ファイル内容確認済み | 未実施 | 2026-10-26 | Firefox実画面での埋め込み、文字入力、削除、Enter、閉鎖後の再表示。Surfaceの高DPI・回転。 |
| control → Cage | `IF-CTL-CAGE-001` | コード差分確認済み | 未実施 | 2026-10-26 | Cageビルド、Surface単一出力での各回転角のtouch down／drag、`wlr-randr`経由の連携。 |
| Split View・開発用拡張読込 | `IF-SV-001` | AutoConfig・導入／削除スクリプト構文確認済み | Surface Fedora / Firefox 157.0.1: 静的合成AutoConfigの起動、スライダー表示・比率反映、foxbook-control一時拡張の自動読込・Reload操作を確認 | 2026-10-27 | タッチ操作、保存・再起動復元、ツールバー再配置、開発用読込解除、Firefox更新後の自己診断。Reload後の拡張ページ自動再表示は未実装。 |
| Split View片側タブ切替 | `IF-SV-002`（見送り・クローズ） | 未実装・試験未実施。開発機Firefox 158.0.1の同梱実装の静的確認のみ。 | 未実施 | 2026-10-30（静的調査） | 片側タブ切替の検証は実施しない。 |
| 垂直タブによる運用 | 既存Split Viewと独立Markdownビューアータブの切替構想 | 未実施 | 未実施 | — | Surfaceで垂直タブ操作と画面幅、非表示中のvoice-editor・Focodexの状態保持。ビューアーは未設計・未実装。 |
| foxbook-speech service起動 | `IF-VE-SP-001` のservice・Native Host導入前提 | socket、状態遷移、Whisper・ReazonSpeech擬似実行を自動試験済み | tuyomori-IStDXi-M1B6 / systemd 255: user serviceがactive、`/run/user/1000/foxbook-speech/foxbook-speech.sock`が0600、Native Messaging manifestを確認。Whisperの5秒実マイク録音で変換101ms、モデル準備129ms、認識1317ms、停止から結果まで1581ms。ReazonSpeech K2は初回が変換100ms、認識170ms、停止から結果まで276ms、Worker世代1。2回目も世代1で認識171ms、停止から結果まで313msを確認。 | 2026-11-16 | ReazonSpeech Workerの5分アイドル解放、Firefox経由の接続、再起動後の回復、Surface Pro 4。 |

補足（2026-11-16）: ReazonSpeech K2を5分以上アイドルにした後、Worker世代2へ再生成され、認識160ms、停止から結果まで264msを確認した。Worker再利用とアイドル解放の実機確認は完了した。

補足（2026-11-16）: FirefoxのVoice Editorで二Port構成を確認した。画面上で「マイク準備完了（共有音声service）」、Whisper準備完了、Whisper録音の認識ブロック・履歴・保存済み表示を同時に確認した。ReazonSpeech選択と各Port切断時の独立性は未確認である。
