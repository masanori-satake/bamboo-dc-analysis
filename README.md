# Bamboo DC Analysis

[![Latest release](https://img.shields.io/github/v/release/masanori-satake/bamboo-dc-analysis)](https://github.com/masanori-satake/bamboo-dc-analysis/releases)
[![Sync mirror and release](https://github.com/masanori-satake/bamboo-dc-analysis/actions/workflows/sync-and-release.yml/badge.svg)](https://github.com/masanori-satake/bamboo-dc-analysis/actions/workflows/sync-and-release.yml)

An Agent Skill that investigates and analyzes **Atlassian Bamboo Data Center (12.1)** through its REST API — read-only — from GitHub Copilot, Amazon Kiro, or any agent that supports the Agent Skills format.

Instead of clicking through the Bamboo web UI screen by screen, you ask your agent questions such as "which plans are failing right now?", "show me the success rate and build duration trend for this plan over the last 90 days", or "what does each task in this plan do, and what triggers it?".

## What it can do

- **Inventory** — list projects and plans you can see, with their state (enabled, building, average build time).
- **Snapshot** — latest results across plans, plans currently failing, build/deployment queues, and the current deployed version per environment.
- **History analysis** — per plan over a window (default 90 days): run count, success rate, build duration (mean / median / p95), current failure streak, last successful run, long-inactive plans.
- **Plan dossier** — for one plan at a time: plan detail, Bamboo Specs YAML export, branches, artifacts, variable names, plan dependencies, linked deployment projects, and history stats in one folder.
- **Task and trigger investigation** — task-level configuration, triggers, and notifications have no dedicated GET endpoints in the Bamboo REST API. The only source is the Bamboo Specs export, so the skill reads the exported YAML (with a generated outline of triggers, notifications, and per-job task types) to answer "what does this plan actually do, and what starts it?".

## Safety model

- **GET only.** The skill never triggers builds or deployments and never changes Bamboo state.
- **Credentials stay out of files.** The helper reads `BAMBOO_BASE_URL` and `BAMBOO_PAT` from environment variables only. Nothing is written into the skill, your repository, or its output.
- **Secrets are not collected.** For variables, only names and the password flag are reported — never values. The token is never printed or written to any output file.
- **Permission-scoped.** You only see what the token owner's READ permissions allow. The skill reports that scope instead of pretending to show everything.

## Requirements

- Bamboo Data Center 12.1 (the bundled API map is generated from the official 12.1.0 swagger; other versions may differ in details)
- A personal access token with read-only permissions (the default when creating a token)
- Python 3.9+ (the helper uses only the standard library)

## Install

**Clone this repository and open it — the skill is already active.** The repository itself carries the skill in the locations both tools discover:

- `.agents/skills/bamboo-dc-analysis/` — the canonical skill (GitHub Copilot discovers `.agents/skills/`)
- `.kiro/skills/bamboo-dc-analysis/` — a byte-identical mirror (Kiro discovers `.kiro/skills/`)

```bash
git clone https://github.com/masanori-satake/bamboo-dc-analysis.git
```

No install step, no copying. Updates are a `git pull`.

To use the skill in a **different workspace**, take the canonical folder `.agents/skills/bamboo-dc-analysis/` from a checkout and place it in that workspace's `.agents/skills/`, then run its bundled installer once to set up Kiro's location as a directory link (a junction on Windows, a symlink on POSIX) pointing at the canonical — one physical copy, so the two environments cannot drift apart:

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace .
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --check
```

Where links are not possible, the installer has a `--mode copy` fallback, and `--check` verifies parity by file set and SHA-256 instead of assuming it. The bundled fixture tests can run against any installed location (`BAMBOO_SKILL_DIR=<path> python tests/test_bamboo.py`), so "same behaviour in both environments" is verified, not hoped for. Maintenance rules live in [MAINTAINING.md](MAINTAINING.md).

## Setup

1. In Bamboo, open your profile → **Personal access tokens** → **Create token**. Keep the default read-only permissions, give it a recognizable name (for example `analysis-skill`), and set an expiry date.
2. Set the environment variables in the shell that launches your editor. In PowerShell, for the current session only:

```powershell
$env:BAMBOO_BASE_URL = "https://your-bamboo.example.com"
$env:BAMBOO_PAT = "your-token"
```

`BAMBOO_BASE_URL` is the Bamboo root URL including any context path, without a trailing `/rest`.

3. Verify the connection (run from the skill folder, `.agents/skills/bamboo-dc-analysis/`):

```bash
python scripts/bamboo.py check
```

This reports the instance version and who you are authenticated as. After that, just ask your agent.

## Helper commands

Run from the skill folder (`.agents/skills/bamboo-dc-analysis/`):

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

## Limitations

- There is no REST endpoint that returns full build logs, so failure analysis goes as far as result details (stages, jobs, test summaries, artifacts).
- Results deleted by Bamboo's expiry settings cannot be recovered through the API; history analysis covers what remains.
- Some GET endpoints are WRITE-scoped in the API specification (permissions, plan dependencies, Docker configuration, deployment project Specs). A read-only token may receive 403 for those; the skill records them as unavailable instead of guessing.

## Repository layout

- `.agents/skills/bamboo-dc-analysis/` — the canonical skill: `SKILL.md`, `references/` (API map for 12.1, a guide to reading Bamboo Specs YAML, analysis metric definitions, the full generated GET endpoint list), `scripts/` (the read-only REST helper and the installer), `tests/` (fixture tests)
- `.kiro/skills/bamboo-dc-analysis/` — byte-identical mirror of the canonical skill, generated by `tools/sync_mirror.py` and never edited by hand
- `tools/sync_mirror.py` — regenerates the mirror and verifies parity
- `MAINTAINING.md` — the single-canonical maintenance and release rules

## License

MIT — see [LICENSE](LICENSE).

---

# Bamboo DC Analysis（日本語）

**Atlassian Bamboo Data Center（12.1）** を REST API で読み取り専用に調査・分析する Agent Skill です。GitHub Copilot、Amazon Kiro など、Agent Skills 形式に対応したエージェントから使えます。

Bamboo の Web 画面を行ったり来たりする代わりに、「いま失敗しているプランはどれ？」「このプランの直近90日の成功率と所要時間の傾向を見せて」「このプランの各タスクは何をしていて、何をトリガーに実行されるの？」のようにエージェントへ聞けるようにします。

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

**別のワークスペースで使う場合** は、チェックアウトから正本フォルダ `.agents/skills/bamboo-dc-analysis/` を取り出してそのワークスペースの `.agents/skills/` に置き、同梱インストーラを1回実行して、Kiro の配置先を正本へのディレクトリリンク（Windows はジャンクション、POSIX はシンボリックリンク）として作ります。実体は1つなので、両環境がずれようがありません。

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace .
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --check
```

リンクが使えない環境向けに `--mode copy` もあり、`--check` がファイル集合と SHA-256 で同一性を検証します。同梱のフィクスチャテストも任意の配置先を指定して実行でき（`BAMBOO_SKILL_DIR=<配置先> python tests/test_bamboo.py`）、「両環境で同じ動き」を前提でなく検証で確かめます。保守ルールの全文は [MAINTAINING.md](MAINTAINING.md) にあります。

## 初期設定

1. Bamboo の画面でプロフィール → Personal access tokens → Create token から、この用途専用のトークンを発行します。権限は既定の読み取り専用のまま、名前は用途が分かるもの（例: analysis-skill）にし、有効期限を設定します。
2. エディタを起動するシェルで環境変数を設定します。PowerShell でそのセッションだけに設定する例:

```powershell
$env:BAMBOO_BASE_URL = "https://（BambooのURL）"
$env:BAMBOO_PAT = "（発行したPAT）"
```

`BAMBOO_BASE_URL` は Bamboo のルート URL（コンテキストパスを含む、末尾に `/rest` は付けない）です。

3. 疎通確認（スキルフォルダ `.agents/skills/bamboo-dc-analysis/` で実行）:

```bash
python scripts/bamboo.py check
```

接続先の版と、誰として認証されたかが返れば準備完了です。あとはエージェントに頼むだけです。

## 限界

- ビルドログ全文を返すエンドポイントはないため、失敗分析は結果詳細（ステージ／ジョブ、テスト集計、成果物）までが範囲です。
- Expiry で削除された古い結果は API でも戻りません。履歴分析は残っている範囲での分析です。
- GET でも WRITE スコープ扱いのエンドポイント（権限、プラン依存、Docker 構成、デプロイプロジェクトの Specs 等）は、読み取り専用トークンでは 403 になることがあります。その場合は「取得不可」として記録し、推測で補いません。

## ライセンス

MIT — [LICENSE](LICENSE) を参照してください。
