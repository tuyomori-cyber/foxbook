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
| foxbook-speech service起動 | `IF-VE-SP-001` のservice・Native Host導入前提 | socket、状態遷移、Whisper・ReazonSpeech擬似実行を自動試験済み | tuyomori-IStDXi-M1B6 / systemd 255: user serviceがactive、0600 socket、Native Messaging manifest、両エンジンの実録音・Worker再利用・5分解放を確認。dynabook G83/HS: 両エンジン、Firefox二Port、録音中切断、30秒上限・復旧を確認。 | 2026-11-16 | Surface Pro 4での共有service測定、service再起動後の回復、認識中・保存中の切断実機確認。 |
| THE SESSION TOOLS → speech | `IF-TST-SP-001`・みらい実験 | Python/C++同一PCMスコア、検出イベント、音程合成音、非アクティブと遅延応答を試験済み | dynabook G83/HS / Firefox: 「みらい」発話検出、非アクティブ時の待機停止・復帰、タブ終了時のマイク解放を確認。C++単独診断は毎回検出、CPU約3.4〜3.9%、RSS約37MiB（arecord別）。 | 2026-11-17 | コマンド全種、チューナーでの「みらい」と解放・復帰、長時間誤検出、Surfaceでの検出・負荷・電力、Voice Editorとの競合。 |

補足（2026-11-16）: dynabook G83/HSでWhisper／ReazonSpeechのservice単体認識とVoice Editorの動作を確認。録音中キャンセル後にWorkerが5分で解放され、再読込後に復旧した。変換中と両エンジン認識中の取消・切断は擬似子プロセスによる自動試験で確認し、実機で該当タイミングの取消・切断は未確認。

補足（2026-11-16）: dynabook G83/HSのVoice EditorでReazonSpeech録音中に音声Hostを終了。音声Port切断表示、録音操作の無効化、`arecord`終了、ライブラリ利用可能表示と既存内容の表示、再読込後の録音・認識復旧を確認した。認識中の音声Port切断は実機未確認。

補足（2026-11-16）: dynabook G83/HSのVoice EditorでReazonSpeech録音中にライブラリHostを終了。自動キャンセル後の`arecord`終了とキャンセルボタン無効化、再読込後の復旧を確認した。認識中の切断と結果到着の競合は自動試験で確認し、実機では未確認。

補足（2026-11-16）: dynabook G83/HSのFirefoxで30秒上限到達後、録音結果の自動表示、履歴への追加、上限案内、次の録音を確認した。

補足（2026-11-16）: ReazonSpeech K2を5分以上アイドルにした後、Worker世代2へ再生成され、認識160ms、停止から結果まで264msを確認した。Worker再利用とアイドル解放の実機確認は完了した。

補足（2026-11-16）: FirefoxのVoice Editorで二Port構成と両エンジンを確認した。待機中・録音中のPort切断は上記の範囲で確認済み。認識中・保存中の切断は実機未確認。
