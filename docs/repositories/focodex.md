---
repository: focodex
updated: 2026-10-26
---

# Focodex 横断管理

## このリポジトリの責務

- Codex実行、Git操作、fox-voice-editorから受け取る文章のFIFO受信バッファを提供する。
- 回答専用の読み取り画面とMarkdownビューアーを第2のSplit Viewに並べる案は、2026-10-30に見送り・クローズ。実装予定には含めない。回答と仕様書の同時確認という要望の扱いは未決定。

## 正本へのリンク

- [README](../../../focodex/README.md)
- [現行仕様 v0.2](../../../focodex/specification/focodex仕様書v0.2.md)
- [TODO](../../../focodex/TODO.md)
- [専用SSH Agent運用](../../../focodex/docs/dedicated-ssh-agent-operations.md)

## 参加インターフェース

| 契約ID | 相手 | 役割 | 状態 | 正本 |
| --- | --- | --- | --- | --- |
| `IF-VE-FD-001` | fox-voice-editor | 受信側 | active | [契約](../interfaces/fox-voice-editor--focodex.md) |
| `IF-VE-FD-002` | fox-voice-editor | 重複判定・再送受信側 | active | [契約](../interfaces/fox-voice-editor--focodex.md) |
| `IF-SV-001` | foxbook-firefox | 利用側 | experimental | [契約](../interfaces/split-view-operation.md) |
