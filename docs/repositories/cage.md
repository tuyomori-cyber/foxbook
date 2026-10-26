---
repository: cage
updated: 2026-10-26
---

# cage 横断管理

## このリポジトリの責務

- Foxbook運用に必要なCage／Wayland側の出力管理とセッション条件を提供する。

## 正本へのリンク

- [上流READMEとFoxbook向け案内](../../../cage/README.md)
- [Foxbook改造仕様 v0.1](../../../cage/specification/foxbook-cage仕様書v0.1.md)
- [TODO](../../../cage/TODO.md)

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-CTL-CAGE-001` | foxbook-control | 提供側 | active | [契約](../interfaces/foxbook-control--cage.md) |

## 変更時の影響確認

- タッチ座標補正、出力transform、単一出力前提を変える場合は、foxbook-controlの`eDP-1`回転操作とSurface実機を同じ変更単位で確認する。
- `master`とFoxbook改造`e7e88b1`は別の上流世代にあるため、改造を現行masterへ移植する場合は再実装・ビルド・実機検証を行う。
