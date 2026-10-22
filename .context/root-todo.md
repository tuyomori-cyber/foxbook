# Auto ToDo Root

> 現在のNow/Nextだけを記載。各プロジェクトの詳細・保留事項は各TODO.mdへ。

## Now

- Done: 単独リポジトリGit、受信バッファ切断時のローカル操作維持、実行設定とGit対象の連動、Commit最終確認の要約・詳細・取消を実装。Host確定時点のステージ済み一覧を使用し、既存Git安全機構を維持。
- Done: ステージ済みファイルを「ステージ済み（解除は未対応）」と明示し、将来の解除機能は安全設計を含む保留事項として記録。
- Pending: Firefox実機でGit操作と受信バッファ、実行設定連動、Commit最終確認を確認。確認後の状態変化時に再確認が要求されることも確認する。

## Next

- `python3 scripts/install_host.py` で更新後のHostを再登録し、FirefoxのFocodex拡張と操作タブを再読み込みして、`git-test` のGit操作、Commit最終確認、受信バッファ、実行設定連動、ステージ済み表示を確認する。詳細はfocodex/TODO.mdを参照。