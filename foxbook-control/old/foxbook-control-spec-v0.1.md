# foxbook control仕様書ｖ0.1

- 文書バージョン：0.1（構想・開発計画）
- 作成日：2026-10-14
- 対象：Foxbook（Fedora 43 / Surface Pro 4 / Cage / Firefox）
- 状態：未実装。記載する構成は設計方針であり、動作保証ではない。

## 1. 目的

Foxbookは、Surface Pro 4をCage上のFirefoxを中心とするタッチ操作専用端末として運用する計画である。Foxbook Controlは、Plasmaなどのデスクトップ環境を常時起動せず、Firefoxの画面からLinuxの基本機能を呼び出すための制御基盤とUIを提供する。

**基本思想：Firefoxは操作画面、Native Hostは橋渡し、Linuxの既存コマンド・サービスが実行本体。** ターミナルエミュレーターを画面に開く必要はない。

## 2. 確定事項・制約

1. ブラウザは当面Firefoxを採用。XubuntuのMVP検証では`~/.local/opt/foxbook-firefox/`に置くMozilla公式バイナリを専用プロファイルで起動し、既存のSnap版は変更しない。Fedora実機ではRPM版Firefoxを使う。Chromium等への変更は現段階では優先しない。
2. Cageの画面回転とタッチ座標については、**現在動作確認できているCage側の修正を維持**する。別方式への置き換えは本計画の対象外。
3. Fedora、Plasma、既存のCage環境は破壊・置換しない。PlasmaとSSHを保守・復旧手段として残す。
4. **開発・仮テストはXubuntuで実施し、Surface実機への移植・統合テストは最終段階**とする。
5. 任意のシェルコマンドをWebページから実行可能にする仕組みにはしない。あらかじめ登録した操作のみ許可する。
6. 専用OSや独自Webエンジンを開発しない。WPE WebKit等は対象外。

## 3. 想定アーキテクチャ

```text
Cage（Surface実機での運用時）
  └─ Firefox
       └─ Foxbook Control 拡張機能・操作UI
            │ Native Messaging（JSON）
            ▼
          Foxbook Native Host（ユーザー権限のローカルプロセス）
            │ 許可済みアクションIDを検証
            ▼
          Linuxのコマンド／サービス
            ├─ uname -a（MVPの初期疎通確認）
            ├─ nmcli（ネットワーク）
            ├─ upower / sysfs（電池情報）
            ├─ wlr-randr（画面回転：Cage環境）
            ├─ 輝度・音量制御ツール
            └─ loginctl / systemctl（セッション終了・電源操作）
```

- Firefox拡張はUIと要求送信を担当する。
- Foxbook Controlの操作UIはツールバーのポップアップではなく拡張ページとする。端末のシステム操作画面として位置づけ、Foxbookの起動画面とは分ける。
- 制御ページは自動表示しない。MVPではポップアップを持たない拡張ツールバーボタンを押したときだけ、通常の拡張ページを新しいタブで開く。ページの表示処理と呼び出し元を分離し、将来Foxbook独自のホーム画面からも開ける構成とする。
- Native HostはPythonで実装し、FirefoxのNative Messagingプロトコルで要求・結果を受け渡す。標準入出力はJSON通信専用とし、デバッグログは標準エラーへ出す。
- MVPの通信は`browser.runtime.sendNativeMessage()`を使い、操作ごとにNative Hostを起動して1件の実行結果を受け取る。継続的な状態監視が必要になった場合に限り、将来`connectNative()`を検討する。
- Native Hostは必要なコマンドを引数配列で直接起動する。シェル解釈を原則介さない。
- 要求・応答のJSON形式を統一し、実行結果は成功／失敗、出力、失敗理由を構造化して拡張へ返す。
- XubuntuとCageで異なる操作（例：画面回転）は環境別の実装・検証を設ける。

### MVPの通信形式

要求：`{"action":"system_info"}`

成功応答：`{"success":true,"output":"Linux ...","error":null}`

失敗応答：`{"success":false,"output":"","error":{"code":"UNKNOWN_ACTION","message":"未登録の操作です"}}`

