# API 地図 — Bamboo Data Center 12.1

対象版の公式 swagger（12.1.0、パス 297 件／GET 208 件）に基づく。全文一覧は `endpoints-12.1.md`。

## 共通

- URL は `{BAMBOO_BASE_URL}/rest/api/latest/...`。応答は `Accept: application/json` で JSON（既定は XML）。
- 認証は `Authorization: Bearer <PAT>`。PAT は作成時に権限が固定され、既定は読み取り専用。UI ログインには使えない。
- ページングは `max-results` / `start-index`。一覧レスポンスは `size`（総数）、`max-result`、`start-index` を持ち、コレクションは `plans.plan`、`results.result` のように入れ子になる。
- `expand` クエリで関連エンティティを展開し、往復を減らす。ドット記法で入れ子を指定する（例: 結果一覧で `expand=results.result`、結果詳細で `expand=stages.stage.results.result`）。展開可能な識別子は親エンティティの `expand` 属性に列挙されている。
- スコープ注記: GET でも WRITE 扱いのものがある（権限まわり、依存検索、Docker 構成、デプロイプロジェクトの Specs 等）。読み取り専用 PAT では 403 になり得る。

## 接続確認

| 目的 | エンドポイント |
|---|---|
| インスタンス情報（版など） | `GET /api/latest/info` |
| 認証ユーザー自身 | `GET /api/latest/currentUser` |
| サーバ状態 | `GET /api/latest/server`、`GET /api/latest/status` |

## 台帳

| 目的 | エンドポイント |
|---|---|
| プロジェクト一覧（空プロジェクトの切替可） | `GET /api/latest/project`（`showEmpty`、`expand=projects.project.plans.plan`） |
| 全プラン一覧（見える分のみ） | `GET /api/latest/plan`（`expand=plans.plan`） |
| プロジェクト詳細 | `GET /api/latest/project/{projectKey}` |
| プラン詳細（有効/無効、実行中、平均ビルド時間、説明、ステージ展開） | `GET /api/latest/plan/{projectKey}-{buildKey}` |
| プランブランチ一覧 | `GET /api/latest/plan/{planKey}/branch`、VCS 側は `.../vcsBranches` |
| 共有成果物の定義 | `GET /api/latest/plan/{planKey}/artifact` |
| 変数の定義 | `GET /api/latest/plan/{planKey}/variables`、`GET /api/latest/project/{key}/variables`（値は扱わない。名前とパスワードフラグのみ） |
| プランの依存（親/子） | `GET /api/latest/dependency/search/{planKey}/parent` ほか（WRITE スコープ扱い） |
| リポジトリと利用プランの逆引き | `GET /api/latest/repository`、`GET /api/latest/repository/{id}/usage`、`GET /api/latest/project/{key}/repositories` |

## 状況把握

| 目的 | エンドポイント |
|---|---|
| 全プランの最新結果（横断） | `GET /api/latest/result`（絞り込み: `buildstate`、`lifeCycleState`、`label`、`issueKey`、`favourite`、`includeAllStates`） |
| プロジェクト単位の最新結果 | `GET /api/latest/result/{projectKey}` |
| 実行中ビルド | `GET /api/latest/result?includeAllStates=true&lifeCycleState=InProgress` |
| 実行中ビルドのランタイム状態 | `GET /api/latest/result/status/{planKey}-{buildNumber}` |
| 自分が責任者の壊れたビルド | `GET /rest/responsibility/latest/brokenBuild/myBrokenBuilds` |
| ビルドキュー | `GET /api/latest/queue` |
| デプロイキュー | `GET /api/latest/queue/deployment` |
| エージェント一覧と状態 | `GET /api/latest/agent`（`online` 絞り込み可）、`GET /api/latest/agent/{id}/status` |

## 分析（履歴）

| 目的 | エンドポイント |
|---|---|
| プランの結果履歴 | `GET /api/latest/result/{projectKey}-{buildKey}`（`max-results` / `start-index` で遡る） |
| ブランチの結果履歴 | `GET /api/latest/result/{planKey}/branch/{branchName}` |
| 結果詳細（ステージ／ジョブ結果、成果物、テスト集計、Jira 課題） | `GET /api/latest/result/{planKey}-{buildNumber}`（`expand` に artifacts / stages / testResults / jiraIssues 等） |
| 変更セットから影響ビルドを横断検索 | `GET /api/latest/result/byChangeset/{csid}` |
| プラン要約とレポート定義 | `GET /api/latest/chart/planSummary`、`GET /api/latest/chart/reports` |

## ドシエ（構成の正本）

| 目的 | エンドポイント | 備考 |
|---|---|---|
| プランの Specs エクスポート | `GET /api/latest/plan/{projectKey}-{buildKey}/specs?format=YAML` | READ スコープ。応答は JSON で YAML は `spec.code` に入る（`Accept: text/plain` は 406）。プラン構成の閲覧権限がないと 403 |
| プロジェクトの Specs エクスポート | `GET /api/latest/project/{projectKey}/specs?format=YAML` | READ スコープ |
| デプロイプロジェクトの Specs | `GET /api/latest/deploy/project/{id}/specs` | WRITE スコープ扱い。取れない場合は環境定義の GET で代替 |
| ジョブの Docker 構成 | `GET /api/latest/job/{jobKey}/docker` | WRITE スコープ扱い |
| 環境の Requirement 要約 | `GET /api/latest/deploy/environment/{id}/requirement/summary` | WRITE スコープ扱い |

## デプロイ

| 目的 | エンドポイント |
|---|---|
| デプロイプロジェクトと環境（状態つき） | `GET /api/latest/deploy/dashboard`（大量環境では `.../deploy/dashboard/paginate`）、`GET /api/latest/deploy/project/all` |
| プランに紐づくデプロイプロジェクト | `GET /api/latest/deploy/project/forPlan?planKey=...` |
| 環境のデプロイ履歴（新しい順） | `GET /api/latest/deploy/environment/{environmentId}/results` |
| 個別デプロイ結果 | `GET /api/latest/deploy/result/{deploymentResultId}` |
| バージョンとその元ビルド結果 | `GET /api/latest/deploy/project/{id}/version`、`GET /api/latest/deploy/version/{versionId}/build-result` |
| Jira 課題のデプロイ状況 | `GET /api/latest/deploy/issue-status/{issueKey}` |

## 検索

| 目的 | エンドポイント |
|---|---|
| 横断クイック検索 | `GET /api/latest/quicksearch` |
| 種別ごとの検索 | `GET /api/latest/search/projects`、`.../search/plans`、`.../search/branches`、`.../search/deployments`、`.../search/versions`、`.../search/stages/{planKey}`、`.../search/jobs/{planKey}` |
