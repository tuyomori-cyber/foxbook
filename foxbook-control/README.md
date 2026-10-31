# Foxbook Control v0.2

Firefoxの拡張ページから、ユーザー権限のNative Messaging Hostへ固定操作だけを送る端末制御コンポーネントです。任意コマンドや任意パスを受け付けず、拡張はUI、Native Hostは入力検証と固定コマンド実行を担当します。

現行の実装仕様は[仕様書 v0.2](specification/foxbook-control仕様書v0.2.md)、未完了事項は[TODO](TODO.md)、Foxbook全体との関係は[横断管理台帳](../docs/repositories/foxbook-control.md)を参照してください。旧文書は[old/](old/)に保管しています。

## 提供する操作

| 分類 | 操作 |
| --- | --- |
| 状態取得 | システム情報、電池、ネットワーク、音量、輝度、画面の向き |
| 変更 | 音量、輝度、画面回転 |
| 運用 | Native Host更新、Dropbox楽譜同期、Cageログアウト |

音量と輝度はスライダーを離した時だけ変更します。回転は`eDP-1`の`normal`と`90`だけを対象とし、変更前後で状態を確認します。

## 導入と更新

対象はMozilla公式展開版、または通常のRPM／DEB版Firefoxです。Snap／Flatpak版はNative Messaging Host登録の対象外です。

```sh
python3 scripts/install_host.py --firefox /absolute/path/to/firefox
```

拡張は開発中は`about:debugging`から`extension/manifest.json`を一時読み込みします。初回登録後、制御ページの「Hostを更新」は保存済みのインストーラーとFirefoxパスを使ってHostを再配置します。拡張側を変更した場合は`about:debugging`から再読み込みします。

## 環境依存の操作

- 電池：`/sys/class/power_supply`のBattery種別だけを読む。
- ネットワーク：NetworkManagerの`nmcli`が必要。
- 音量：WirePlumberの`wpctl`が必要。
- 輝度：`brightnessctl`とバックライト変更権限が必要。Hostは権限昇格しない。
- 回転：Cage／Wayland環境の`wlr-randr`が必要。
- Cageログアウト：`FOXBOOK_CAGE_SESSION=1`がある場合だけ実行する。
- 楽譜同期：`~/bin/sync-score.sh`が実行可能である必要がある。待機上限は15分。

## Split View

Split ViewのAutoConfigは[foxbook-firefox](../../foxbook-firefox/README.md)が正本です。横断上の契約は[`IF-SV-001`](../docs/interfaces/split-view-operation.md)を参照してください。このリポジトリの`experiments/splitview-autoconfig/`は移設前の実験コードです。

## テスト

```sh
python3 -m unittest discover -s tests -v
node --test tests/test_control.cjs
```

Python単体試験はNative Hostとインストーラーを、JavaScript試験は音量・輝度・回転UIの6シナリオをモックで検証します。テストは実際のシステム操作を行いません。