- MVPの要求JSONには`action`を含める。応答JSONは成功・失敗ともに`success`、`output`、`error`を持つ。
- MVPの`system_info`は固定コマンド`uname -a`だけを実行し、その標準出力を`output`で返す。
- `success`は真偽値、`output`は文字列、`error`は成功時`null`、失敗時は機械判定用の`code`とユーザー向けの`message`を持つオブジェクトとする。調査用の詳細は応答JSONに含めず、ログに記録する。
- Host側の失敗コードは`INVALID_REQUEST`、`UNKNOWN_ACTION`、`COMMAND_FAILED`、`PERMISSION_DENIED`、`TIMEOUT`、`INTERNAL_ERROR`とする。権限不足を明確に判定できる場合だけ`PERMISSION_DENIED`を使い、判別できないコマンド失敗は`COMMAND_FAILED`とする。
- Host起動・接続に失敗して応答JSONを受け取れない場合は、拡張側で`HOST_UNAVAILABLE`として扱い、接続エラーを表示する。
- MVPの`system_info`に対応するコマンド実行時間の上限は5秒とする。超過時は実行中のコマンドを終了し、Hostが`TIMEOUT`の失敗応答を返す。
- 拡張側はHost応答を最大10秒待つ。応答がない場合は待機表示を終え、`HOST_UNAVAILABLE`として応答がない旨を表示する。これは画面側の待機期限であり、Hostプロセスの強制終了を意味しない。後から届いた応答はその操作の表示に反映しない。

## 4. 機能範囲

### 4.1 最優先：通信基盤

- MVPの拡張ページには操作ボタンと実行結果・エラー表示だけを設け、未登録アクションの検証専用ボタンは設けない。
- ツールバーボタンは制御ページを開く入口とし、システム操作や結果表示は拡張ページで行う。
- エラー時は`error.message`を主に表示し、`error.code`を補助的に小さく併記する。コマンドのエラー出力やトレースバックは画面に表示しない。
- Firefox拡張からNative Hostを起動し、要求を送る。
- Native Hostは明示的に許可したアクションに対応する固定コマンドだけを実行する。
- Native Hostが`system_info`に対応する固定コマンド`uname -a`を実行する。
- 実行結果とエラーをFirefoxの画面に返す。
- 操作のホワイトリスト、引数検証、タイムアウト、ログ出力を整える。

### 4.2 Foxbook Controlの操作機能（候補）

| 分野 | 想定操作 | 備考 |
|---|---|---|
| システム情報 | OS・ホスト情報の表示 | 最初のPoC対象 |
| 電池 | 残量・充電状態の表示 | Xubuntuで基本処理を試作 |
| Wi-Fi | 状態確認、スキャン、接続・切断 | 接続時の認証情報の扱いを要設計 |
| 画面 | 回転、明るさ変更 | 輝度取得・変更はbrightnessctlで実装。1〜100%のスライダーを離すと反映。2026-10-18にSurface実機で輝度調整を確認済み。回転操作は未実装 |
| 音量 | 音量取得・変更 | 使用する音声基盤を確認 |
| セッション | Firefox／Cageの終了 | 終了方法を実機で検証 |
| 電源 | シャットダウン・再起動 | 確認画面、権限・polkitの確認が必要 |

### 4.3 仮想キーボード（別フェーズ）

- 未決定事項。候補はWayland側の仮想キーボード、Firefox拡張による画面キーボード、音声入力の併用。
- Firefox拡張のDOM操作だけではアドレスバーなどブラウザUIへ直接入力できない。
- Native Hostから`ydotool`等の仮想入力を利用する案はあるが、**フォーカス制御、uinput権限、Cage上での動作は未検証**。
- Native Messagingの通信基盤を先に完成させ、キーボード実装は独立した課題として扱う。

## 5. セキュリティ・安全設計

