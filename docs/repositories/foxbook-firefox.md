---
repository: foxbook-firefox
updated: 2026-10-27
---

# foxbook-firefox 横断管理

## このリポジトリの責務

- Firefox Split Viewの比率をタッチ向けスライダーで保存・適用するAutoConfigを提供する。

## 正本へのリンク

- [README](../../../foxbook-firefox/README.md)
- [現行仕様 v0.2](../../../foxbook-firefox/specification/foxbook-firefox仕様書v0.2.md)
- [TODO](../../../foxbook-firefox/TODO.md)

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-SV-001` | fox-voice-editor、focodex | 提供側 | experimental | [契約](../interfaces/split-view-operation.md) |

開発用の`foxbook-control`等を登録する場合も、実行時AutoConfig外部読込ではなく、登録時に単一の主AutoConfigへ静的合成する。拡張ID・登録表・利用側の操作契約は変更しない。
