# Foxbook

Foxbookを構成する複数リポジトリの横断文書と共有コンテキストの正本です。

## 共有コンテキスト

`.context/` は `llmctx` による再開用の共有状態です。`root-todo.md` と`session.md`だけをGit管理し、詳細ログ・保留中のturn・自動生成記録はローカルに保持します。

現在この共有コンテキストを参照するリポジトリは、`foxbook-control`、`foxbook-firefox`、`fox-voice-editor`、`focodex`、`Firefox-On-Screen-Keyboard`、`cage`、`lato`です。

各リポジトリ固有の設計・運用・未完了事項は、そのリポジトリ内のREADME、仕様書、TODOを正本とします。このリポジトリには、複数リポジトリにまたがる構成、連携契約、検証状況、文書の正本一覧を置きます。

横断文書の入口は[横断管理台帳](docs/cross-repo-ledger.md)です。