- Native Hostは許可済みアクションと実行コマンドの対応表を明示し、許可済みのアクションIDだけ受理する。任意コマンド文字列やシェルスクリプトを受け付けない。
- Firefox拡張IDは`foxbook-control@foxbook.example`に固定し、Native Messagingのホスト定義の`allowed_extensions`にも同じIDを明示する。
- XubuntuでのNative Host定義はユーザー単位の`~/.mozilla/native-messaging-hosts/`に配置する。
- Native Host名は`foxbook_control`とし、定義ファイル名を`foxbook_control.json`に揃える。拡張からもこの名前を指定する。
- Host本体は開発用リポジトリから各端末の`~/.local/share/foxbook-control/`へインストールする。MVPにインストールスクリプトを含め、Host本体の配置、実行権限の設定、Firefox Native Messaging Host定義の生成を行う。
- Host定義の`path`にはインストール先の絶対パスを設定し、開発環境固有のパスをハードコードしない。XubuntuとFedoraで同じインストール手順を使う。
- MVPはサンドボックス外で動作するMozilla公式LinuxバイナリまたはLinuxネイティブパッケージ版Firefoxを対象とし、Snap／Flatpak版Firefoxは対象外とする。共通インストーラーは`--firefox /絶対パス/firefox`を必須引数とし、指定されたFirefoxの存在、実行権限、実体、導入形態を検査する。Snap／Flatpak版または判定不能な場合は理由を表示してエラー終了する。単に`command -v firefox`の結果だけで判定しない。
- Firefoxとインストール元Hostなどの事前検査がすべて成功してから、Host本体の配置・実行権限設定・Host定義の生成を開始する。`--firefox`は検査対象を指定する引数であり、ユーザー単位のNative Messaging Host登録をそのFirefox専用に制限するものではない。
- インストーラーの再実行を許可し、事前検査に成功した場合はNative Host本体とHost定義を更新する。検証用Firefoxのプロファイル、既存のSnap版Firefox、その他のFirefox環境は変更しない。
- 更新時は既存ファイルを先に削除せず、同じ配置先に一時ファイルを作成して内容・権限を検証した後に置き換える。途中失敗では既存の正常な環境をできるだけ維持し、一時ファイルを後片付けする。再実行で不要な重複ファイルを増やさない。
- Xubuntuの検証用FirefoxはMozilla公式配布物のディレクトリ構造を維持して`~/.local/opt/foxbook-firefox/`へ配置し、その中の実行ファイルを専用プロファイル`~/.local/share/foxbook-control/firefox-profile/`で起動する。既存のSnap版Firefoxとそのプロファイルは変更しない。Fedora実機では`/usr/bin/firefox`のRPM版を使う。両環境で同じHostインストール手順を用いる。
- MVPにはXubuntu開発環境専用のFirefox起動スクリプトを含める。スクリプトは公式バイナリの絶対パスを指定し、`-profile`で上記の検証専用プロファイルを指定し、`--no-remote`を付けて既存のSnap版Firefoxと独立して起動する。Fedora実機ではこのスクリプトを使わない。
- MVP開発中の拡張は、Xubuntuの検証専用プロファイルで`about:debugging`から一時読み込みする。Firefox再起動後は再読み込みが必要であり、常用向けの署名・配布方法は後続で決める。
- 権限は通常ユーザーを基本とし、root常駐を避ける。特権操作は既存の権限管理機構で処理する。
- シャットダウン、再起動、Wi-Fi切断など影響の大きい操作には確認を設ける。
- 外部WebサイトからNative Hostの機能を直接呼び出せないよう、拡張側のメッセージ経路を限定する。
- Wi-Fiパスワードなどの秘密情報をログに記録しない。
- コマンド失敗時は終了コードやエラー出力など、開発時に原因を調べられる情報を標準エラーのログに残せる設計とする。秘密情報は記録せず、ユーザー向けの`error.message`には内部詳細やトレースバックを出さない。

## 6. ロードマップ

| 段階 | 環境 | 作業内容 | 完了条件 |
|---|---|---|---|
| **P0** | Xubuntu | 専用起動スクリプトで公式Linuxバイナリを専用プロファイルで起動し、`about:debugging`から一時読み込みする拡張、Python Native Hostの最小構成、共通インストールスクリプトを作成 | スクリプトでHostを配置・登録し、一時読み込みした拡張からNative Messagingで接続できる。非対応の導入形態では理由を表示して終了する |
| **P1** | Xubuntu | `system_info`で`uname -a`を実行し、結果を画面に表示 | 要求→実行→応答の往復成功 |
| **P2** | Xubuntu | 許可アクション表、入力検証、エラー処理、ログを整備し、Native Hostの単体テストを行う | 未登録アクションに対して正常なJSONで`UNKNOWN_ACTION`を返し、OSコマンドを実行しない |
| **P3** | Xubuntu | 電池・ネットワーク・音量等の状態取得を追加 | UIで状態を確認できる |
| **P4** | Xubuntu | Wi-Fi操作、電源操作等の変更系コマンドを追加 | 確認・権限処理を含めて仮テスト完了 |
| **P5** | Xubuntu | タッチ向けFoxbook Control UIを整備 | マウス操作で機能・導線を検証できる |
| **P6** | Xubuntu | 仮想キーボード方式の小規模PoC（必要に応じて） | 制約と採否を判断できる |
| **P7** | Surface / Cage | 拡張・Host・UIを移植し、回転、入力、Wi-Fi、電源などを統合確認 | タッチのみで主要操作が成立し、Plasmaへ戻れる |

※P4以降の機能は必要性に応じて取捨選択する。仮想キーボードはFoxbook Control v0.1の必須完成条件に含めない。

## 7. v0.1の最小完成条件（MVP）

