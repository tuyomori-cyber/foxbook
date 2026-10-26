# Foxbook 横断管理台帳

複数のFoxbook関連リポジトリにまたがる構成、連携契約、運用前提、検証状態の索引です。詳細な実装仕様は各リポジトリを正本とし、共有事実は契約IDで管理します。

## 更新規則

- 二つ以上の関連リポジトリ、拡張間契約、共有運用、共通検証条件に影響する変更では、この台帳と該当文書を同じ変更単位で更新する。
- 共有される接続形式・識別子・状態遷移・互換性方針は`interfaces/`を正本とする。各`repositories/`文書には、そのリポジトリ自身の責務と影響範囲を書く。
- 実機検証は、実施日、環境、確認した範囲、未確認範囲を`operations/verification-matrix.md`へ記録する。

## 関連リポジトリ

| リポジトリ | 主な責務 | 管理文書 |
| --- | --- | --- |
| `foxbook-control` | 端末制御用Firefox拡張とNative Host | [管理文書](repositories/foxbook-control.md) |
| `foxbook-firefox` | Firefox Split View用AutoConfig | [管理文書](repositories/foxbook-firefox.md) |
| `fox-voice-editor` | 音声・手入力による文章編集 | [管理文書](repositories/fox-voice-editor.md) |
| `focodex` | Codex実行、Git操作、文章受信バッファ | [管理文書](repositories/focodex.md) |
| `Firefox-On-Screen-Keyboard` | fox-voice-editor向け埋め込みOSK | [管理文書](repositories/firefox-on-screen-keyboard.md) |
| `cage` | Foxbook運用時のCage側変更 | [管理文書](repositories/cage.md) |

## インターフェース索引

契約ID、状態、正本は[interfaces/index.md](interfaces/index.md)を参照する。

## 運用・検証

- [環境台帳](operations/environments.md)
- [検証マトリクス](operations/verification-matrix.md)
- [設計判断](decisions/)
