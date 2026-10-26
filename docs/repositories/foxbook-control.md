---
repository: foxbook-control
updated: 2026-10-26
---

# foxbook-control 横断管理

## このリポジトリの責務

- Firefoxから固定操作をNative Hostへ送り、端末状態・音量・輝度・回転・Cageログアウトを制御する。

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-CTL-CAGE-001` | cage | 利用側 | active | [契約](../interfaces/foxbook-control--cage.md) |

## 正本へのリンク

- [README](../../../foxbook-control/README.md)
- [現行仕様 v0.2](../../../foxbook-control/specification/foxbook-control仕様書v0.2.md)
- [TODO](../../../foxbook-control/TODO.md)
- [旧文書](../../../foxbook-control/old/)

## 変更時の影響確認

- Cageでの回転・ログアウトの安全境界を変える場合は`IF-CTL-CAGE-001`を更新する。
- Split Viewの実装・導入手順は`foxbook-firefox`の責務であり、ここには複製しない。