1. XubuntuのFirefoxで、拡張ツールバーボタンからFoxbook Controlの拡張ページを新しいタブで開き、操作ボタンを押せる。制御ページは自動表示しない。
2. Native Hostへ固定アクション`system_info`を送信できる。
3. Native Hostが登録済みのLinuxコマンドを実行する。
4. 実行結果・失敗理由をFirefox内に表示できる。
5. Native Hostの単体テストで未知のアクションを送り、正常なJSON応答で`UNKNOWN_ACTION`が返り、OSコマンドが一切実行されないことを確認できる。テストではモックなどを使い、実際のシステム操作を行わない。
6. インストールスクリプトがHost本体を`~/.local/share/foxbook-control/`へ配置して実行権限を設定し、実際のインストール先の絶対パスを含むFirefox Native Messaging Host定義を生成できる。
7. インストールスクリプトは`--firefox`で絶対パスを必須指定し、存在・実行権限・実体・導入形態を確認する。Snap／Flatpak版または判定不能な場合は理由を表示して終了し、Host本体やHost定義を変更しない。
8. インストールスクリプトを再実行してもHost本体とHost定義が更新され、失敗時には既存の正常な環境ができるだけ維持される。不要な重複ファイルを残さず、Firefox本体や各プロファイルは変更しない。
9. XubuntuではユーザーディレクトリのMozilla公式バイナリを専用プロファイルで起動し、その拡張からNative Messaging Hostへ接続できる。既存のSnap版Firefoxは変更しない。
10. Xubuntu専用の起動スクリプトが公式バイナリの絶対パス、`-profile`、`--no-remote`を使用し、既存のSnap版Firefoxと別プロセス・別プロファイルで起動できる。

この段階ではSurface実機での動作を要求しない。インストール手順はXubuntuとFedoraで共通とし、**通信経路の確立がv0.1の第一目標**。

## 8. 保留事項

- MVP後のFirefox拡張の常用向け署名・配布方法。
- 開発環境のXubuntu 24.04では、現在の`/usr/bin/firefox`がSnap版を起動するラッパーである。MVP検証用バイナリの配置先は`~/.local/opt/foxbook-firefox/`、専用プロファイルの保存先は`~/.local/share/foxbook-control/firefox-profile/`に確定。起動にはXubuntu専用スクリプトで`-profile`と`--no-remote`を指定する。
- Fedora実機のFirefoxは`/usr/bin/firefox`、RPMパッケージ`firefox-157.0-1.fc43.x86_64`。提示された`flatpak list --app | grep -i firefox`には結果がない。
- 2026-10-14にFedora KDE PlasmaとFedora Cageで既存MVPの実機確認が成功。以後の機能追加はXubuntuで進め、追加機能のSurface/Cage確認は別途行う。
- 2026-10-14にXubuntuのFirefox画面でP3の電池・ネットワーク・音量表示を確認。電池のない開発機では「バッテリーが見つかりません。」と表示された。
- 2026-10-18にSurface実機で輝度スライダーによる輝度調整の動作を確認した（ユーザーによる実機確認）。
- 2026-10-14、Wi-Fiの接続先候補表示とパスワード入力の優先度を下げ、拡張を再起動後も利用するための導入方法の検討を先行する方針に変更。
- Fedora Cageで`web-ext run`を起動コマンドに組み込んだ際、Firefoxが起動しないとの報告があった。原因は未確認のため自動読み込みは採用しない。元のFirefox起動引数で`about:debugging`を開く方式に戻し、2026-10-14にCageで起動を確認した。拡張は毎回手動で一時読み込みする。
- 開発時のCageログアウトを実装し、2026-10-14にFedora Cageで成功を確認した。Firefoxウィンドウだけを閉じてもCage画面が黒く残るため、Hostの固定アクション`cage_logout`から`loginctl --no-ask-password terminate-session ""`で呼び出し元のログインセッションを終了する。Cage起動スクリプトが渡す`FOXBOOK_CAGE_SESSION=1`を実行条件とし、画面で確認してから送る。SSHは別セッションとして維持する設計。
- Host登録後の更新は制御ページの確認付き`update_host`アクションから行う。インストーラーは更新元インストーラーと検査対象Firefoxのパスをユーザー領域に記録し、Hostはその固定記録からインストーラーを再実行する。初回登録と既存Hostへの機能導入は端末から行い、更新元リポジトリがない場合はエラーを表示する。
- 将来のSnap／Flatpak版FirefoxとNative Messagingの連携方法。
- 将来のFoxbookホーム画面から制御ページを安全に開く経路。
- 失敗コードごとの具体的なユーザー向けメッセージ。
- Wi-Fi認証情報の入力・保存方法。
- 仮想キーボードとアドレスバーへの入力方法。
- 将来のChromium対応は必要になった場合のみ検討。

## 9. 開発原則

**実機を開発環境にしない。** Xubuntuで作ってテストし、Surfaceには完成に近いものを移植する。既存のCage修正を維持し、PlasmaとSSHによる復旧手段を残す。Foxbookの目標はPlasmaの全機能を再実装することではなく、必要な操作をFirefoxから完結させることである。
