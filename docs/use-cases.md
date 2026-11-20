# Use cases and prompt cookbook

For people who investigate and analyze Bamboo with this skill. The [README](../README.md) covers setup and basic usage; this document collects detailed, ready-to-paste prompts per use case.

How to read each entry: **Goal** — what you want to know. **Prompt** — paste it to your agent as-is (replace plan keys and periods with yours). **You get** — the shape of the answer. **Notes** — limits and follow-ups worth knowing.

Two things to keep in mind for every prompt:

- Answers are computed from what your access token can see. If a plan is missing from an answer, it may be outside your permissions rather than nonexistent.
- The skill always states the period, the number of results read, and whether a list was truncated. If an answer lacks those, ask for them — long lists are paged, and a silent truncation changes conclusions.

---

## 1. Morning snapshot — what is failing right now?

**Goal.** Start the day knowing which plans need attention, without opening the Bamboo UI.

**Prompt**

```
Using the Bamboo skill, show me the current state across all plans I can see:
which plans' latest results are failures, which builds are running or queued,
and which deployment environments were updated most recently. For each failing
plan, include when its last success was.
```

**You get.** A cross-plan list of latest results filtered to failures, the build and deployment queues, and recent deployment activity.

**Notes.** "Latest result" is one row per plan. To dig into one plan, continue with use case 3.

## 2. Plan health check — success rate and duration trend

**Goal.** Judge whether a plan is healthy over a period, not just today.

**Prompt**

```
Using the Bamboo skill, analyze plan PROJ-PLAN over the last 90 days:
how many runs, the success rate, build duration (mean, median, p95),
the current failure streak, and when the last successful run was.
Tell me whether the duration is trending up.
```

**You get.** Aggregated history statistics with fixed definitions (success rate = successful / completed runs in the window; durations from completed runs).

**Notes.** Name the period explicitly — "recently" is interpreted as the default 90 days. For a release audit, fix the window to the release period and keep the numbers with the period attached.

## 3. Failure triage — when did it break, and with what error?

**Goal.** Separate "it broke just now" from "it has been broken for a week", and see the actual error.

**Prompt**

```
Using the Bamboo skill, investigate the latest failure of plan PROJ-PLAN:
show the failing job, the end of its log or error summary, how many builds
have failed in a row, and what the last successful build was doing differently
(branch, and any visible change in duration).
```

**You get.** The latest result in detail, the failure streak, and the last success for contrast.

**Notes.** The skill reports the error tail the API exposes; full logs may require the Bamboo UI. Ask for a specific older result by key (for example `PROJ-PLAN-JOB1-123`) when comparing two runs.

## 4. Slow-build investigation — where did the time go?

**Goal.** Find whether slowness is recent, gradual, or tied to one job.

**Prompt**

```
Using the Bamboo skill, look at plan PROJ-PLAN over the last 90 days and
tell me how build duration has changed (median and p95, first half vs
second half of the window). Then, from the plan's Bamboo Specs, list the
jobs and the task types in each job, so I can see which job is the likely
heavy one.
```

**You get.** Duration statistics over the window, plus the per-job task composition from the Specs export.

**Notes.** Task-level configuration exists only in the Bamboo Specs export, not in result data — that is why this prompt combines history with Specs. Per-job durations depend on what the result data exposes for your instance.

## 5. What is inside a plan — tasks, triggers, notifications

**Goal.** Answer "what does this plan actually do, and what starts it?" for a plan you inherited.

**Prompt**

```
Using the Bamboo skill, explain plan PROJ-PLAN from its Bamboo Specs:
list each job and its tasks in order, all triggers (scheduled and remote),
and the notification rules. Also list the plan's variables by name and say
which ones are passwords, without showing any values.
```

**You get.** A Specs outline: per-job task types in order, triggers (type and schedule or repository), notifications, and variable names with a password flag.

**Notes.** Variable values are never printed by this skill, for passwords or otherwise. If the Specs export is not permitted for your token, the skill says so — task and trigger details cannot be obtained any other way.

## 6. Inventory and housekeeping — stale and forgotten plans

**Goal.** Find plans nobody has run in months, and projects that have grown unchecked.

**Prompt**

