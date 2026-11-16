# Auto ToDo Root

> 現在のNow/Nextだけを記載。各プロジェクトの詳細・保留事項は各TODO.mdへ。

## Now

- Done: 共有音声serviceとVoice Editor二Portを実機確認し、待機中の切断・復旧と状態表示を確認した。
- Pending: 録音中のキャンセル後にReazonSpeech Workerが5分経過後も残る。録音中のライブラリ切断では録音が継続する。

## Next

- foxbook-speechのWorker寿命・取消／切断回収を修正・検証する。
- Voice Editorの録音・認識中のライブラリ切断時の扱いを決め、実装・検証する。
