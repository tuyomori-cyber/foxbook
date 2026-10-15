# Foxbook Control v0.1

Firefoxの拡張ページから、ユーザー権限のNative Messaging Hostに固定アクションを送ります。`system_info`に加え、電池（`/sys/class/power_supply`）、ネットワーク（`nmcli device status`）、音量（`wpctl get-volume`）を表示できます。音量は0〜100%のスライダーで調整でき、スライダーを離した時に`wpctl set-volume`を1回実行します。電池がない端末ではその旨を表示します。ネットワーク表示にはNetworkManager、音量表示・変更にはWirePlumberの`wpctl`が必要です。Cage用のログアウトボタンは確認後に呼び出し元のログインセッションを終了します。

## Xubuntu 24.04での検証

1. [Mozilla公式のLinux版Firefox](https://support.mozilla.org/ja/kb/install-firefox-linux)を取得し、配布物のディレクトリ構造を保って`~/.local/opt/foxbook-firefox/`に配置します。`~/.local/opt/foxbook-firefox/firefox`が実行ファイルとなるようにします。既存のSnap版には触れません。
2. リポジトリのルートでHostを登録します。

   ```sh
   python3 scripts/install_host.py --firefox "$HOME/.local/opt/foxbook-firefox/firefox"
   ```

3. 検証用Firefoxを専用プロファイルで起動します。

   ```sh
   ./scripts/run_dev_firefox.sh
   ```

4. そのFirefoxの`about:debugging`で「この Firefox」→「一時的なアドオンを読み込む」を選び、`extension/manifest.json`を指定します。拡張アクションを押すと制御ページが新しいタブで開きます。ボタンがツールバーに見えない場合は拡張メニューから表示・ピン留めします。一時読み込みはFirefox再起動後にやり直します。

初回のHost登録後は、制御ページの「Hostを更新」から更新元リポジトリのHostを再配置できます。インストーラーは使用したインストーラーとFirefoxの絶対パスを`~/.local/share/foxbook-control/install_source.json`へ記録します。更新元リポジトリを移動・削除した場合は、端末からインストーラーを再実行して記録を更新してください。既存のHostには更新操作がないため、この機能を導入する際は一度だけ手順2を端末で実行します。拡張側を変更した場合は`about:debugging`から再読み込みしてください。

2026-10-14にXubuntuのFirefox画面でP3の電池・ネットワーク・音量を確認済みです。音量とネットワークは取得結果を表示し、このXubuntu環境の電池は「バッテリーが見つかりません。」と表示されました。

共通インストーラーは、指定FirefoxがSnap／Flatpak版または導入形態を判定できない場合、ファイルを変更せずに終了します。`--firefox`は検査対象であり、Host登録をそのFirefoxだけに限定するものではありません。

## Fedora実機

同じインストーラーをRPM版Firefoxで実行します。Fedoraではリポジトリが`~/foxbook-control`にある場合、先にそのディレクトリへ移動してください。Xubuntu用の`~/.local/opt/foxbook-firefox/firefox`ではなく、RPM版の`/usr/bin/firefox`を指定します。2026-10-14にFedora KDE PlasmaとFedora Cageで既存MVPの実機確認は両方成功しました。P3の状態取得はXubuntuで確認済みで、Fedoraでの確認はこれからです。

```sh
cd "$HOME/foxbook-control"
grep -n 'update_host\|cage_logout' native_host/foxbook_control.py
python3 scripts/install_host.py --firefox /usr/bin/firefox
```

`grep`に両方の操作が出なければ、Fedora側のリポジトリを更新してからインストーラーを実行してください。

Cageの`~/.local/bin/firefox-kiosk-app`では、スケール・回転・センサー設定を維持し、最後のFirefox起動行を次にします。2026-10-14にCageでFirefoxとデバッグ画面が起動することを確認しました。「この Firefox」から`manifest.json`を一時読み込みすれば、SSHなしで画面上から拡張を検証できます。Firefoxの再起動後は再読み込みが必要です。

```sh
exec firefox --no-remote --new-instance about:debugging
```

ログアウト機能を使う場合は同じスクリプトでFirefox起動行の直前に`export FOXBOOK_CAGE_SESSION=1`を追加します。この印がない環境ではHostがログアウト操作を拒否します。Fedoraでも初回と更新ボタン導入時は上記のインストーラーを端末で実行し、その後は制御ページからHostを更新できます。更新元リポジトリはFedora上にも必要です。

音量スライダーの追加後に`INVALID_REQUEST`が出る場合は、Surface上で`cd "$HOME/foxbook-control" && git pull`を実行し、制御ページの「Hostを更新」を押してください。初回登録が済んでいれば、端末からインストーラーを再実行する必要はありません。拡張も変更されているため、`about:debugging`で再読み込みしてから制御ページを開き直します。更新元の記録がない場合だけ、上記のインストーラーを再実行してください。

Hostの`cage_logout`は固定コマンド`loginctl --no-ask-password terminate-session ""`を実行します。空文字のIDはコマンドを呼び出したログインセッションを指すため、Cageから呼んだ場合はCageのセッションを終了し、別のSSHセッションは対象にしません。2026-10-14にFedora Cageでログアウト成功を確認しました。[systemdのloginctlマニュアル](https://www.freedesktop.org/software/systemd/man/latest/loginctl.html)


## 単体テスト

```sh
python3 -m unittest discover -s tests -v
```

テストはモックを使い、システム操作を実行しません。
