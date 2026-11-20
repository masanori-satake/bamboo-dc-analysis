# Bamboo DC Analysis

[![Latest release](https://img.shields.io/github/v/release/masanori-satake/bamboo-dc-analysis?style=flat)](https://github.com/masanori-satake/bamboo-dc-analysis/releases)
[![Sync mirror and release](https://github.com/masanori-satake/bamboo-dc-analysis/actions/workflows/sync-and-release.yml/badge.svg)](https://github.com/masanori-satake/bamboo-dc-analysis/actions/workflows/sync-and-release.yml)

**Atlassian Bamboo Data Center（12.1）** を REST API で読み取り専用に調査・分析する Agent Skill です。GitHub Copilot、Amazon Kiro など、Agent Skills 形式に対応したエージェントから使えます。

Bamboo の Web 画面を何枚も開いて確認していたことを、エージェントへの質問で済ませるためのものです。「いま失敗しているプランはどれ？」「このプランの直近90日の成功率と所要時間の傾向を見せて」「このプランの各タスクは何をしていて、何をトリガーに実行されるの？」と聞けば、API から集めて答えます。

## できること

- **台帳** — 見える範囲のプロジェクト／プラン一覧（有効/無効、実行中、平均ビルド時間）
- **状況把握** — 全プランの最新結果、失敗中プランの抽出、ビルド／デプロイキュー、環境ごとの現行デプロイバージョン
- **履歴分析** — プランごとに期間（既定90日）の実行回数、成功率、所要時間（平均／中央値／p95）、連続失敗、最終成功日、長期未実行プラン
- **ドシエ** — 対象プラン1件について、プラン詳細、Bamboo Specs YAML、ブランチ、成果物、変数名、プラン依存、紐づくデプロイプロジェクト、履歴統計を1フォルダに集める
- **タスクとトリガーの調査** — タスク単位の構成、トリガー、通知には専用の GET エンドポイントがありません。唯一の取得経路である Bamboo Specs エクスポートを読み（トリガー、通知、ジョブごとのタスク種別のアウトライン付き）、「このプランは実際に何をして、何がきっかけで動くのか」に答える

## 安全の考え方

- **GET のみ。** ビルドやデプロイの実行、Bamboo の状態変更は一切しません。
- **認証情報はファイルに残しません。** ヘルパーは `BAMBOO_BASE_URL` と `BAMBOO_PAT` を環境変数からだけ読みます。スキル、リポジトリ、出力のどこにも書きません。
- **秘密は集めません。** 変数は名前とパスワードフラグだけを扱い、値は表示しません。トークンが出力や生成物に含まれることもありません。
- **見える範囲は権限の範囲だけ。** その前提を落とさずに報告します。

## 動作環境

- Bamboo Data Center 12.1（同梱の API 地図は公式 12.1.0 swagger から生成。他の版では細部が異なる場合があります）
- 読み取り専用の Personal Access Token（作成時の既定）
- Python 3.9 以降（ヘルパーは標準ライブラリのみ）

## 導入

**このリポジトリを clone して開けば、その場でスキルが有効になります。** リポジトリ自体が、両ツールの発見先にスキルを内蔵しています。

- `.agents/skills/bamboo-dc-analysis/` — 正本のスキル（Copilot は `.agents/skills/` を発見する）
- `.kiro/skills/bamboo-dc-analysis/` — バイト同一のミラー（Kiro は `.kiro/skills/` を発見する）

```bash
git clone https://github.com/masanori-satake/bamboo-dc-analysis.git
```

配置作業もコピーも不要です。更新は `git pull` だけです。

**別のワークスペースで使う場合** は、チェックアウトから正本フォルダ `.agents/skills/bamboo-dc-analysis/` を取り出してそのワークスペースの `.agents/skills/` に置き、同梱インストーラを1回実行して、Kiro の配置先を正本へのディレクトリリンク（Windows はジャンクション、POSIX はシンボリックリンク）として作ります。実体は正本だけなので、コピー同士が食い違うことはありません。

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace .
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --check
```

リンクが使えない環境向けに `--mode copy` もあり、`--check` がファイル集合と SHA-256 で同一性を検証します。同梱のフィクスチャテストは配置先を指定して実行できるので（`BAMBOO_SKILL_DIR=<配置先> python tests/test_bamboo.py`）、両方で同じ動きになることを実際に確かめられます。保守ルールの全文は [MAINTAINING.md](MAINTAINING.md) にあります。

## 初期設定

1. Bamboo の画面でプロフィール → Personal access tokens → Create token から、この用途専用のトークンを発行します。権限は既定の読み取り専用のまま、名前は用途が分かるもの（例: analysis-skill）にし、有効期限を設定します。
2. エディタを起動するシェルで環境変数を設定します。PowerShell でそのセッションだけに設定する例:

```powershell
$env:BAMBOO_BASE_URL = "https://（BambooのURL）"
$env:BAMBOO_PAT = "（発行したPAT）"
```

`BAMBOO_BASE_URL` は Bamboo のルート URL（コンテキストパスを含む、末尾に `/rest` は付けない）です。**末尾のスラッシュは、あってもなくても構いません。** ヘルパーが末尾のスラッシュを取り除いてから接続するので、どちらでも同じ動きをします。

3. 疎通確認（スキルフォルダ `.agents/skills/bamboo-dc-analysis/` で実行）:

```bash
python scripts/bamboo.py check
```

接続先の版と、誰として認証されたかが返れば準備完了です。あとはエージェントに頼むだけです。

ユースケースごとの詳細なプロンプト（朝の状況確認、失敗の切り分け、ビルド遅延の調査、移行ドシエ、週次レポートなど、そのまま貼って使える形）は [ユースケース別プロンプト集](docs/use-cases.md) にあります。

## ヘルパーのコマンド

スキルフォルダ（`.agents/skills/bamboo-dc-analysis/`）で実行します。

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

## 限界

- ビルドログ全文を返すエンドポイントはないため、失敗分析は結果詳細（ステージ／ジョブ、テスト集計、成果物）までが範囲です。
- Expiry で削除された古い結果は API でも戻りません。履歴分析は残っている範囲での分析です。
- GET でも WRITE スコープ扱いのエンドポイント（権限、プラン依存、Docker 構成、デプロイプロジェクトの Specs 等）は、読み取り専用トークンでは 403 になることがあります。その場合は「取得不可」として記録し、推測で補いません。

## リポジトリ構成

- `.agents/skills/bamboo-dc-analysis/` — 正本のスキル一式（`SKILL.md`、`references/`（12.1 の API 地図、Bamboo Specs YAML の読み方、分析指標の定義、生成した GET エンドポイント全一覧）、`scripts/`（読み取り専用 REST ヘルパーとインストーラ）、`tests/`（フィクスチャテスト））
- `.kiro/skills/bamboo-dc-analysis/` — 正本のバイト同一ミラー。`tools/sync_mirror.py` が生成し、手では編集しない
- `docs/use-cases.md` — ユースケース別プロンプト集
- `tools/sync_mirror.py` — ミラーの再生成と同一性検証
- `MAINTAINING.md` — 正本1つを保つ保守・リリースのルール

## ライセンス

MIT — [LICENSE](LICENSE) を参照してください。
