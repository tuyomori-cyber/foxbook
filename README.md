# Foxbook Control v0.1

Firefoxの拡張ページから、ユーザー権限のNative Messaging Hostに固定アクションを送るMVPです。現時点の操作は`system_info`（`/usr/bin/uname -a`）だけです。

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

共通インストーラーは、指定FirefoxがSnap／Flatpak版または導入形態を判定できない場合、ファイルを変更せずに終了します。`--firefox`は検査対象であり、Host登録をそのFirefoxだけに限定するものではありません。

## Fedora実機への移植時

同じインストーラーをRPM版Firefoxで実行します。Surface/Cageでの統合確認はP7の対象です。

```sh
python3 scripts/install_host.py --firefox /usr/bin/firefox
```

## 単体テスト

```sh
python3 -m unittest discover -s tests -v
```

テストはモックを使い、システム操作を実行しません。
