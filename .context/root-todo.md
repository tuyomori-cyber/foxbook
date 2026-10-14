# Auto ToDo Root

> このファイルは `llmctx` が `Stop` hook ごとに更新する作業用 ToDo です。
> 本番 ToDo への最終マージは手動で行ってください。

## テーマ

- Foxbook Control v0.1：Xubuntu上でFirefox拡張とNative Hostの通信基盤を確立する

## 目的

- Firefoxの画面から許可済みのLinux操作を呼び出す基盤を作る
- まずは`system_info`の要求・実行・応答と、未登録アクションの拒否をMVPとして確認する

## 前提認識

- 仕様は`specification/foxbook control仕様書ｖ0.1.md`。MVPの拡張・Python Host・インストーラーは実装済み
- 開発・仮テストはXubuntuで行い、Surface実機とCageでの統合確認は最終段階とする
- 任意のシェルコマンドは受け付けず、Native Hostは通常ユーザー権限で許可済みアクションだけを実行する
- 既存のFedora、Plasma、Cage環境を維持し、PlasmaとSSHを復旧手段として残す
- 本ファイルは`llmctx`が自動更新する作業用ToDoであり、正本へのマージは手動で行う
- Foxbook ControlのUIは起動画面と別の端末システム操作画面とし、ツールバーポップアップではなく拡張ページを使う
- 制御ページは自動表示せず、MVPではポップアップを持たない拡張ツールバーボタンから新しいタブで開く。表示処理と呼び出し元を分離する
- Native Hostの実装言語はPythonとする
- Firefox拡張IDは`foxbook-control@foxbook.example`に固定する
- XubuntuでのNative Host定義は`~/.mozilla/native-messaging-hosts/`にユーザー単位で配置する
- Native Host名は`foxbook_control`とし、定義ファイル名は`foxbook_control.json`とする
- MVPの通信は`browser.runtime.sendNativeMessage()`で操作ごとにHostを起動し、1件の応答を受け取る。継続監視が必要になった場合のみ`connectNative()`を検討する
- Hostは明示したアクションと固定コマンドの対応表だけを実行し、要求・応答JSONで成功・失敗と失敗理由を扱う
- MVPの要求は`{"action":"system_info"}`。応答は`success`（真偽値）、`output`（文字列）、`error`（成功時`null`、失敗時`code`と`message`）で統一し、Host接続失敗は拡張側で表示する
- MVPの`system_info`は固定コマンド`uname -a`だけを実行し、標準出力を返す
- Host側の失敗コードは`INVALID_REQUEST`、`UNKNOWN_ACTION`、`COMMAND_FAILED`、`PERMISSION_DENIED`、`TIMEOUT`、`INTERNAL_ERROR`。権限不足が明確な場合だけ`PERMISSION_DENIED`を使い、接続失敗の`HOST_UNAVAILABLE`は拡張側で扱う
- `error.code`は機械判定用、`error.message`はユーザー向けとし、終了コード・エラー出力などの調査情報は秘密情報を除いて標準エラーログに残せる設計とする
- 制御ページでは`error.message`を主に、`error.code`を小さく併記し、コマンドのエラー出力やトレースバックは表示しない
- MVPの`system_info`コマンド実行上限は5秒。超過時はコマンドを終了し、Hostが`TIMEOUT`を返す
- 拡張側のHost応答待機上限は10秒。超過時は待機表示を終え、`HOST_UNAVAILABLE`を表示する。遅延応答は反映しない
- Host本体は各端末の`~/.local/share/foxbook-control/`へ配置し、MVPのインストールスクリプトで実行権限とHost定義を設定する
- Host定義の`path`はインストール先の絶対パスから生成し、XubuntuとFedoraで同じインストール手順を使う
- MVPはサンドボックス外のMozilla公式Linuxバイナリまたはネイティブパッケージ版Firefoxを対象とし、Snap／Flatpak版は対象外とする
- 共通インストーラーは`--firefox /絶対パス/firefox`を必須とし、存在・実行権限・実体・導入形態を検査する。Snap／Flatpak版と判定不能なものは変更前にエラー終了する
- `--firefox`は検査対象の指定であり、ユーザー単位のHost登録をそのFirefox専用にするものではない。事前検査がすべて成功してからインストールを始める
- インストーラーは再実行可能とし、Host本体と定義のみ更新する。Firefox本体・各プロファイルは変更せず、一時ファイルを検証してから置き換え、途中失敗時の復旧と後片付けを行う
- XubuntuではMozilla公式配布物の構造を維持して`~/.local/opt/foxbook-firefox/`に配置し、専用プロファイル`~/.local/share/foxbook-control/firefox-profile/`で起動する。Snap版とそのプロファイルは変更しない。FedoraではRPM版Firefoxを使う
- MVPにはXubuntu専用のFirefox起動スクリプトを含め、公式バイナリの絶対パス、`-profile`、`--no-remote`を指定する。Fedoraでは使用しない
- MVP開発中の拡張は検証専用プロファイルの`about:debugging`から一時読み込みし、Firefox再起動後は再読み込みする
- FedoraのFirefoxはRPM版`firefox-157.0-1.fc43.x86_64`と確認済み。実機でのHost接続確認はP7で行う

