# Foxbook Control 仕様書 v0.2

- 文書バージョン：0.2
- 作成日：2026-10-26
- 状態：現行実装ベース
- 対象：Firefox拡張、Python Native Messaging Host、ユーザー単位インストーラー

旧v0.1の構想・開発計画は[old/foxbook-control-spec-v0.1.md](../old/foxbook-control-spec-v0.1.md)に保管する。

## 1. 目的と構成

Firefoxの拡張ページを端末操作の入口とし、Native Messaging経由でユーザー権限の固定操作を実行する。拡張は表示と要求送信、Hostは要求検証・固定コマンド実行・結果返却を担う。

```text
Firefox 拡張ページ
  └─ Native Messaging
       └─ foxbook_control Host
            └─ 固定のOSコマンド／sysfs読取
```

拡張IDは`foxbook-control@foxbook.example`、Host名は`foxbook_control`とする。

## 2. 通信契約

要求は`action`を持つJSONオブジェクトである。通常の状態取得・操作要求は`{"action":"…"}`だけを受け付ける。`set_volume`は`volume`、`set_brightness`は`brightness`を追加し、いずれも整数範囲を厳格に検証する。

成功応答は`{"success":true,"output":"…","error":null}`、失敗応答は`{"success":false,"output":"","error":{"code":"…","message":"…"}}`とする。Hostに接続できない、またはUI側の10秒待機期限を超えた場合は、拡張が`HOST_UNAVAILABLE`として表示する。

失敗コードは`INVALID_REQUEST`、`UNKNOWN_ACTION`、`COMMAND_FAILED`、`PERMISSION_DENIED`、`TIMEOUT`、`INTERNAL_ERROR`を用いる。

## 3. 許可アクション

| action | 処理 | 入力制約 |
| --- | --- | --- |
| `system_info` | `/usr/bin/uname -a` | 追加入力なし |
| `battery_status` | `/sys/class/power_supply`のBattery読取 | 追加入力なし |
| `network_status` | 固定`nmcli device status` | 追加入力なし |
| `audio_status` | 固定`wpctl get-volume` | 追加入力なし |
| `set_volume` | 固定sinkの`wpctl set-volume` | `volume`: 0〜100の整数 |
| `brightness_status` | 固定`brightnessctl … info` | 追加入力なし |
| `set_brightness` | 固定`brightnessctl … set` | `brightness`: 1〜100の整数 |
| `rotation_status` | `wlr-randr`で`eDP-1`を読取 | 追加入力なし |
| `toggle_rotation` | `eDP-1`を`normal`／`90`へ切替後に再読取 | 追加入力なし |
| `sync_score` | `~/bin/sync-score.sh`だけを起動 | 追加入力なし |
| `update_host` | 保存済みインストーラーを再実行 | 追加入力なし |
| `cage_logout` | 呼出元ログインセッションを終了 | `FOXBOOK_CAGE_SESSION=1`が必須 |

通常のコマンド上限は5秒、`update_host`は30秒、`sync_score`は900秒とする。同期は別プロセスグループで実行し、時間切れ時は子プロセス群も終了する。

## 4. UI

制御ページはツールバーアクションから新規タブで開く。起動時に音量、輝度、画面の向きを順に取得する。スライダーは入力中は表示だけを変え、`change`時に1回だけ変更要求を送る。Hostの実測値を再表示し、失敗時は直前の確認済み値へ戻す。

回転は取得済みの`normal`または`90`だけで有効にする。変更中の重複操作を防ぎ、失敗後は「向きを再取得」が成功するまで無効にする。Cageログアウトは確認ダイアログを必須とする。

## 5. インストールと更新

インストーラーはMozilla公式展開版、RPM版、Snap移行用でないDEB版を検査対象にできる。Snap／Flatpak、判定不能なFirefoxはファイル変更前に拒否する。

Host本体、更新元情報、Native Messaging定義は一時ファイル・fsync・原子的置換で更新する。Hostは`~/.local/share/foxbook-control/`、定義は`~/.mozilla/native-messaging-hosts/`へ置く。定義の`allowed_extensions`は拡張IDだけを許可する。

## 6. 安全境界

- 任意コマンド、任意引数、任意パス、任意出力先を受け付けない。
- Hostはrootへ昇格しない。
- `cage_logout`は明示環境印なしには実行しない。
- 回転は`eDP-1`だけを対象とし、不明・無効・想定外のtransformでは変更しない。
- UIへコマンドの標準エラーやトレースバックを表示しない。Hostは必要な診断を標準エラーログへ残す。

## 7. 横断関係

Cageとの回転・ログアウト境界は[`IF-CTL-CAGE-001`](../../docs/interfaces/foxbook-control--cage.md)を参照する。Split Viewは`foxbook-firefox`の責務であり、[`IF-SV-001`](../../docs/interfaces/split-view-operation.md)を参照する。

## 8. 検証

Python単体試験はHostの入力検証、固定コマンド、タイムアウト、同期の子プロセス終了、インストーラーの原子的更新を検証する。JavaScript試験は音量・輝度・回転のUI状態遷移を検証する。実機確認と未確認範囲はFoxbookの[検証マトリクス](../../docs/operations/verification-matrix.md)へ記録する。
