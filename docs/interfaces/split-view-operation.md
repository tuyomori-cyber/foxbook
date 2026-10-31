---
relation: REL-SV-001
participants: [foxbook-firefox, fox-voice-editor, focodex]
status: experimental
updated: 2026-10-30
---

# Firefox Split View運用

## IF-SV-001: 保存済み比率のAutoConfig適用

| 項目 | 内容 |
| --- | --- |
| 提供側 | foxbook-firefox |
| 利用側 | fox-voice-editor、focodexを並べて使うFirefox利用者 |
| 開始条件 | Split View作成、または比率スライダーの操作。 |
| 成功時 | 保存した左ペイン比率を新規Split Viewへ適用する。 |
| 制約 | Firefox本体へAutoConfigを導入できる環境だけが対象。 |

- Firefox更新後の自己診断、タッチ操作、ツールバー再配置、環境差を検証対象とする。

## IF-SV-002: Split View片側の既存タブ切替（見送り）

2026-10-30に検討をクローズした。以下は当時の契約案であり、実装・検証の予定ではない。独立Markdownビューアーを別タブとし、Firefoxの垂直タブで切り替える運用を目指す。

| 項目 | 内容 |
| --- | --- |
| 状態 | closed：見送り、未実装・実機未検証。 |
| 提供側 | foxbook-firefoxの常用AutoConfig。 |
| 利用側 | Split Viewを使うFirefox利用者。特定の拡張には限定しない。 |
| 開始条件 | Firefox標準UIで2タブを分割し、利用者が切替側と同一ウィンドウ内の既存タブを登録する。 |
| 操作 | ツールバーから1タップで登録順に次を表示。2件では交互に切替。設定画面から直接選択も可能。 |
| 成功時 | 指定側だけを登録タブへ差し替え、反対側のタブを維持する。タブは閉じず再読み込みしない。 |
| 境界 | ブラウザーUIから利用者が操作する。拡張間の新たな操作APIやファイル読取権限は含まない。 |

- 登録はウィンドウとSplit View単位、Firefox終了後は再登録する。同じタブの複数Split Viewでの利用は未対応。
- 閉じたタブを登録から外し、残り1件以下では切替を無効にする。別ウィンドウへの移動や対象不明、API未対応時は止めて理由を表示する。
- Firefox内部APIの可用性と、切替中の入力、接続、録音、Codex実行の維持は未確認。片側タブ切替の検証は見送る。
- 開発機のFirefox 158.0.1の静的調査では`replaceTab`が元タブに`gBrowser.removeTab`を呼ぶ。閉鎖確認時やSurfaceでの挙動は未検証。根拠は[検討記録](../../../foxbook-firefox/specification/Split%20Viewタブ切替仕様案.md)を参照する。
- Markdownビューアーは独立した別機能であり、この契約案はその実装を規定しない。