## MVP ゴール

- XubuntuのFirefoxで拡張ツールバーボタンからFoxbook Controlの拡張ページを新しいタブで開き、操作ボタンを押せる
- MVPの画面は操作ボタンと実行結果・エラー表示に絞る
- 制御ページに未登録アクションの検証専用ボタンは設けない
- 固定アクション`system_info`をNative Hostへ送り、登録済みコマンドの結果をFirefox内に表示できる
- Host起動失敗・コマンド失敗などの理由をFirefox内に表示できる
- Native Hostの単体テストで未知アクションへの正常なJSON応答と`UNKNOWN_ACTION`、OSコマンドが一切実行されないことをモックで確認する
- インストールスクリプトでHost本体の配置・実行権限設定・絶対パスを含むHost定義の生成ができる
- インストールスクリプトが`--firefox`の絶対パスを必須とし、存在・実行権限・実体・導入形態を確認する。Snap／Flatpak版と判定不能なものは変更せず理由を表示して終了する
- インストーラーの再実行でHost本体と定義を安全に更新でき、途中失敗で既存の正常な環境をできるだけ維持し、不要な重複ファイルを残さない
- Xubuntuの検証用Firefoxの専用プロファイルからNative Messaging Hostへ接続できる
- Xubuntu専用スクリプトでSnap版と別プロセス・別プロファイルのFirefoxを起動できる

## 非ゴール

- MVP段階での電池・Wi-Fi・音量・回転・電源操作、仮想キーボード、タッチ向け完成UI
- MVP段階でのSurface実機・Cage上の動作保証、Firefox拡張の常用配布
- 正本ToDoへの自動マージ

## 段階的 ToDo

- 仕様上のMVP範囲と検証条件を確定済み
- Xubuntu 24.04の`/usr/bin/firefox`はSnap版の起動ラッパーと確認済み。Mozilla公式Firefox 158.0を`~/.local/opt/foxbook-firefox/`に配置済み
- Xubuntu専用のFirefox起動スクリプトで公式バイナリの絶対パス、`-profile`、`--no-remote`を指定済み。`--version`で起動を確認済み
- 共通インストーラーでFirefoxの事前検査、Host本体・定義の配置、実行権限、再実行、失敗時復旧を実装済み。Snap版拒否時に既存Host・定義のハッシュが変わらないことを確認済み
- P0：専用プロファイルのMozilla Firefoxへ拡張を一時読み込みし、拡張アクションから制御ページの新規タブ表示とNative Host接続を確認済み
- P1：制御ページの`system_info`ボタンから`uname -a`の結果表示まで実機ブラウザーで確認済み
- P2：許可アクション、入力検証、タイムアウト、エラー処理、ログを実装済み。未知アクションの`UNKNOWN_ACTION`応答とコマンド未実行をモック単体テストで確認済み（全9件成功）
- 検証専用プロファイルの`about:debugging`から`extension/manifest.json`を手動で一時読み込み済み。拡張アクションからの新規タブ表示と`system_info`結果をスクリーンショットで確認済み
- MVP達成後にP3以降の状態取得・変更操作とSurface移植の優先順位を決める

## 未解決論点

- 将来Foxbook独自のホーム画面から制御ページを安全に開く経路
- 将来のSnap／Flatpak版Firefoxへの対応方法
- MVP後の拡張の署名・配布方法
- 失敗コードごとの具体的な表示文言（実装時に調整）

## 次の一手

1. P3以降の状態取得・変更操作とSurface移植の優先順位を決める
