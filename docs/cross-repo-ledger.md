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
| `foxbook-speech` | 共有のローカル音声認識Host・音声service | [管理文書](repositories/foxbook-speech.md) |
| `focodex` | Codex実行、Git操作、文章受信バッファ | [管理文書](repositories/focodex.md) |
| `Firefox-On-Screen-Keyboard` | fox-voice-editor向け埋め込みOSK | [管理文書](repositories/firefox-on-screen-keyboard.md) |
| `cage` | Foxbook運用時のCage側変更 | [管理文書](repositories/cage.md) |
| `lato` | ローカルMarkdownのタッチ閲覧用Firefox拡張 | [管理文書](repositories/lato.md) |

## インターフェース索引

契約ID、状態、正本は[interfaces/index.md](interfaces/index.md)を参照する。
複数アプリ向け音声アシスタントの検討は[全体アーキテクチャ 2026-11-19](Foxbook_全体アーキテクチャ_2026-11-19.md)を参照する。構想は未実装であり、既存の音声契約を変更するものではない。
段階別の進め方と完了条件は[音声アシスタント基盤汎用化対応ロードマップ](音声アシスタント基盤汎用化対応_ロードマップ.md)を参照する。
表示不能ページでも管理層が動作するための候補と検証は[実行方式の検討](decisions/音声アシスタント実行方式_検討.md)を参照する。方式は未決定。
Split View片側の汎用タブ切替案`IF-SV-002`は見送り・クローズ。Firefox 158.0.1の`replaceTab`に関する調査記録は保持するが、代替方式の調査・実装は進めない。
今後は独立したローカルMarkdownビューアーを別タブとして実装し、Firefoxの垂直タブで既存Split Viewと切り替える運用を目指す。ビューアーの保存場所・設計・ローカル読取方式とSurface実機での操作性は未決定・未検証。
Focodexの回答を読み取り専用の別画面へ共有し、Markdownビューアーと並べる案は2026-10-30に見送り・クローズした。実装や新しい連携契約はない。回答と仕様書を同時に確認したい要望の実現方式は未決定。

## 運用・検証

- [環境台帳](operations/environments.md)
- [検証マトリクス](operations/verification-matrix.md)
- [設計判断](decisions/)

## 直近の横断運用変更

以下は記録時点の履歴であり、現状・未確認範囲は最新の記録と各正本を参照する。

- 2026-11-21: 起動時の確認で少なくとも一つの対象アプリに操作可能な操作があれば音声受付を開始し、他の対象が利用不可でも利用可能な対象を使う方針。管理UIにWake Wordと各対象の状態を折りたたみ可能に表示する。詳細設計・実装・検証は未完了。[草案](decisions/音声操作要求の状態と照会_草案.md)

- 2026-11-21: 操作対象の状態を確認前・接続できない・接続可能かつ操作不可・操作可能の四分類とし、照会APIを追加する初期方針に合意。起動・再起動時は対象状態を確認してから音声認識の利用を開始する。複数対象の一部が利用不可の場合の開始条件とAPI詳細は未決定。[草案](decisions/音声操作要求の状態と照会_草案.md)

- 2026-11-21: 操作対象の状態・操作可否は対象アプリが管理し、各対象リポジトリでAPI仕様とともに定義する方針。共有する契約は共有インターフェース文書にも記載する。Wake Word等のアシスタント自身の状態はfoxbook-speech内の管理プロセスが扱う。詳細仕様・実装は未決定。[草案](decisions/音声操作要求の状態と照会_草案.md)

- 2026-11-21: 表示不能ページでのシステム操作とTHE SESSION TOOLSの個別操作条件を区別。要求記録を所有プロセスの寿命内に限る初期草案と、操作対象の準備状態の検討を[草案](decisions/音声操作要求の状態と照会_草案.md)に記録。実行単位・復旧方式・状態の定義は未決定。

- 2026-11-21: 音声アシスタントの受付・配送・応答処理を管理画面から独立させ、表示不能ページでも実行基盤が動作する限り受付可能とする設計方針を草案に追加。停止後の復旧を初期検証対象とし、シーケンス図を具体的な利用場面に整理。方式・実装・実機確認は未完了。[草案](decisions/音声操作要求の状態と照会_草案.md)

