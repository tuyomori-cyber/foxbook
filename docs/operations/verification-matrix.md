# 検証マトリクス

`実装済み`、`自動試験済み`、`実機確認済み`を同じ意味として扱わない。

| 対象 | 契約ID／機能 | 自動試験 | 実機環境 | 最終確認日 | 未確認範囲 |
| --- | --- | --- | --- | --- | --- |
| voice-editor → focodex | `IF-VE-FD-001`, `IF-VE-FD-002` | 送受信契約・受信バッファ試験済み | 未実施 | 2026-10-26 | Firefox実配送、最大3件FIFO、明示再送、受信側操作。 |
| voice-editor → OSK | `IF-VE-OSK-001` | bridge試験2件、OSK ZIP生成・10ファイル内容確認済み | 未実施 | 2026-10-26 | Firefox実画面での埋め込み、文字入力、削除、Enter、閉鎖後の再表示。Surfaceの高DPI・回転。 |
| control → Cage | `IF-CTL-CAGE-001` | コード差分確認済み | 未実施 | 2026-10-26 | Cageビルド、Surface単一出力での各回転角のtouch down／drag、`wlr-randr`経由の連携。 |
| Split View | `IF-SV-001` | AutoConfig・導入／削除スクリプト構文確認済み | 未実施 | 2026-10-26 | Xubuntu／Surfaceのタッチ操作、保存・再起動復元、ツールバー再配置、Firefox更新後の自己診断。 |
