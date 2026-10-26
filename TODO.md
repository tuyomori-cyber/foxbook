# Foxbook Control 現状 ToDo

更新日：2026-10-26

## 現状

- Firefox拡張、Python Native Host、ユーザー単位インストーラー、固定アクションの入力検証を実装済み。
- 状態取得、音量・輝度変更、楽譜同期、Native Host更新、Cageログアウト、画面回転を実装済み。
- XubuntuでMVPと電池・ネットワーク・音量表示を確認済み。Surfaceでは輝度変更（2026-10-18）と画面回転（2026-10-19）を確認済み。
- ローカル自動試験はPython 33件とJavaScript UI 6シナリオが成功。

## 未完了

- [ ] Fedora実機で「Hostを更新」と電池・ネットワーク・音量表示を確認する。
- [ ] Surfaceの`~/bin/sync-score.sh`が`rclone sync`失敗時に非0で終了するようにし、同期成功・失敗の画面表示を確認する。
- [ ] AMO提出用アーカイブを再検証し、結果を記録する。
- [ ] URL入力欄と必要な`about:`ページへの導線の要否を決める。
- [ ] 常用向けの拡張配布方法、Snap／Flatpak対応、Foxbookホーム画面からの導線を必要になった時点で設計する。

## 対象外・横断事項

- Split ViewのAutoConfigは`foxbook-firefox`が正本であり、ここでは管理しない。横断契約は[`IF-SV-001`](../foxbook/docs/interfaces/split-view-operation.md)を参照する。
- Cageとの画面回転・ログアウトの境界は[`IF-CTL-CAGE-001`](../foxbook/docs/interfaces/foxbook-control--cage.md)を参照する。

## 参照

- 現行実装仕様：[仕様書 v0.2](specification/foxbook-control仕様書v0.2.md)
- 横断管理：[foxbook-control管理文書](../foxbook/docs/repositories/foxbook-control.md)
- 旧文書：[old/](old/)