- 2026-11-21: BPM +5を例とする要求状態・重複排除・状態照会の[草案](decisions/音声操作要求の状態と照会_草案.md)と[シーケンス図](音声操作要求_シーケンス草案.html)を追加。未確定であり、契約・実装変更を意味しない。

- 2026-11-21: 将来の操作対象解除について、解除確定後の新規送信を止め、送信済み操作の取消は保証せず、送信の可否が判別不能なら結果不明として自動再送しない方針に合意。確定点と競合制御は未設計。[登録と配送の検討](decisions/音声操作対象の登録と配送_検討.md)

- 2026-11-21: 初期の操作対象登録はコード内固定値とし、定義応答が不正・不一致なら操作不可としてイベント表示する方針に合意。管理画面を開いている間のみ主要イベントを表示し、将来の保存に備えてイベント情報と表示文を分離する。実行中の解除と送信の競合は未設計。[登録と配送の検討](decisions/音声操作対象の登録と配送_検討.md)

- 2026-11-21: 最初の操作対象をTHE SESSION TOOLSとし、アプリID・Firefox拡張ID・対応APIバージョンを管理側に明示登録、`getCommands`で取得した定義を照合する方針に合意。登録解除後は新規操作を止め、送信済み操作の取消は保証しない。[登録と配送の検討](decisions/音声操作対象の登録と配送_検討.md)を参照。詳細設計・実装は未完了。

- 2026-11-20: foxbook-speech利用登録と音声アシスタント操作対象登録を分け、既存の接続・認証と許可リストを出発点に段階的に整備する方針を[ロードマップ](音声アシスタント基盤汎用化対応_ロードマップ.md)に記録。初期登録は明示的に行い、現行THE SESSION TOOLSの直接利用は移行まで維持する。登録方式の詳細・実装・契約変更は未着手。

- 2026-11-20: ネイティブアプリとFirefox拡張の信頼境界、音声基盤利用と操作対象の許可の分離、接続単位のセッション管理を[ロードマップ](音声アシスタント基盤汎用化対応_ロードマップ.md)の設計方針に記録。現行HostはFirefoxの起動引数の拡張IDを照合するが、同一ユーザーからのservice socket直接接続による詐称は防がない。新たな登録方式・契約・実装は未変更。

- 2026-11-20: 音声操作の正式方式の検討方針として接続可否と操作可否、`execute`と状態照会、backgroundの要求状態管理を分離し、対象の中断時整合性を明文化する方針をロードマップへ追加。THE SESSION TOOLSの一操作で通信・重複排除・状態照会を検証した時点で第3段階に進み、残る汎用基盤を並行整備する。正式契約・実装は未変更。

- 2026-11-19: 利用者がダミー対象の正常・遅延応答・遅延実行・操作無応答・定義取得無応答の5条件をFirefoxで確認。遅延実行送信直後に設定ページへ移動後、約8秒で操作記録が現れた。端末・Firefoxバージョン未記録。[検証マトリクス](operations/verification-matrix.md)

- 2026-11-19: ダミー対象に遅延応答・遅延実行・無応答の試験モードと操作回数・時刻の記録を追加。自動試験済み、Firefox実機確認待ち。[手順](../../foxbook-speech/assistant-ui/exchange-probe/README.md)

- 2026-11-19: 対象の固定登録・定義取得・結果不明時の再試行の検討を追加。試作に5秒の応答期限を設け、操作要求の時間切れ時は結果不明として操作を無効化する。処理の取消・遅延実行の防止は保証しない。自動試験済み、Firefoxの遅延・無応答は未確認。[検討](decisions/音声操作対象の登録と配送_検討.md)

- 2026-11-19: 利用者が対象拡張の無効化時の操作ボタン無効化・接続エラーと、対象タブの非アクティブ時の `TARGET_INACTIVE` 表示を確認。端末・Firefoxバージョン、非アクティブ時のBPM値は未記録。[IF-AST-TST-001](interfaces/assistant--the-session-tools.md)

