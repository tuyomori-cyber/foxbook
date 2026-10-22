# Foxbook Control 現状 ToDo

更新日：2026-10-22

## 現状

- MVPの拡張、Python Native Host、インストーラー、電池・ネットワーク・音量表示、音量・輝度スライダー、楽譜同期ボタンは実装済み。
- Cageの出力管理対応を確認し、`wlr-randr`による現在向きの取得と縦横トグルを既存Native Messaging経由で実装済み。取得失敗・想定外の向きでは変更せず、変更後も確認する。
- XubuntuでMVPとP3表示を確認済み。FedoraのPlasmaとCageでMVPのHost通信を確認済み。
- Surfaceでの輝度取得・変更は2026-10-18に実機確認済み。再確認のToDoにはしない。
- Surfaceで画面回転ボタンによる縦横切替を2026-10-19に実機確認済み。
- ローカル検証の記録はPython単体テスト33件、UIテスト7件成功。
- AMO提出用の`/tmp/foxbook-control-amo.zip`は作成・検査済み。「データ収集なし」の宣言を追加済み。

## 未完了

- [ ] Surface / Cageで仮想マウスを使わずに分割ビュー比率を変更する。AutoConfigのツールバースライダーで左側30〜60%を5%刻みで変更・保存する実装を追加済み。XubuntuのMozilla公式Firefox 158ではスライダーDOM生成と自動適用を確認済み。次はXubuntuとFedoraで実操作、Firefox標準のツールバーカスタマイズによる非表示・再表示を確認する。Snap版Firefoxは対象外。導入手順は`experiments/splitview-autoconfig/README.md`を参照。
- [ ] Fedora実機で「Hostを更新」ボタンとP3の電池・ネットワーク・音量表示を確認する。
- [ ] `/tmp/foxbook-control-amo.zip`をAMOで再検証し、結果を確認する。
- [ ] Surfaceの`~/bin/sync-score.sh`で`rclone sync`の失敗が終了コードに反映されるよう修正し、同期成功・失敗時の画面表示を確認する。修正例と手順はREADMEに記載済み。
- [ ] URL入力欄と必要な`about:`ページへの専用導線の要否を決める。現時点では設計案であり未実装。CageでFirefoxの既存ウィンドウへ特別なページを開けるかは未確認。
- [ ] 将来の拡張配布方法、Snap／Flatpak対応、Foxbook独自ホーム画面からの導線を必要になった段階で検討する。

## 参照

- 実装仕様：`specification/foxbook control仕様書ｖ0.1.md`
- 詳細な作業履歴：`.context/turns.jsonl`、Git履歴
- 現在の横断作業：`.context/root-todo.md`
