---
name: bamboo-dc-analysis
description: Bamboo Data Center（12.1）の REST API を読み取り専用で使い、プロジェクト／プランの棚卸し、最新結果の横断確認、失敗傾向や所要時間の履歴分析、プラン内のタスク構成とトリガーの調査を行うときに使う。Web 画面を行ったり来たりせずに状況を把握したいとき、Bamboo から GitHub Actions / Bitbucket Pipelines への移行調査の材料を集めるときに使う。
metadata:
  version: "1.2.2"
---

# Bamboo Data Center 調査・分析

Bamboo Data Center 12.1 に対して REST API（GET のみ）で調査と分析を行う手順。同梱の `scripts/bamboo.py`（Python 標準ライブラリのみ）を使う。

## 安全と前提

- 書き込みは一切しない。使うのは HTTP GET のみ。ビルドやデプロイの実行、プランの変更・削除はこのスキルの対象外。
- 接続情報は環境変数からのみ読む。`BAMBOO_BASE_URL`（Bamboo のルート URL。コンテキストパスを含む、末尾に `/rest` は付けない。末尾のスラッシュはあってもなくてもよい）と `BAMBOO_PAT`（読み取り専用の Personal Access Token）。
- PAT の値、ベース URL、変数の秘密の値を、チャット・ファイル・コミット・チケットに書かない。変数については「名前とパスワードかどうか」だけを扱い、値は取得しても表示しない。
- 見える範囲は認証ユーザーの READ 権限の範囲だけである。一覧に出ないことは「存在しない」ことと区別できない。報告ではこの前提を落とさない。
- GET でも WRITE スコープ扱いのエンドポイントがある（権限まわり、依存検索、Docker 構成、デプロイプロジェクトの Specs 等）。403 は「権限で見えない」として記録し、推測で補わない。

## 手順 0: 接続確認（必ず最初に行う）

```bash
python scripts/bamboo.py check
```

`/rest/api/latest/info` と `/currentUser` を取得し、「どのインスタンスに、誰として」つないだかを確認してから調査に入る。版が 12.1 系でない場合は、references の API 地図がずれる可能性があることを報告する。

## 調査の進め方（深さで選ぶ）

1. **台帳**（浅く・全件）: `projects` と `plans` でプロジェクト／プランの一覧を作る。以後の情報はすべてプランキー（PROJECT-PLAN）に紐づける。
2. **状況把握**（横断スナップショット）: `latest` で全プランの最新結果、`latest --state Failed` で失敗中プラン、`queue` でビルド／デプロイの詰まり、`deploys` と `deploy-env` で環境ごとの現行バージョンを見る。
3. **分析**（履歴集計）: `history PLANKEY --days 90` で実行回数、成功率、所要時間（平均／中央値／p95）、連続失敗、最終成功日を集計する。集計の定義と限界は `references/analysis-recipes.md` に従う。
4. **ドシエ**（深く・対象プランのみ）: `dossier PLANKEY --out DIR` で、プラン詳細、Specs YAML、ブランチ、成果物、変数名、依存、デプロイ、履歴統計を 1 フォルダに集める。深い情報は対象を絞ってから取る。全プランにドシエを作らない。

コマンドの詳細とエンドポイント対応は `references/api-map.md` を参照。

## タスクとトリガーの調査（中核）

プランの中で「各タスクが何をしているか」「何をトリガーに実行されるか」は、通常の REST フィールドでは取れない。

- タスク単位の構成、トリガー（リポジトリポーリング、スケジュール、手動、他プラン依存など）、通知には独立した GET エンドポイントが存在しない。唯一の取得経路は Bamboo Specs エクスポートである。
- `specs PLANKEY --out plan.yaml` で YAML を取得し、`specs-outline PLANKEY` のアウトライン（トリガー、通知、ジョブごとのタスク種別の出現順）を読みの入口にする。条件・引数・スクリプト本文は YAML 本体で確認する。
- 読み方は `references/specs-guide.md` に従う。UI で作られたプランでも生成 Specs として出てくるが、手書き Specs と生成 Specs では読みやすさが違う点を報告に注記する。
- Specs が 403 の場合は「プラン構成の閲覧権限がないため取得不可」と記録し、通常フィールド（ステージ／ジョブ名）で代替できる範囲だけを報告する。
- Specs の応答は JSON 形式で、YAML 本体は `spec.code` に入っている。`Accept: text/plain` では 406 になるため、Specs の取得は必ずヘルパー経由で行い、API を直接叩かない。取得に失敗した場合は、ヘルパーのエラー文（HTTP ステータスと応答本文の抜粋を含む）を要約せず、そのまま報告に含める。

## 分析と報告の約束

- 集計には必ず「期間、取得できた件数、打ち切りの有無」を添える。ページング上限で打ち切った場合は、その旨を明記して結論の強さを落とす。
- Expiry で削除された古い結果は API でも戻らない。「長く成功していない」等の判定は、残っている履歴の範囲での判定であると注記する。
- ビルドログ全文を返すエンドポイントはない。失敗の内訳は結果詳細（ステージ／ジョブ結果、テスト集計、成果物）までが範囲であり、ログ本文が必要な場合は Web 画面への案内にとどめる。
- 失敗傾向は「プラン単位の成功率と連続失敗」「所要時間の中央値と p95 の推移」「長期未実行プラン」の 3 点を基本形とし、憶測で原因を断定しない。原因に触れる場合は、結果詳細や Specs のどの記述に基づくかを併記する。

## ヘルパーのコマンド

```bash
python scripts/bamboo.py check
python scripts/bamboo.py projects
python scripts/bamboo.py plans
python scripts/bamboo.py plan PROJ-PLAN
python scripts/bamboo.py latest [--state Failed] [--in-progress]
python scripts/bamboo.py results PROJ-PLAN
python scripts/bamboo.py result PROJ-PLAN-JOB1-123
python scripts/bamboo.py history PROJ-PLAN [--days 90]
python scripts/bamboo.py branches PROJ-PLAN
python scripts/bamboo.py variables PROJ-PLAN
python scripts/bamboo.py deploys
python scripts/bamboo.py deploy-env ENVIRONMENT_ID
python scripts/bamboo.py queue
python scripts/bamboo.py specs PROJ-PLAN [--out plan.yaml]
python scripts/bamboo.py specs-outline PROJ-PLAN
python scripts/bamboo.py dossier PROJ-PLAN --out DIR [--days 90]
```

## References

- `references/api-map.md` — モード別の主要エンドポイント、expand とページングの使い方
- `references/specs-guide.md` — Bamboo Specs YAML の読み方（タスク、トリガー、通知、変数、リポジトリ）
- `references/analysis-recipes.md` — 集計の定義、判定基準、限界
- `references/endpoints-12.1.md` — 12.1 の GET 全 208 件（swagger から機械生成）