- 2026-11-19: 管理試作で操作要求中の二重送信を防止し、通信失敗時は実行結果が不明と表示する。固定IDへの定義取得・古い応答の破棄と再送しない方針を実験契約に記録。自動試験済み、Firefox実機確認・動的登録とタイムアウトは未完了。[IF-AST-TST-001](interfaces/assistant--the-session-tools.md)

- 2026-11-19: 管理拡張からTHE SESSION TOOLSの実験APIを呼び出し、BPMが5増えることを利用者が確認。The Sessionドメインを開いていない場合は失敗したと報告。失敗表示の詳細と、対象タブを残した非アクティブ条件は未確認。[IF-AST-TST-001](interfaces/assistant--the-session-tools.md)

- 2026-11-19: 第2段階の実験として、THE SESSION TOOLSにコマンドJSON取得とアクティブ時のBPM +5を公開し、試作管理拡張からの呼び出しに対応した。実験用拡張ID以外・不正形式・対象非アクティブを拒否する。自動試験済み、Firefox実機確認待ち。音声API・マイク制御は変更しない。[IF-AST-TST-001](interfaces/assistant--the-session-tools.md)

- 2026-11-19: 利用者が2つの独立した試作拡張間でJSON定義取得と模擬操作の成功応答を確認。実アプリへの配送と対象不在時は未確認。

- 2026-11-19: ダミーHostの検証を踏まえ、Firefox拡張イベントページでの管理を実行方式の第一候補とした。正式採用と実音声・長時間検証は未完了。第2段階を先行検討するため、2つの独立した試作拡張によるJSON定義取得・模擬操作を追加。正式な操作APIと既存音声契約は変更しない。

- 2026-11-19: IStDXi-M1B6で利用者がダミーNative Host PID 153946の再読み込み前の存在と、再読み込み後の不在を`ps`で確認。別試行で再接続も確認済み。実音声でのマイク回収は未検証。

- 2026-11-19: 検証拡張の再読み込み後、利用者が新しいダミーNative Host PID 152829で再接続可能なことを確認。再読み込み直前の旧Host生存と直後の回収は未確認。

- 2026-11-19: IStDXi-M1B6で検証拡張の再読み込み後、ダミーNative Host PID 145611が`ps`で存在しないことを利用者が確認。再読み込み直前の生存状態・再接続は未記録。

- 2026-11-19: 利用者がダミーNative Hostの300秒後のイベント受信とHost PID 145611の一致を確認。5分を超える継続、拡張再読み込み時の回収・再接続、実音声は未検証。

- 2026-11-19: ダミーNative Hostの試験に、追加通信を行わない5分後のイベント受信モードと、拡張再読み込み時のPID回収・再接続の手順を追加。いずれもFirefox実機確認待ち。実音声サービスやマイクは使用しない。

- 2026-11-19: 専用ダミーNative Hostの90秒後イベントを利用者がFirefoxで受信したと報告（PID 130404）。端末・Firefoxバージョン・他の開いていた画面は未記録。長時間のPort継続、切断・復帰と実音声は未検証。

- 2026-11-19: 表示不可ページ閲覧中の予約イベント実行を利用者が実機確認。次の検証用としてマイクを使わない専用Native Hostと90秒遅延イベントの検証拡張を追加し、Hostの入出力・切断を自動試験した。Firefox実機でのPort継続性は未確認。既存音声Hostの登録・契約は変更しない。

- 2026-11-19: 管理層のページ非依存な実行方式の候補と、MV3背景・Native Messagingの制約を整理。表示不可ページ閲覧中の予約イベント検証用拡張を追加した。Firefox実機、Port継続性、実音声・アプリ配送は未検証で、方式・現行契約は未変更。

- 2026-11-19: 管理層を`foxbook-speech`内の独立構成要素とし、共通UIをContent Scriptで表示する方針を決定。状態文字とドラッグ位置を試す`assistant-ui/`の動作を利用者が確認した。端末・Firefoxバージョンと個別の確認範囲は未記録。実音声サービスには未接続で、表示不可ページでも音声動作を維持する実行形態は未決定。現行音声契約は変更しない。

