# Bamboo Specs YAML の読み方

プランの「各タスクが何をしているか」「何をトリガーに実行されるか」「失敗時に誰へ通知されるか」は、通常の REST フィールドでは取れない。これらは Bamboo Specs エクスポートが唯一の取得経路である（トリガーと通知には独立した GET エンドポイントが存在しない。仕様に TriggerDefinition や NotificationRule のスキーマはあるが、取得は Specs 経由のみ）。

## 取得

```bash
python scripts/bamboo.py specs PROJ-PLAN --out plan.yaml
python scripts/bamboo.py specs-outline PROJ-PLAN
```

- エンドポイントは `GET /rest/api/latest/plan/{projectKey}-{buildKey}/specs?format=YAML`（プロジェクト単位は `/project/{projectKey}/specs`）。
- **応答は YAML そのものではなく JSON で、YAML 本体は `spec.code` の文字列に入っている。** `Accept: application/json` で取得すること。`Accept: text/plain` は 406 Not Acceptable になる（実機 12.1 で確認済み。Atlassian 公式の取得例も application/json ＋ `.spec.code` の取り出しである）。ヘルパーは JSON で取得して `spec.code` を取り出し、406 の場合は `Accept: */*` で1回だけ再試行する。API を直接叩く場合も、この形式に合わせること。
- 12.1 では READ スコープだが、プラン構成の閲覧権限がないと 403 になる。その場合は「取得不可」と記録し、通常フィールドで代替する。
- UI で作られたプランでも生成 Specs として出てくる。生成 Specs は冗長で読みにくいことがある。手書き Specs（リポジトリ管理、RSS）かどうかは読みやすさと `repositories` の記述から推測できるが、断定はしない。

## ドキュメントの構造（version: 2 形式）

Specs YAML は概ね次のセクションで構成される。セクション名がそのまま調査の観点になる。

- `plan` — プロジェクトキー、プランキー、名前、説明、有効/無効
- `repositories` — チェックアウトするリポジトリ（名前、スコープ）。複数リポジトリを扱うプランは移行時の設計判断ポイント
- `variables` — プラン変数。パスワード変数は値がマスクされる前提でも、値は転記しない。名前の一覧だけを使う
- `stages` と `jobs` — ステージの並びと、各ジョブの定義。手動ステージかどうかもここに出る
- ジョブ配下の `tasks` — タスクの出現順が実行順。各タスクは種別キー（例: `script`、`checkout`、`maven3`、`junit-parser`、`artifact-download`、`inject-variables` など）で始まる
- ジョブ配下の `requirements` — 実行に必要な Capability（エージェント要件）
- ジョブ配下の `docker` — Docker で実行する場合のイメージ等
- ジョブ配下の `artifacts` — そのジョブが作る成果物（名前、配置場所、共有）
- `triggers` — 実行のきっかけ（後述）
- `notifications` — イベント（例: プラン失敗）と宛先（watchers、メール、コミッター等）
- `plan-branch-management` やブランチ関連の設定 — ブランチプランの作られ方
- `other` / `versioning` 等 — その他のプラン設定、デプロイのバージョン命名に関わる情報

## タスクの読み方

- タスク種別ごとに「何をしているか」を要約する。`script` は本文（scripts）が実体なので、コマンド列を読み、何をビルド・検証・生成しているかを書く。長いスクリプトは全文転記せず、要点と外部依存（呼び出すツール、接続先の種類）を示す。
- `final` フラグのあるタスクは後処理（常時実行）である。失敗判定に効くタスクと、後処理タスクを分けて書く。
- `enabled: false` のタスクは無効化されている。存在と無効であることの両方を記録する。
- 条件付きタスク（conditions）は条件を併記する。アウトラインだけでは条件は分からないので、必ず YAML 本体で確認する。

## トリガーの読み方

`triggers` セクションの代表的な種別:

- `scheduled` — cron 式のスケジュール実行。式をそのまま記録し、実行頻度の解釈を添える
- `polling` / リポジトリポーリング — 一定間隔でリポジトリの変更を検知して実行
- `remote` — リポジトリ側のフック（Webhook 等）から起動
- `manual` — 手動実行のみ
- 他プランの成功に連動する依存起動は、Specs のトリガーではなくプラン依存（dependency）側に現れることがある。ドシエでは依存の GET 結果と合わせて読む

トリガーが複数ある場合はすべて列挙する。「何をトリガーに実行されるか」への回答は、この列挙が正になる。

## 通知の読み方

- イベント種別（プラン失敗、成功、完了など）と宛先の種別を組で記録する。
- 宛先が個人メールアドレス等の場合、報告では個人を特定する形で転記しない（種別と件数にとどめる）。

## 注意

- Specs は「現在の構成」のスナップショットである。変更履歴は含まれない。
- 変数の値、共有クレデンシャルの値は Specs にも結果にも転記しない。移行先では再発行・再登録が正道であり、このスキルは「名前と秘密フラグ」のチェックリストまでを扱う。
- アウトライン（specs-outline）はインデント走査による読み補助である。タスクの条件・引数・順序の確定は YAML 本体で行う。
