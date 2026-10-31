---
repository: foxbook-firefox
updated: 2026-10-30
---

# foxbook-firefox 横断管理

## このリポジトリの責務

- Firefox Split Viewの比率をタッチ向けスライダーで保存・適用するAutoConfigを提供する。
- Split View片側の既存タブ切替は見送り・クローズ済み、未実装。

## 正本へのリンク

- [README](../../../foxbook-firefox/README.md)
- [現行仕様 v0.2](../../../foxbook-firefox/specification/foxbook-firefox仕様書v0.2.md)
- [タブ切替仕様案](../../../foxbook-firefox/specification/Split%20Viewタブ切替仕様案.md)
- [TODO](../../../foxbook-firefox/TODO.md)

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-SV-001` | fox-voice-editor、focodex | 提供側 | experimental | [契約](../interfaces/split-view-operation.md) |
| `IF-SV-002` | Split View利用者 | 提供側の検討案 | closed | [検討記録](../interfaces/split-view-operation.md) |
