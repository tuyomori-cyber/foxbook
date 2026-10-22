# Split View 比率スライダー

Firefox Split Viewの左ペイン比率を、Firefoxのナビゲーションツールバーから変更・保存するAutoConfigです。

## 動作

- スライダーは左側30〜60%を5%刻みで選べる。
- ドラッグ中は開いているSplit Viewへ直ちに適用する。
- 指を離すと`foxbook.splitview.savedRatio`へ文字列として保存する。
- 次に作るSplit Viewにも保存済み比率を自動適用する。未設定時はFirefox標準の50:50のままにする。
- Webページ、通常拡張、Native Hostから特権コードを呼ぶ経路はない。

## 導入

Firefoxを完全に終了してから、次の2ファイルだけを配置する。`selftest-user.js`は使い捨て試験専用であり、導入しない。

| このディレクトリのファイル | Firefox内の配置先 |
| --- | --- |
| `foxbook-splitview-autoconfig.js` | `defaults/pref/foxbook-splitview-autoconfig.js` |
| `foxbook-splitview.cfg` | `foxbook-splitview.cfg` |

### XubuntuのMozilla公式展開版

```bash
cd ~/project/foxbook-control
install -m 0644 experiments/splitview-autoconfig/foxbook-splitview-autoconfig.js \
  ~/.local/opt/foxbook-firefox/defaults/pref/foxbook-splitview-autoconfig.js
install -m 0644 experiments/splitview-autoconfig/foxbook-splitview.cfg \
  ~/.local/opt/foxbook-firefox/foxbook-splitview.cfg
```

### Fedoraの標準RPM版

```bash
cd ~/project/foxbook-control
sudo install -m 0644 experiments/splitview-autoconfig/foxbook-splitview-autoconfig.js \
  /usr/lib64/firefox/defaults/pref/foxbook-splitview-autoconfig.js
sudo install -m 0644 experiments/splitview-autoconfig/foxbook-splitview.cfg \
  /usr/lib64/firefox/foxbook-splitview.cfg
sudo restorecon -v /usr/lib64/firefox/defaults/pref/foxbook-splitview-autoconfig.js \
  /usr/lib64/firefox/foxbook-splitview.cfg
```

## 利用と確認

Firefoxを起動すると、ナビゲーションツールバーに`分割 50:50`のスライダーが現れる。Split Viewを開いてスライダーを動かし、左ペイン幅と次に作るSplit Viewの幅が保存値になることを確認する。

Firefox本体の更新後は、上記2ファイルが残っていることとスライダーが動くことを確認する。保存値はプロファイル内にあるため残る。

## 対象外

Xubuntu標準のSnap版、Firefox Flatpak版、読み取り専用のrpm-ostree環境はFirefox本体へAutoConfigを導入できないため対象外。

## 検証記録

- XubuntuのMozilla公式Firefox 158：使い捨てプロファイルでスライダーDOM生成と保存値0.65の自動適用（実測0.650）を確認。
- Fedora Plasmaの標準RPM版Firefox 157.0.1：保存値0.65が新規Split Viewへ65:35で自動適用されることを手動確認。