- 2026-11-19: 共通音声アシスタントへの移行を、UI、操作API、解釈、音声接続、マイク所有権、実機確認の6段階としてロードマップに整理。各段階は未着手で、現行契約は変更しない。

- 2026-11-19: 複数拡張向け共通音声アシスタントの構想を全体アーキテクチャ新版に整理。各拡張のJSON定義、一意候補の実行、複数候補の共通UI・音声選択を検討する。配置・UI・通信・マイク管理は未決定で、現行契約は変更しない。

- 2026-11-18: THE SESSION TOOLSのオフラインチューナー起動、メトロノーム起動・ポップアップ閉鎖後の継続、オンライン復帰後の停止・通常画面切替を利用者が実機確認。停止応答待ち・遅延応答の競合は自動試験済み。端末・Firefoxバージョン、マイク回収のプロセス等による直接確認は未記録。

- 2026-11-18: serviceのウェイクワード既定値を「みらい」に変更。従来のFOXは`FOXBOOK_WAKEWORD=fox`で選択し、「みらい」に必要な導入手順をREADMEと横断契約に明記した。コマンド全種・チューナー・Surfaceの検証は継続。

- 2026-11-18: IStDXi-M1B6で非アクティブ化時とタブ終了時のプロセス一覧を確認し、KWS・`arecord`の残存がないことを確認した。復帰・連続切替および他端末は未確認。

- 2026-11-18: 非アクティブ化時に通常KWSを停止せず、KWS親終了後に子`arecord`が残り得たため、THE SESSION TOOLSで通常KWS停止・録音取消完了後の復帰を追加した。foxbook-speechはKWSを専用プロセスグループで起動し、親子へSIGTERM、2秒後にSIGKILLを送る。通常KWS非アクティブ化とプロセスグループ回収の自動試験済み、連続切替時の実機残存確認は保留。

- 2026-11-18: 「みらい」の導入手順を`foxbook-speech` READMEへ補完した。`foxbook-mirai-test`固定配置、onnx-wakeword／ONNX Runtime、NuGetから同版C APIヘッダーを取得するネイティブ診断のビルド、service切替・FOXへの復帰を一続きにし、IF-TST-SP-001から正本へ参照を追加した。

- 2026-11-17: 今後のウェイクワード検証は「みらい」を優先する。dynabookのFirefoxで発話検出、非アクティブ時の一時停止・復帰、タブ終了時のマイク解放を確認。コードの既定はFOX、みらいはservice環境変数で選択。コマンド全種・チューナー・Surfaceは継続検証。

- 2026-11-17: 対象タブの非アクティブ化・終了時に通常KWSの停止と開始途中の録音取消を行う修正を追加。dynabookで残存KWS・arecordを確認しservice再起動で解放。修正後のFirefox実機確認は未完了。

- 2026-11-17: dynabook試験用に音声serviceで`FOXBOOK_WAKEWORD=mirai`を選択可能にし、THE SESSION TOOLSの待機表示を呼びかけ共通にした。既定はFOX。みらいの単独検出は実機確認済み、Firefox経由とチューナーの実機確認は未完了。

- 2026-11-17: チューナー表示時に測定を自動開始し、所有タブの非表示・ウィンドウ非アクティブ時はserviceの`stop_tuner`でマイクを解放、復帰時に再取得する。競合時は手動再開を待つ。状態遷移の自動試験済み、実機確認待ち。

- 2026-11-17: チューナーで単一のネイティブ入力をKWSと単音ピッチ解析へ渡し、周波数イベントからストロボ風表示・音名・centを表示する機能とA4基準の保存を追加した。合成音で82〜880Hzを検証。実楽器・Surfaceでの追従性と、非アクティブ時の回収は未確認・未実装。

- 2026-11-17: ReazonSpeechでの認識結果に基づき、THE SESSION TOOLSのチューナー起動語を「チューナー」「チューナー起動して」「チューナーを起動して」「十七」とした。いずれも`FOX`検出後の認識結果への完全一致で判定する。

