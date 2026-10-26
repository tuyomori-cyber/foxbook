# Firefox分割ビューのタッチ操作回避案

調査・実装日：2026-10-22。対象は既存構成のSurface / Fedora / Cageを想定。

導入と運用の手順は`experiments/splitview-autoconfig/README.md`を正とする。

## 制約と確認結果

- 仮想マウスは起動するとタブレットモードが解除されるとのユーザー報告があり、採用しない。
- [Bug 1998922](https://bugzilla.mozilla.org/show_bug.cgi?id=1998922)はタッチで中央線を移動できない問題。Windowsで再現し、Ubuntuでは再現しなかったという記録がある。Fedora / Cageで同じ原因かは未確定。
- [Bug 2012633](https://bugzilla.mozilla.org/show_bug.cgi?id=2012633)で区切り線のキーボード操作が追加され、Firefox 149で修正済み。フォーカスされた区切り線を左右矢印で動かせる。
- [Mozillaの試験](https://searchfox.org/firefox-main/source/browser/components/tabbrowser/test/browser/tabs/browser_tab_splitview_splitter_keyboard.js)は、左browser → Tab → 区切り線 → Tab → 右browser、および逆方向の移動と左矢印による幅変更を確認している。実際のアプリには入力欄等があるためTab回数を固定できるとは限らない。
- [区切り線の実装](https://raw.githubusercontent.com/mozilla-firefox/firefox/main/layout/xul/nsSplitterFrame.cpp)の取得できた版では矢印1回につき5 CSS px移動する。対象端末の版での確認が必要。
- [標準Tabs API](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/tabs)には分割比率を指定するAPIがない。Native MessagingだけでもFirefox内部のDOMを直接操作できない。
- 既存Firefox-On-Screen-Keyboardのkeyboard.jsはページ内の入力対象へKeyboardEvent等を送る方式。これにTabや矢印ボタンを追加するだけではブラウザーUIの区切り線を操作できない。

## 採用方針：保存済み比率の自動適用

Firefoxツールバーのスライダーで決めた比率を、次回以降のSplit View作成時にも自動適用する。

1. 新しいSplit ViewはFirefox標準の50:50で作られる。
2. 利用者はツールバーのスライダーで左側30〜60%を5%刻みで調整する。
3. 指を離すと比率がFirefoxプロファイル内へ保存される。
4. 次回以降、Split View作成を検出したbrowser chrome用コードが保存済み比率を適用する。
5. 再調整して保存すると保存値を置き換える。

Firefox本体の更新後もプロファイル内の保存値は維持される。

### 権限と安全境界

- browser chromeの内部APIへのアクセスは、専用Firefoxに導入するAutoConfigの特権コードだけに限定する。通常のWebExtension、Focodex、fox-voice-editor、Webページ、Native Hostから呼び出す経路は作らない。
- AutoConfigの起動時処理は例外を捕捉し、Split Viewがない、保存値が不正、Firefox内部APIが変更された場合は何も変更せずFirefoxの標準動作を継続する。起動を失敗させない。
- 保存値はFirefoxプロファイル内の専用設定値とし、許容範囲を検証する。Webページの値、URL、任意のコマンド、任意のJavaScriptを入力として受け付けない。
- Firefox更新でAutoConfig本体が再配置を要しても、プロファイル内の保存値は残る。更新後に内部APIが変わった場合は自動適用を停止し、標準の50:50へフォールバックする。

### 比率変更UIの実装境界

- 通常のWebExtensionのポップアップ、サイドバー、設定ページは、Firefox内部の`gBrowser`、Split Viewパネル、Firefoxプロファイル設定サービスへアクセスできない。そのためfoxbook-control拡張のUIだけで、現在のSplit View比率を直接変更・保存することはできない。
- AutoConfigがFirefoxのbrowser chrome内へスライダーを追加する。スライダーの処理も同じAutoConfig内で実行し、開いているSplit Viewへ適用してから`foxbook.splitview.savedRatio`へ保存する。Webページ・拡張・Native Hostを特権コードへの入口にはしない。

### 検証結果（Xubuntu、2026-10-22）

- Mozilla公式配布版Firefox 158.0を、通常の検証プロファイルとは別の使い捨てプロファイルで起動した。
- AutoConfigがFirefox起動後に2個の`about:blank`タブからSplit Viewを作成し、左パネルの`width`属性と`style.width`を65%へ設定した。
- Firefoxプロファイルに記録した実測比率は`0.650`であり、設定値`0.65`と一致した。AutoConfigから分割比率を直接変更できることを確認した。
- 自己試験中の内部APIエラーは捕捉し、失敗値としてプロファイルへ記録する。Firefoxの起動は継続する。
- 検証後、Firefox本体に一時配置したAutoConfigファイルは削除した。通常のFirefox起動時にこのプローブは読み込まれない。

### 自動適用の最小実装

- AutoConfigはFirefoxの`SplitViewCreated`イベントだけを監視する。
- プロファイル設定`foxbook.splitview.savedRatio`が`0 < ratio < 1`の文字列として存在するときだけ、新しく作られたSplit Viewの左側へ適用する。未設定・不正値では標準の50:50を維持する。
- ツールバーのスライダーが指を離した時点で保存値を更新する。
- XubuntuのFirefox 158で、使い捨てプロファイルに`foxbook.splitview.savedRatio = "0.65"`を設定して検証した。`SplitViewCreated`経由で自動適用された実測比率は`0.650`だった。
- Fedora Plasmaの標準RPM版Firefox 157.0.1でも、同じAutoConfig 2ファイルと文字列設定`foxbook.splitview.savedRatio = "0.65"`を導入し、新規Split Viewが65:35へ自動適用されることを手動確認した。

### 配布形態ごとの導入可否

- Mozilla公式の展開版（tarball）および、Firefox本体の`defaults/pref`と本体直下へ管理者が書き込める通常パッケージ版では利用できる。今回の検証用Firefoxはこの展開版である。
- Fedora Workstationの標準Firefoxは通常RPM版であり、一般的な配置先は`/usr/lib64/firefox/`である。root権限でAutoConfigを配置できるため、この方式の候補になる。Fedora実機では`rpm -q firefox`と`rpm -ql firefox`でRPM版と実際の配置先を確認してから導入・検証する。RPM更新後はAutoConfigの2ファイルが残っていることと、Firefox内部APIの互換性を確認する。
- FedoraでもFlatpak版Firefox、または読み取り専用のrpm-ostree環境では、Firefox本体へ直接AutoConfigを導入できない。これらはSnap版と同様に対象外とする。
- このXubuntuで`/usr/bin/firefox`から起動する通常版はSnap版だった。AutoConfigを置く`/snap/firefox/current/usr/lib/firefox/`は読み取り専用の`squashfs`であり、AutoConfigの恒久的な導入先にできない。Snap更新でもリビジョンが差し替わるため、この方式の対象外とする。
- したがって実運用では、検証済みのMozilla公式展開版をfoxbook用Firefoxとして起動する。プロファイルの`foxbook.splitview.savedRatio`はFirefox本体の更新とは別に残るが、AutoConfigの2ファイルはFirefox本体の更新時に再配置する。

## 代替案

1. **タッチボタンから固定キー列を送る。** Firefox上のボタンからNative Hostを呼び、`wtype`などのWayland仮想キーボードプロトコルでTab / Shift+Tab / 左右矢印を送る。Cageの実装では仮想キーボードはポインター能力を追加しないため、仮想マウスの問題は避けられる見込みである。ただし区切り線のフォーカスを保証できず、日常利用の主方式にはしない。
2. **Firefox内部に比率ボタンを設け、幅を直接変更する。** 保存や自動適用が不要で固定比率だけを切り替えたい場合の方式。
3. **アプリ側で二画面を構成する。** Focodexと音声エディターのUIを共通画面に収め、通常のHTML/CSSとPointer Eventsで比率ボタンやタッチドラッグを実装する。Firefox内部への依存を避けられるが、別拡張間の通信・権限・状態保持・音声録音を再設計する必要がある。別拡張ページをiframeに入れるだけで動くとは扱わない。

固定比率だけでよければuserChrome.cssも候補だが、随時の比率変更には操作経路を別途用意する必要がある。Cageのウィンドウ配置変更ではFirefox内の二つのタブの比率は変えられない。

参考：
- [WebExtensionsの特権・実験API](https://firefox-source-docs.mozilla.org/toolkit/components/extensions/webextensions/basics.html)（通常拡張とは異なり、導入条件の確認が必要）
- [AutoConfigの配置と仕組み](https://support.mozilla.org/en-US/kb/customizing-firefox-using-autoconfig)（ブラウザーUI操作のための特権読み込みは追加検証が必要）