```
Using the Bamboo skill, inventory all projects and plans I can see.
List plans with no completed run in the last 180 days, plans that are
disabled, and for each project the number of plans. State how many plans
you read in total and whether the list was truncated.
```

**You get.** A plan inventory with last-run information, suitable as the starting point for a cleanup discussion.

**Notes.** "No run in 180 days" is judged from result history; confirm before deleting anything — a plan may be seasonal or manually triggered. Truncation matters most here: if the list was cut, the inventory is partial.

## 7. Deployment status — what is running where?

**Goal.** Know the currently deployed version per environment and recent deployment failures.

**Prompt**

```
Using the Bamboo skill, list the deployment projects and, for each
environment, the version currently deployed. Show any failed deployments
in the latest results, and what is waiting in the deployment queue.
```

**You get.** Deployment projects with per-environment current versions, recent failures, and queue state.

**Notes.** Deployment data follows the same visibility rules as plans. Ask for one environment by ID when you need its full history.

## 8. Migration research — moving a plan to GitHub Actions or Bitbucket Pipelines

**Goal.** Collect everything needed to judge how hard one plan is to migrate, in one folder.

**Prompt**

```
Using the Bamboo skill, build a dossier for plan PROJ-PLAN for a migration
assessment: plan details, the Bamboo Specs YAML, the task list per job,
triggers, notification rules, variable names (no values), artifacts,
plan dependencies, linked deployment projects, and the last 90 days of
history statistics. Save it as files and summarize what will need manual
work in GitHub Actions: custom script tasks, Bamboo-specific variables,
and anything the Specs export could not show.
```

**You get.** A dossier folder (plan JSON, Specs YAML, outline, history statistics) plus a summary of migration friction points.

**Notes.** Do one plan at a time — the dossier is the unit of migration work. Secrets never appear: variable values are excluded by design, so credentials must be re-issued in the target system regardless.

## 9. Weekly report — a fixed-period summary for the team

**Goal.** A repeatable summary whose numbers can be compared week to week.

**Prompt**

```
Using the Bamboo skill, write this week's Bamboo summary for the team:
for the last 7 days, per project — number of runs, overall success rate,
plans that failed all week, plans whose p95 duration grew versus the
previous 7 days, and deployments per environment. Always state the exact
period and how many results you read.
```

**You get.** A period-stamped summary using the same metric definitions every time, so weeks are comparable.

**Notes.** Keep the prompt text unchanged between weeks; changing definitions breaks comparability more than changing tools does. Duration comparisons need enough runs in both windows — the skill will say when counts are too small to compare.

## 10. Access check — what can this token actually see?

**Goal.** Before trusting any analysis, confirm the connection and the visible scope.

**Prompt**

```
Using the Bamboo skill, check the connection: which Bamboo instance and
version answered, and who am I authenticated as? Then list the projects
I can see, and tell me the total number.
```

**You get.** The instance version, the authenticated user, and the project list that bounds every other answer.

**Notes.** Every other use case inherits this scope. If a colleague's answer mentions plans you cannot see, compare access checks before comparing conclusions.

---

# ユースケース別プロンプト集

Bamboo の調査・分析にこのスキルを使う人向けの文書です。[README](../README.md) には導入と基本的な使い方を書いているので、ここではユースケースごとの詳細なプロンプトを、そのまま貼って使える形で集めました。

各項目の読み方です。**目的** — 知りたいこと。**プロンプト** — そのままエージェントに貼って使えます（プランキーや期間は自分のものに置き換えてください）。**返ってくるもの** — 回答の形。**注意** — 限界と、次に聞くとよいこと。

どのプロンプトにも共通する前提が2つあります。

- 回答は、あなたのアクセストークンが見える範囲から計算されます。回答にプランが出てこない場合、「存在しない」ではなく「権限の外」かもしれません。
- スキルは必ず、対象期間・読み取った件数・一覧が打ち切られたかどうかを明示します。もし回答にそれが無ければ、聞き直してください。長い一覧はページングされるため、黙った打ち切りは結論を変えます。

---

## 1. 朝の状況確認 — いま失敗しているのはどれか

**目的** — Bamboo の画面を開かずに、今日手を付けるべきプランを把握する。

**プロンプト**