- 2026-11-17: チューナー中の`FOX`単独検出からlease解放とMetronome表示復帰までを実装した。起動直後1.5秒は検出を無視する。音程解析・入力共有は未実装で、音声終了の実機確認もこれから行う。

- 2026-11-17: THE SESSION TOOLSのチューナー仕様を[現行仕様書](../../THE-SESSION-TOOLS/specification/THE%20SESSION%20TOOLS_仕様書v0.2.md)へ統合し、初期段階として既存パネルのTuner表示、`FOX、チューナー`による起動、表示内クリックによる開始・終了、serviceの単一`tuner` lease予約を実装した。PCMキャプチャ・ピッチ解析・単一キャプチャ共有・チューナー中の`FOX`終了は未実装である。`IF-TST-SP-001`をこの初期契約まで更新した。

- 2026-11-17: THE SESSION TOOLS READMEから公開`foxbook-speech`リポジトリへ導線を追加し、Whisper.cpp、ReazonSpeech、Git LFS、ネイティブKWS、Native Host、ユーザーserviceまでを一続きの初回導入手順として整備した。音声操作の依存関係と正本は`foxbook-speech` READMEとする。

- 2026-11-17: `IF-TST-SP-001`をexperimentalとして追加。THE SESSION TOOLSは`FOX`検出後、3秒のReazonSpeech認識で再生・停止、BPM、音量、Divisionを操作できる。ネイティブKWSはserviceが所有し、検出時に停止して録音へマイクを引き継ぎ、結果後に再待機する。Voice Editorの任意録音UI・契約は変更しない。実機で各コマンドは確認済み、切断回収・同時利用・Surfaceは未確認。

- 2026-11-17: wakeword実用化の最初の利用先をTHE SESSION TOOLSに定めた。The Sessionタブ利用中だけ`FOX`を待機し、検出後のReazonSpeech結果が正規化済み「再生」「停止」の場合だけ既存メトロノームを操作する方針。Native Messaging許可、KWSと録音のマイク排他・回収、結果後の再待機、横断APIと実機検証は未実装。

- 2026-11-16: ウェイクワード単独診断でdynabookのFOX検出とテレビ音下5分以上の誤検出なしを確認。Python検出処理のCPU平均3.6%、RSS 68,880KBを記録。次はdynabookでネイティブ版と比較し、登録拡張の利用中だけ監視する運用を検討する。拡張連携・マイク排他・Surface性能は未決定・未検証。

- 2026-11-16: foxbook-speechにsherpa-onnx KWS単独診断を追加した。英語モデルと合成音声でHEY FOXを検出、FOXは1件で未検出。Voice Editor・共有service・APIには未統合で、実マイク検証とマイク排他は未完了。同時録音しない運用とする。

- 2026-11-16: Porcupine無料枠AccessKey終了の開発元回答を確認し、sherpa-onnx英語KWSによる`FOX`の検出実験を候補として調査した。最終選定・日本語発音での精度・Surface負荷は未検証。[検討メモ](../../foxbook-speech/specification/ウェイクワード常時待機検討.md)。

- 2026-11-16: ウェイクワードの検討を開始。最初は軽量検出器の単独実験で検出だけを確認し、Voice Editorの自動録音やマイク共有は未実装・未決定。語句の言語、エンジン、Surface性能も未決定。詳細は[foxbook-speechの検討メモ](../../foxbook-speech/specification/ウェイクワード常時待機検討.md)。

- 2026-11-16: 今回のVoice Editor実機確認を一区切りにし、音声service・二Port・マイク補正の現状、30秒上限、実機確認と保留範囲を各正本と検証記録で整合した。`IF-VE-SP-001`は現行実装としてactiveに統一。Surfaceの共有service測定と補正方式などは各TODOに保留する。

- 2026-11-16: dynabook G83/HSのFirefoxで、30秒上限時の自動認識結果表示、履歴への追加、録音上限の案内、次の録音を実機確認した。

