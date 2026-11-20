# Bamboo DC Analysis

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

Clone this repository once, as the canonical copy, into `.agents/skills/`:

```bash
git clone https://github.com/masanori-satake/bamboo-dc-analysis.git .agents/skills/bamboo-dc-analysis
```

Then run the installer once per workspace:

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace .
```

## One canonical copy for both Copilot and Kiro

There is exactly one physical copy of this skill, and both tools work from it:

- **GitHub Copilot** reads `.agents/skills/` directly as a project skill location, so it uses the canonical copy as-is. No Copilot-specific copy exists.
- **Kiro** only reads `.kiro/skills/`, so the installer places a **directory link** there (a junction on Windows, a symlink on POSIX) pointing at the canonical copy. A link is not a copy: edit the canonical and Kiro sees the same content immediately, so the two environments cannot drift apart.

Where links are not possible (for example, a tree that must be committed as real files), use `--mode copy` and verify parity instead of assuming it:

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --mode copy
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --check
```

`--check` compares every installed location against the canonical by file set and SHA-256 and fails on any difference. The bundled fixture tests can also run against any installed location (`BAMBOO_SKILL_DIR=<path> python tests/test_bamboo.py`), so "same behaviour in both environments" is verified, not hoped for. Updates are just a `git pull` of the canonical clone; with links, Kiro follows automatically. The full maintenance rules live in [MAINTAINING.md](MAINTAINING.md).

## Setup

1. In Bamboo, open your profile → **Personal access tokens** → **Create token**. Keep the default read-only permissions, give it a recognizable name (for example `analysis-skill`), and set an expiry date.
2. Set the environment variables in the shell that launches your editor. In PowerShell, for the current session only:

```powershell
$env:BAMBOO_BASE_URL = "https://your-bamboo.example.com"
$env:BAMBOO_PAT = "your-token"
```

`BAMBOO_BASE_URL` is the Bamboo root URL including any context path, without a trailing `/rest`.

3. Verify the connection:

```bash
python scripts/bamboo.py check
```

This reports the instance version and who you are authenticated as. After that, just ask your agent.

## Helper commands

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

- `SKILL.md` — the skill itself
- `references/` — API map for 12.1, a guide to reading Bamboo Specs YAML, analysis metric definitions, and the full generated GET endpoint list
- `scripts/bamboo.py` — the read-only REST helper

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

正本として、このリポジトリを `.agents/skills/` へ1回だけ clone します。

```bash
git clone https://github.com/masanori-satake/bamboo-dc-analysis.git .agents/skills/bamboo-dc-analysis
```

そのうえで、ワークスペースごとにインストーラを1回実行します。

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace .
```

## 正本1つで Copilot と Kiro の両対応

スキルの実体は1つだけで、両ツールがそこから動きます。

- **GitHub Copilot** は `.agents/skills/` をプロジェクトスキルの配置先として直接読むため、正本をそのまま使います。Copilot 向けのコピーは存在しません。
- **Kiro** は `.kiro/skills/` しか読まないため、そこにはコピーではなく、正本を指す **ディレクトリリンク**（Windows はジャンクション、POSIX はシンボリックリンク）を置きます。リンクはコピーではないので、正本を直せば Kiro 側も即座に同じ内容になり、両環境がずれようがありません。

リンクが使えない環境（ファイルそのものをコミットする必要があるツリー等）では `--mode copy` でコピー方式にし、同一性は検証で担保します。

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --mode copy
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --check
```

`--check` は配置先と正本をファイル集合と SHA-256 で比較し、差分があれば失敗します。同梱のフィクスチャテストも任意の配置先を指定して実行でき（`BAMBOO_SKILL_DIR=<配置先> python tests/test_bamboo.py`）、「両環境で同じ動き」を前提でなく検証で確かめます。更新は正本の clone を `git pull` するだけで、リンク方式なら Kiro 側は自動で追随します。保守ルールの全文は [MAINTAINING.md](MAINTAINING.md) にあります。

## 初期設定

1. Bamboo の画面でプロフィール → Personal access tokens → Create token から、この用途専用のトークンを発行します。権限は既定の読み取り専用のまま、名前は用途が分かるもの（例: analysis-skill）にし、有効期限を設定します。
2. エディタを起動するシェルで環境変数を設定します。PowerShell でそのセッションだけに設定する例:

```powershell
$env:BAMBOO_BASE_URL = "https://（BambooのURL）"
$env:BAMBOO_PAT = "（発行したPAT）"
```

`BAMBOO_BASE_URL` は Bamboo のルート URL（コンテキストパスを含む、末尾に `/rest` は付けない）です。

3. 疎通確認:

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
