# Auto ToDo Root

> このファイルは `llmctx` が `Stop` hook ごとに更新する作業用 ToDo です。
> 本番 ToDo への最終マージは手動で行ってください。

## テーマ

- Foxbook Control v0.1：Xubuntu上でFirefox拡張とNative Hostの通信基盤を確立する
- SurfaceのCage環境で、通常のWebページの入力欄を操作できる仮想キーボードを検証する

## 目的

- Firefoxの画面から許可済みのLinux操作を呼び出す基盤を作る
- まずは`system_info`の要求・実行・応答と、未登録アクションの拒否をMVPとして確認する
- MVP達成後、状態取得機能を拡張し、Fedora環境でもP3の状態表示とHost更新機能を確認する
- SurfaceのCage上で、The SessionやGoogle検索など通常のWebページへ文字を入力できるようにする
- 通常のWebページ向けの仮想キーボードは既存のFirefox拡張を先に評価する。URL移動には拡張ページ内の入力欄、必要な`about:`ページには固定の導線を検討する
- Surfaceのタッチ操作に適したキーボードの表示サイズを確保する。既存の倍率設定で改善できるかを先に確認し、不足する場合はFX OSKのサイズ計算を調整する
- FX OSKの改造版は専用ブランチで管理し、別端末でも利用する場合は自分のGitHub Forkへpushして共有できるようにする

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
- FedoraのFirefoxはRPM版`firefox-157.0-1.fc43.x86_64`と確認済み。MVPのHost通信はKDE PlasmaとCageで確認済み
- XubuntuではMVPに加え、P3の電池・ネットワーク・音量表示を確認済み
- P3の実装とローカル単体テスト16件は完了済み。Fedora実機での「Hostを更新」ボタンとP3の電池・ネットワーク・音量表示の確認が残っている
- Foxbookの主な利用目的は楽譜閲覧。ローカルPDFはFirefoxのファイルメニューから開き、The Session（`thesession.org`）では楽曲検索を行う
- Surface実機のCageとFirefoxでは検索文字列を入力する手段が不足しているため、仮想キーボードなどの入力手段を検討する
- The Session専用のメトロノームは別リポジトリ`/home/tuyomori/project/THE-SESSION-TOOLS/`で実装済み
- The Session以外にGoogle検索などのWeb検索でも入力が必要になるため、仮想キーボードをTHE SESSION TOOLSに同居させる方針は取り下げる
- THE SESSION TOOLSはメトロノーム専用のままとする。仮想キーボードは既存のFX OSK（[Firefox-On-Screen-Keyboard](https://github.com/TravFitz/Firefox-On-Screen-Keyboard)）を候補とし、新リポジトリの作成は実機評価後に判断する
- Firefox拡張のページ内UIはWebページの入力欄を補助できるが、Firefoxのアドレスバーや「ファイルを開く」ダイアログへの入力には対応できない
- Google検索はGoogleの入力欄、任意のURLへの移動は拡張ページ内の入力欄から新しいタブで開く方法で代替できるため、アドレスバーへの直接入力は必須ではない
- URLを見て編集する操作やブラウザの検索候補・履歴候補を使う操作も、現時点ではFoxbookの必須要件ではない
- `about:debugging`などの特別なページは、Firefox拡張の`tabs.create()`では開けない。必要なページに限ってFoxbook Control側に専用ボタンを設ける方法を検討する
- Native HostからFirefoxのコマンドラインで特別なページを開く案もあるが、現在のCage起動構成で既存ウィンドウに開けるかは未確認
- 通常のWebページ向けの仮想キーボードは独立したブラウザ拡張として検討する。Webページ用拡張はFirefoxの設定画面やPDFビューア、ファイル選択画面などでは利用できないため、そこへの文字入力が実際に必要かを別途判断する
- アドレスバーへの直接入力を前提にせず、通常のWebページへの入力と、特別なページを開く導線を分離して設計する
- FX OSKはFirefoxのAMOで配布中。公開版は1.12.0（2021年更新）、GitHubのmasterはManifest V2・1.11.0で版数が異なる。The SessionとGoogle検索で入力・削除・送信を実機評価してから採否を決める
- FX OSKの公開ソースでは、削除はカーソル位置ではなく文字列の末尾を消す実装となっており、Enterによる送信もフォームの構造に依存する。実際の検索欄での挙動を確認する
- AMO公開版とGitHubのmasterでは版数が異なり、コード差分は未確認。まずAMO公開版を評価し、必要が生じた場合にソースとの差分を確認する
- FX OSKでの文字入力は確認済み。入力できなかった原因は未特定であり、The SessionとGoogle検索それぞれでの削除・検索実行は未確認
- FX OSKには画面上の倍率設定があり、初期値は90、設定上限は100。設定値は入力欄からフォーカスを外したときに保存され、表示中のWebページを再読み込みすると反映される
- FX OSKのサイズ計算では設定値を`devicePixelRatio`で割っているため、高DPI環境では設定を100にしても表示サイズの拡大が限定的になる可能性がある。Surfaceで設定100を試した結果、Surface向けの拡大が不足することを確認済み。倍率設定だけでは不十分なため、サイズ計算やキー寸法の調整を検討する
- FX OSKのサイズ調整は、既存プロジェクトの自分用ブランチで行う。別端末でも改造版を使う場合は、自分のGitHub Forkへブランチをpushし、別端末からそのブランチをcloneする。元の作者のリポジトリへ直接pushする前提にはしない
- 改造ブランチ`foxbook-touch`は作成済み。自分のGitHub Forkへのpushと追跡設定も完了し、`mine/foxbook-touch`を追跡する状態になっている。GitHub上のForkは`tuyomori-cyber/Firefox-On-Screen-Keyboard`。サイズ調整後の変更はcommit・pushする
- Forkへのpushは自分のGitHubリポジトリを対象とし、元の作者のリポジトリへ直接pushしない。cloneの削除や作り直しは不要
- 開発ワークスペースには`foxbook-control`、`THE-SESSION-TOOLS`、`Firefox-On-Screen-Keyboard`の3リポジトリを登録している。3リポジトリとも読み取り可能だが、書き込み権限はリポジトリごとに異なり、他の2リポジトリの編集には承認が必要な場合がある

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
- P3：電池・ネットワーク・音量の状態表示を実装済み。Xubuntuで表示を確認済み
- FedoraではKDE PlasmaとCageでMVPのNative Host通信を確認済み。Cageのログアウトも成功済み
- ローカル単体テスト16件成功済み
- Fedora実機で「Hostを更新」ボタンとP3の電池・ネットワーク・音量表示を確認する
- 楽譜閲覧に必要な入力手段を前倒しし、その後の状態取得・変更操作とSurface移植の優先順位を見直す
- 仮想キーボードはOS側への導入や新規開発を前提とせず、既存のFX OSKを先に試す
- Google検索はGoogleページ内の入力欄、URL移動は拡張ページ内の入力欄から新しいタブで開く方法で代替する。アドレスバーへの直接入力を必須要件にしない
- `about:`など必要な特別なページへの導線は、対象を絞ってFoxbook Control側の専用ボタンで代替できるか検討する。Firefoxのコマンドライン経由で開く方法は、現在のCage起動構成での動作が未確認のため必要に応じて検証する
- 通常のWebページ向けキーボード拡張ではFirefoxのアドレスバーや「ファイルを開く」ダイアログを扱えないことを前提に、実際に必要な入力先と対応範囲を整理する
- THE SESSION TOOLSはメトロノーム専用のままとし、仮想キーボードを同居させない
- FX OSKでの文字入力は確認済み。入力できなかった原因は未特定。The SessionとGoogle検索の各入力欄で削除・検索実行を確認し、実用性を評価する
- FX OSKの倍率設定は初期値90、上限100。Surfaceで設定100を試した結果、タッチ操作に十分な大きさにならないことを確認済み。自分用ブランチ`foxbook-touch`で`devicePixelRatio`を使ったサイズ計算やキー寸法を調整する
- FX OSKの改造版は、自分のGitHub Forkへpushする手順を確立済み。`foxbook-touch`ブランチは`tuyomori-cyber/Firefox-On-Screen-Keyboard`へpush済みで、`mine/foxbook-touch`を追跡する設定も完了。サイズ調整後は変更をcommit・pushし、別端末ではForkから改造ブランチをcloneして利用する。元の作者のリポジトリには直接pushしない
- Forkを利用する際は、既存のローカルcloneを削除せず、元の作者のリポジトリを`origin`として維持する。自分のForkを追加remote（例：`mine`）として登録し、`foxbook-touch`ブランチをpushする。ブランチのpushと追跡設定は完了済み
- FX OSKが要件を満たせば新しいリポジトリを作らない。不足がある場合に設定変更、既存プロジェクトへの改善提案、別実装の順に検討する
- 開発ワークスペースの3リポジトリは読み取り可能。`foxbook-control`以外のリポジトリへの変更は、必要な権限・承認を確認してから行う

## 未解決論点

- Fedora実機で「Hostを更新」ボタンが正常に動作するか
- Fedora実機でP3の電池・ネットワーク・音量表示が正常に動作するか
- 将来Foxbook独自のホーム画面から制御ページを安全に開く経路
- 将来のSnap／Flatpak版Firefoxへの対応方法
- MVP後の拡張の署名・配布方法
- 失敗コードごとの具体的な表示文言（実装時に調整）
- SurfaceのCage上で通常のWebページ向けの仮想キーボード拡張を利用できるか
- 独立したキーボード拡張で、The SessionやGoogle検索などのWebページ上の入力欄をどこまで扱えるか
- Firefoxのアドレスバーへの直接入力が必要になる具体的な用途が今後発生するか。現時点ではGoogle検索やURL移動の代替手段があるため必須要件としない
- `about:debugging`など必要な特別なページをFoxbook Controlの専用ボタンから開く方法。拡張APIだけでは開けないページがあり、Native Host経由のコマンドライン起動も現在のCage構成では未確認
- 通常のWebページ向けのキーボード拡張では、Firefoxの設定画面、PDFビューア、ファイル選択画面などへの入力には対応できない。これらの画面で入力が必要かは用途に応じて判断する
- FX OSKのAMO公開版がFirefox 157/158とSurfaceのCage環境で動作するか。GitHub公開ソースとAMO公開版の差分も未確認
- FX OSKの英語配列、カーソル途中での削除、検索送信、画面回転時の表示が用途に合うか
- FX OSKで文字入力できることは確認済みだが、入力できなかった原因は未特定。The SessionとGoogle検索それぞれでの削除・検索実行は未確認
- FX OSKの倍率設定を100にしてもSurface向けの拡大が不足することを確認済み。サイズ計算やキー寸法の調整でタッチ操作に十分な表示サイズを確保できるか
- 高DPI環境で`devicePixelRatio`による縮小が表示サイズに与える影響。倍率設定だけで不十分なため、改造ブランチでサイズ計算やキー寸法を調整する

## 次の一手

1. FX OSKの`foxbook-touch`ブランチでサイズ計算とキー寸法を調整し、Surfaceのタッチ操作に十分な大きさになるか確認する。一時読み込みで確認後、変更をcommit・pushする
2. FX OSKを使い、The SessionとGoogle検索の入力欄で削除・検索実行を確認する。入力できなかった原因の特定は必要に応じて行う
3. Fedora実機で「Hostを更新」ボタンとP3の電池・ネットワーク・音量表示を確認する