- 2026-11-16: 30秒上限で録音プロセスが正常終了すると音声serviceが`reason: recording_limit`付き停止イベントを送り、自動で変換・認識へ進む。Voice Editorに時間の案内を追加し、自動停止と手動停止の競合を自動試験した。両リポジトリの変更を反映したFirefox実機確認は未完了。

- 2026-11-16: dynabook G83/HSのVoice Editorで録音中にライブラリHostを終了し、自動キャンセルによる`arecord`終了、キャンセルボタン無効化、再読込後の復旧を実機確認した。認識中の切断・結果到着の競合は自動試験で確認済み。

- 2026-11-16: Voice EditorはライブラリPort切断を検知した際、開始・録音・変換・認識中の音声処理を既存の音声Portでキャンセルし、切断検知後の結果を破棄する。切断前に確定した内容は維持する。開始応答前や結果との競合を自動試験で確認し、Firefox実機確認は未完了。

- 2026-11-16: dynabook G83/HSのVoice EditorでReazonSpeech録音中に音声Hostを終了し、Port切断表示、録音操作の無効化、`arecord`終了、ライブラリ利用可能表示と既存内容の表示、再読込後の録音・認識復旧を確認した。認識中の音声Port切断と、録音・認識中のライブラリ切断時の扱いは未確認。

- 2026-11-16: 新端末で録音中キャンセル後のReazonSpeech Workerの5分解放と再読込後の復旧を確認した。変換中・Whisper／ReazonSpeech認識中の取消と接続断は、擬似子プロセスを待機させる自動試験で回収を確認した。Voice Editorのライブラリ切断時の扱いは未完了。

- 2026-11-16: 新端末dynabook G83/HSで共有service単体のWhisper／ReazonSpeech録音・認識とVoice Editorの動作を確認した。録音中取消後のWorker寿命管理を修正し自動試験を追加した。修正後のservice再起動と5分後のWorker解放・再生成の実機確認、Voice Editorのライブラリ切断時の扱いは未完了。

- 2026-11-16: 待機中の二Port切断・復旧と内部状態表示をFirefox実機で確認した。録音中のライブラリHost切断では録音停止ボタンが無効でも録音が続き、手動キャンセル後に`arecord`は終了したがReazonSpeech Workerは5分以上残存した。`foxbook-speech`の取消時Worker解放漏れと、Voice Editorの録音・認識中のライブラリ切断時の扱いは未修正。詳細と次の検証は各リポジトリの`TODO.md`を参照。

- 2026-11-16: Voice Editorで音声service停止中の手入力・保存継続と復旧、ライブラリHost切断時の編集・録音抑止と再読込による復旧を実機確認した。内部状態には音声とライブラリの状態を別々に表示する変更を追加した（表示変更のFirefox確認は未実施）。録音・認識中の切断は未確認。

- 2026-11-16: `foxbook-speech` を新設し、音声認識のNative Messaging Host、録音・認識・マイク排他を担う単一service、共通APIの所有先とした。最初の利用者はfox-voice-editorであり、`IF-VE-SP-001`はdraftで未実装。既存の`fox_voice_editor` Hostは移行後に編集データの保存・読込だけを担う。

- 2026-11-16: `foxbook-speech` のWhisper経路を、録音・WAV変換・CLI認識・取消・一時ファイル回収まで単一serviceへ接続した。socket経由の所有権、録音リース、`stopping → converting → recognizing → result`の順序を擬似コマンドによる自動試験で確認した。systemd --user unit templateと導入スクリプトも追加した。`IF-VE-SP-001`は引き続きdraftで、実機起動・録音、ReazonSpeech、Voice Editorの二Port移行は未完了である。

- 2026-11-16: `foxbook-speech` を実機 `tuyomori-IStDXi-M1B6` でsystemd --user serviceとして起動し、ユーザー専用0600 socketと`foxbook_speech` Native Messaging manifestを確認した。実マイクの録音・認識とFirefox経由の確認は、追加したsocket診断クライアントとVoice Editor移行後に行う。