```
Bamboo のスキルを使って、見える範囲の全プランの現状を教えてください。
最新の結果が失敗のプラン、実行中とキューのビルド、最近更新された
デプロイ環境を挙げてください。失敗しているプランには、最後に
成功したのがいつかも付けてください。
```

**返ってくるもの** — 最新結果を失敗で絞った横断一覧、ビルドとデプロイのキュー、最近のデプロイ活動。

**注意** — 「最新結果」はプランごとに1行です。個別のプランを掘る場合はユースケース3へ続けてください。

## 2. プランの健全性診断 — 成功率と所要時間の傾向

**目的** — 今日だけでなく、期間を通してプランが健全かどうかを判断する。

**プロンプト**

```
Bamboo のスキルを使って、プラン PROJ-PLAN の直近90日を分析してください。
実行回数、成功率、ビルド所要時間（平均・中央値・p95）、現在の連続失敗回数、
最後に成功した日時を教えてください。所要時間が伸びる傾向にあるかも
判定してください。
```

**返ってくるもの** — 定義の固定された履歴統計（成功率＝期間内の完了した実行に対する成功の割合、所要時間は完了した実行から算出）。

**注意** — 期間は明示してください。「最近」と言うと既定の90日で解釈されます。リリース監査などでは期間を固定し、数字には必ず期間を添えて残してください。

## 3. 失敗の切り分け — いつから、どんなエラーで壊れているか

**目的** — 「たった今壊れた」のか「1週間前から壊れっぱなし」なのかを分け、実際のエラーを見る。

**プロンプト**

```
Bamboo のスキルを使って、プラン PROJ-PLAN の最新の失敗を調べてください。
失敗したジョブ、ログの末尾またはエラーの要約、連続失敗回数を見せてください。
あわせて、最後に成功したビルドとの違い（ブランチ、所要時間の visible な変化）
も教えてください。
```

**返ってくるもの** — 最新結果の詳細、連続失敗の状況、対比としての最後の成功。

**注意** — スキルが見せるのは API が公開するエラーの末尾です。完全なログは Bamboo の画面が要る場合があります。2つの実行を比べたいときは、結果キーを指定して聞いてください（例： `PROJ-PLAN-JOB1-123`）。

## 4. ビルドが遅くなった調査 — 時間はどこへ行ったか

**目的** — 遅さが最近の変化か、緩やかな悪化か、特定ジョブのものかを見分ける。

**プロンプト**

```
Bamboo のスキルを使って、プラン PROJ-PLAN の直近90日でビルド所要時間が
どう変わったか教えてください（中央値と p95 を、期間の前半と後半で比較）。
そのうえで、このプランの Bamboo Specs から、ジョブごとのタスク種別を
一覧にしてください。どのジョブが重そうか判断材料がほしいです。
```

**返ってくるもの** — 期間内の所要時間統計と、Specs 書き出しに基づくジョブ別タスク構成。

**注意** — タスク単位の設定は結果データには無く、Bamboo Specs の書き出しにだけあります。だからこのプロンプトは履歴と Specs を組み合わせています。ジョブ別の所要時間は、お使いのインスタンスの結果データが公開する範囲に依存します。

## 5. プランの中身調査 — タスク、トリガー、通知

**目的** — 引き継いだプランについて「何をするプランで、何が起動するのか」に答える。

**プロンプト**

```
Bamboo のスキルを使って、プラン PROJ-PLAN を Bamboo Specs から説明して
ください。ジョブごとにタスクを順番に挙げ、トリガー（スケジュールと
リモートの両方）と通知ルールも全部挙げてください。プラン変数は名前だけを
挙げ、パスワードかどうかを示してください。値は表示しないでください。
```

**返ってくるもの** — Specs のアウトライン。ジョブ順のタスク種別、トリガー（種別とスケジュールまたはリポジトリ）、通知、パスワードフラグ付きの変数名。

**注意** — 変数の値は、パスワードに限らずこのスキルは一切表示しません。トークンに Specs 書き出しの権限が無い場合、スキルはその旨を伝えます。タスクとトリガーの詳細は、他の方法では取得できません。

## 6. 棚卸し — 忘れられたプランの洗い出し