- 2026-11-16: `foxbook-speech` のsocket診断クライアントで、実機 `tuyomori-IStDXi-M1B6` の5秒録音からWAV変換、Whisper認識、結果返却までを確認した。変換86ms、モデル準備219ms、認識1121msだった。Firefox経由の接続とVoice Editor二Port移行は未確認である。

- 2026-11-16: `foxbook-speech` の実機診断で、`elapsedMs`を含む全計測値の返却を確認した。5秒録音で変換101ms、モデル準備129ms、認識1317ms、停止から結果まで1581msだった。service単体の実機検証は完了し、Firefox経由の接続とVoice Editor二Port移行は未確認である。

- 2026-11-16: `foxbook-speech` にReazonSpeech K2の共有Workerを追加した。Workerは全serviceで一つだけを再利用し、取消時は破棄、最終利用から5分で解放する。`IF-VE-SP-001`の実機ReazonSpeech確認とVoice Editor二Port移行は未完了である。

- 2026-11-16: `foxbook-speech` のReazonSpeech K2を実機 `tuyomori-IStDXi-M1B6` で確認した。5秒録音で変換100ms、認識170ms、停止から結果まで276ms、Worker世代1で結果を返した。Worker再利用・アイドル解放、Firefox経由の接続、Voice Editor二Port移行は未確認である。

- 2026-11-16: `foxbook-speech` のReazonSpeech K2を連続実行し、2回目もWorker世代1のまま認識171ms、停止から結果まで313msで結果を返すことを確認した。Worker再利用の実機確認は完了し、5分アイドル解放、Firefox経由の接続、Voice Editor二Port移行は未確認である。

- 2026-11-16: `foxbook-speech` のReazonSpeech K2を5分以上アイドルにした後、Worker世代2へ再生成され、認識160ms、停止から結果まで264msで結果を返すことを確認した。Worker再利用とアイドル解放の実機検証は完了し、Firefox経由の接続とVoice Editor二Port移行は未確認である。

- 2026-11-16: `fox-voice-editor` を二つのNative Messaging Portへ分離した。`foxbook_speech`はAPI v1の音声操作だけ、`fox_voice_editor`は履歴・定型の読込・保存だけを担う。Voice Editorの既存回帰試験は成功し、Firefox実機での二Port接続確認は未完了である。

- 2026-11-16: Firefox実機の`fox-voice-editor`で二Port構成を確認した。共有音声serviceによるマイク・Whisper準備、認識ブロック追加、履歴表示、保存済み表示が同時に成功した。ReazonSpeech選択と各Port切断時の独立性は未確認である。

- 2026-11-16: Firefox実機の`fox-voice-editor`でReazonSpeech K2を選択した二Port構成も確認した。共有音声serviceによるマイク・ReazonSpeech準備、認識ブロック追加、履歴表示、保存済み表示が成功した。各Port切断時の独立性は未確認である。

- 2026-10-29: `foxbook-firefox` の開発用再読込ボタンが表示されない報告を受け、登録判定とアイコンを修正した。更新時はFirefox終了後、登録済み拡張を一つ指定して `install-dev-addon.sh` を再実行し、合成AutoConfigを更新する。Surfaceでの表示・操作は未確認。
- 2026-10-29: `foxbook-firefox` に `scripts/list-dev-addons.sh` を追加した。`foxbook-control` などの開発用一時拡張について、root管理の登録表を変更せず、登録済みの拡張IDと開発元を `ADDON_ID<TAB>SOURCE_DIR` 形式で確認できる。登録表が不安全な権限・所有者・形式なら読込前に拒否する。
- 2026-10-27: `foxbook-firefox` は、Surface実機で起動エラーになった実行時AutoConfig外部読込を廃止した。`foxbook-control` などの開発用拡張の登録手順・ID・登録表は変えず、登録時にSplit Viewと読込器を単一の主AutoConfigへ静的合成する方式に変更した。Surface実機での合成版再導入とfoxbook-controlの一時読込を確認した。Reload操作は狭い画面でオーバーフローメニューへ入ること、拡張ページは再読込時に閉じることを共有運用とする。