**目的** — 何か月も実行されていないプランと、増え続けたプロジェクトを把握する。

**プロンプト**

```
Bamboo のスキルを使って、見える範囲の全プロジェクトと全プランを
棚卸ししてください。直近180日に完了した実行が無いプラン、無効化されて
いるプランを挙げ、プロジェクトごとにプラン数も教えてください。
読み取ったプランの総数と、一覧が打ち切られたかどうかも明示してください。
```

**返ってくるもの** — 最終実行情報付きのプラン一覧。整理の議論の出発点になります。

**注意** — 「180日実行なし」は結果履歴からの判定です。季節性のプランや手動実行のプランもあるので、削除の前に必ず確認してください。打ち切りの有無が最も効くのはこのユースケースです。一覧が途中で切れていれば、棚卸しは部分的なものになります。

## 7. デプロイ状況 — どの環境に何が入っているか

**目的** — 環境ごとの現在のデプロイバージョンと、最近のデプロイ失敗を把握する。

**プロンプト**

```
Bamboo のスキルを使って、デプロイプロジェクトを挙げ、環境ごとに現在
デプロイされているバージョンを教えてください。最新の結果にある
デプロイ失敗と、デプロイキューで待っているものも見せてください。
```

**返ってくるもの** — デプロイプロジェクトと環境別の現行バージョン、最近の失敗、キューの状態。

**注意** — デプロイのデータもプランと同じ可視範囲の規則に従います。特定の環境の履歴が要るときは、環境 ID を指定して聞いてください。

## 8. 移行調査 — GitHub Actions / Bitbucket Pipelines への移行材料

**目的** — 1プランの移行の難しさを判断する材料を、1フォルダに集める。

**プロンプト**

```
Bamboo のスキルを使って、プラン PROJ-PLAN の移行調査ドシエを作って
ください。プラン詳細、Bamboo Specs の YAML、ジョブごとのタスク一覧、
トリガー、通知ルール、変数名（値は除く）、成果物、プラン依存関係、
関連するデプロイプロジェクト、直近90日の履歴統計をファイルに保存し、
GitHub Actions へ移すときに手作業になりそうな点（カスタムスクリプトの
タスク、Bamboo 固有の変数、Specs で見えなかったもの）を要約してください。
```

**返ってくるもの** — ドシエのフォルダ（プラン JSON、Specs YAML、アウトライン、履歴統計）と、移行の摩擦点の要約。

**注意** — 1回に1プランずつが原則です。ドシエが移行作業の単位になります。秘密情報は設計上含まれません（変数の値は除外される）ため、認証情報は移行先で再発行が前提になります。

## 9. 週次レポート — 期間固定のチーム向け要約

**目的** — 週ごとに比較できる、再現性のある要約を作る。

**プロンプト**

```
Bamboo のスキルを使って、今週の Bamboo 要約をチーム向けに書いて
ください。直近7日について、プロジェクトごとに実行回数、全体の成功率、
週を通して失敗し続けたプラン、前7日と比べて p95 所要時間が伸びたプラン、
環境ごとのデプロイ回数を挙げてください。対象期間の正確な範囲と、
読み取った結果の件数は必ず明示してください。
```

**返ってくるもの** — 期間入りの要約。指標の定義が毎回同じなので、週同士を比べられます。

**注意** — プロンプトの文面は週のあいだ変えないでください。定義の変更は、ツールの変更より比較可能性を壊します。所要時間の比較には両期間とも十分な実行回数が要ります。件数が足りなければスキルがその旨を伝えます。

## 10. アクセス確認 — このトークンで何が見えるか

**目的** — どの分析を信じる前に、接続と可視範囲を確かめる。

**プロンプト**

```
Bamboo のスキルを使って、接続を確認してください。応答した Bamboo の
インスタンスとバージョン、私が誰として認証されているかを教えてください。
そのうえで、見えるプロジェクトを挙げ、総数を教えてください。
```

**返ってくるもの** — インスタンスのバージョン、認証ユーザー、そして他のすべての回答の範囲を決めるプロジェクト一覧。

**注意** — 他のユースケースはすべてこの範囲を引き継ぎます。同僚の回答に自分には見えないプランが出てきたら、結論を比べる前にアクセス確認を比べてください。
