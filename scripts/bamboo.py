#!/usr/bin/env python3
"""Bamboo Data Center REST helper (read-only).

Reads connection settings from environment variables only:
  BAMBOO_BASE_URL  e.g. https://bamboo.example.com/bamboo  (root incl. context path, no trailing /rest)
  BAMBOO_PAT       Personal Access Token (read-only). Sent as "Authorization: Bearer ...".
                   Never printed, never written to any output file.

Only HTTP GET is used. Standard library only, so it runs on a plain Python 3.9+.
"""
import argparse
import json
import os
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

TIMEOUT = 30
DEFAULT_PAGE = 100


class ConfigError(Exception):
    pass


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def load_config():
    base = os.environ.get("BAMBOO_BASE_URL", "").rstrip("/")
    pat = os.environ.get("BAMBOO_PAT", "")
    if not base or not pat:
        raise ConfigError(
            "BAMBOO_BASE_URL and BAMBOO_PAT must be set in the environment. "
            "Do not write them into files or chat."
        )
    return base, pat


def redact(text, pat):
    if pat and pat in text:
        return text.replace(pat, "***")
    return text


def api_get(base, pat, path, params=None, accept="application/json"):
    url = base + "/rest" + path
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        if clean:
            url += "?" + urllib.parse.urlencode(clean)
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": "Bearer " + pat,
            "Accept": accept,
            "User-Agent": "bamboo-dc-analysis-skill/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read()
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        try:
            excerpt = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            excerpt = ""
        raise ApiError(e.code, f"HTTP {e.code} for {path}: {redact(excerpt, pat)}")
    except urllib.error.URLError as e:
        raise ApiError(0, f"Connection failed for {path}: {e.reason}")
    if "json" in ctype:
        return json.loads(body.decode("utf-8"))
    return body.decode("utf-8", "replace")


def fetch_paged(base, pat, path, container_key, item_key, params=None, max_pages=20, page_size=DEFAULT_PAGE):
    """Fetch a Bamboo list endpoint across pages. Returns (items, total_size, truncated)."""
    items = []
    total = None
    start = 0
    p = dict(params or {})
    for _ in range(max_pages):
        p["max-results"] = page_size
        p["start-index"] = start
        data = api_get(base, pat, path, p)
        container = data.get(container_key, {}) if isinstance(data, dict) else {}
        page_items = container.get(item_key, []) if isinstance(container, dict) else []
        if isinstance(page_items, dict):
            page_items = [page_items]
        items.extend(page_items)
        if isinstance(data, dict) and isinstance(data.get("size"), int):
            total = data["size"]
        if not page_items or len(page_items) < page_size:
            break
        start += len(page_items)
        if total is not None and len(items) >= total:
            break
    truncated = total is not None and len(items) < total
    return items, total, truncated


def parse_time(value):
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def result_duration_seconds(result):
    started = parse_time(result.get("buildStartedTime"))
    completed = parse_time(result.get("buildCompletedTime"))
    if started and completed:
        return max(0.0, (completed - started).total_seconds())
    for key in ("buildDurationInSeconds", "durationInSeconds"):
        v = result.get(key)
        if isinstance(v, (int, float)) and v >= 0:
            return float(v)
    return None


def percentile(values, pct):
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, int(round(pct / 100.0 * len(ordered))))
    return ordered[min(rank, len(ordered)) - 1]


def compute_history_stats(results, days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    in_window = []
    for r in results:
        completed = parse_time(r.get("buildCompletedTime")) or parse_time(r.get("buildStartedTime"))
        if completed is None or completed >= cutoff:
            in_window.append(r)
    finished = [r for r in in_window if r.get("lifeCycleState") in (None, "Finished")]
    states = [r.get("buildState") or r.get("state") for r in finished]
    total = len(finished)
    successful = sum(1 for s in states if s == "Successful")
    failed = sum(1 for s in states if s == "Failed")
    durations = [d for d in (result_duration_seconds(r) for r in finished) if d is not None]
    # longest current failure streak, counting from the newest finished result
    streak = 0
    ordered = sorted(
        finished,
        key=lambda r: parse_time(r.get("buildCompletedTime")) or parse_time(r.get("buildStartedTime")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    for r in ordered:
        if (r.get("buildState") or r.get("state")) == "Failed":
            streak += 1
        else:
            break
    last_success = None
    for r in ordered:
        if (r.get("buildState") or r.get("state")) == "Successful":
            last_success = r.get("buildCompletedTime") or r.get("buildStartedTime")
            break
    last_run = ordered[0].get("buildCompletedTime") if ordered else None
    return {
        "windowDays": days,
        "runs": total,
        "successful": successful,
        "failed": failed,
        "successRate": round(successful / total, 4) if total else None,
        "durationSeconds": {
            "count": len(durations),
            "mean": round(statistics.mean(durations), 1) if durations else None,
            "median": round(statistics.median(durations), 1) if durations else None,
            "p95": round(percentile(durations, 95), 1) if durations else None,
        },
        "currentFailureStreak": streak,
        "lastRunAt": last_run,
        "lastSuccessAt": last_success,
        "sampledResults": len(results),
    }


def specs_outline(yaml_text):
    """Best-effort outline of a Bamboo Specs YAML document.

    Indentation-based scan (no YAML library). Extracts top-level sections and,
    for triggers / notifications / variables / repositories, their first-level
    entries, plus per-job task type names in order. The full YAML stays the
    source of truth; this outline is only a reading aid.
    """
    lines = yaml_text.splitlines()
    sections = {}
    current_section = None
    current_job = None
    jobs = {}
    in_tasks = False
    tasks_indent = None
    task_item_indent = None
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()
        if indent == 0:
            key = text.rstrip(":").split(":")[0].strip()
            current_section = key
            sections.setdefault(key, [])
            in_tasks = False
            current_job = None
            continue
        if current_section == "jobs":
            if text.startswith("- ") and indent <= 4:
                job_name = text[2:].rstrip(":").strip().strip("'\"")
                current_job = job_name
                jobs.setdefault(current_job, [])
                in_tasks = False
                continue
            if text.startswith("tasks:"):
                in_tasks = True
                tasks_indent = indent
                task_item_indent = None
                continue
            if in_tasks:
                if indent <= tasks_indent and not text.startswith("- "):
                    in_tasks = False
                elif text.startswith("- ") and current_job is not None:
                    if task_item_indent is None:
                        task_item_indent = indent
                    if indent == task_item_indent:
                        task = text[2:].rstrip(":").strip()
                        if task and not task.startswith("-"):
                            jobs[current_job].append(task)
            continue
        if current_section in ("triggers", "notifications", "variables", "repositories"):
            if text.startswith("- "):
                entry = text[2:].strip()
                sections[current_section].append(entry)
    return {
        "sections": sorted(sections.keys()),
        "triggers": sections.get("triggers", []),
        "notifications": sections.get("notifications", []),
        "variables": sections.get("variables", []),
        "repositories": sections.get("repositories", []),
        "jobTasks": jobs,
        "note": "Best-effort outline from indentation scan. Read the full Specs YAML for conditions, arguments and ordering details.",
    }


def dump(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def split_plan_key(plan_key):
    parts = plan_key.split("-", 1)
    if len(parts) != 2:
        raise ConfigError("Plan key must look like PROJECT-PLAN")
    return parts[0], parts[1]


def cmd_check(base, pat, args):
    info = api_get(base, pat, "/api/latest/info")
    user = api_get(base, pat, "/api/latest/currentUser")
    dump({"info": info, "currentUser": user})


def cmd_projects(base, pat, args):
    items, total, truncated = fetch_paged(
        base, pat, "/api/latest/project", "projects", "project",
        params={"expand": "projects.project"}, max_pages=args.max_pages,
    )
    dump({"projects": items, "size": total, "returned": len(items), "truncated": truncated})


def cmd_plans(base, pat, args):
    items, total, truncated = fetch_paged(
        base, pat, "/api/latest/plan", "plans", "plan",
        params={"expand": "plans.plan"}, max_pages=args.max_pages,
    )
    dump({"plans": items, "size": total, "returned": len(items), "truncated": truncated})


def cmd_plan(base, pat, args):
    data = api_get(base, pat, f"/api/latest/plan/{args.plan_key}",
                   {"expand": "stages,branches,actions,applications,labels,variableContext"})
    dump(data)


def cmd_latest(base, pat, args):
    params = {"expand": "results.result"}
    if args.state:
        params["buildstate"] = args.state
    if args.in_progress:
        params["includeAllStates"] = "true"
        params["lifeCycleState"] = "InProgress"
    items, total, truncated = fetch_paged(
        base, pat, "/api/latest/result", "results", "result",
        params=params, max_pages=args.max_pages,
    )
    dump({"results": items, "size": total, "returned": len(items), "truncated": truncated})


def cmd_results(base, pat, args):
    items, total, truncated = fetch_paged(
        base, pat, f"/api/latest/result/{args.plan_key}", "results", "result",
        params={"expand": "results.result"}, max_pages=args.max_pages,
    )
    dump({"results": items, "size": total, "returned": len(items), "truncated": truncated})


def cmd_result(base, pat, args):
    data = api_get(base, pat, f"/api/latest/result/{args.result_key}",
                   {"expand": "artifacts,stages,comments,labels,jiraIssues,testResults,logEntries"})
    dump(data)


def cmd_history(base, pat, args):
    items, total, truncated = fetch_paged(
        base, pat, f"/api/latest/result/{args.plan_key}", "results", "result",
        params={"expand": "results.result"}, max_pages=args.max_pages,
    )
    stats = compute_history_stats(items, args.days)
    stats["totalAvailable"] = total
    stats["truncated"] = truncated
    dump(stats)


def cmd_branches(base, pat, args):
    items, total, truncated = fetch_paged(
        base, pat, f"/api/latest/plan/{args.plan_key}/branch", "branches", "branch",
        params={"expand": "branches.branch"}, max_pages=args.max_pages,
    )
    dump({"branches": items, "size": total, "returned": len(items), "truncated": truncated})


def cmd_variables(base, pat, args):
    data = api_get(base, pat, f"/api/latest/plan/{args.plan_key}/variables")
    raw = data if isinstance(data, list) else data.get("variables", data)
    names = []
    if isinstance(raw, list):
        for v in raw:
            if isinstance(v, dict):
                names.append({
                    "name": v.get("name") or v.get("key"),
                    "isPassword": bool(v.get("isPassword") or v.get("password")),
                })
    dump({"variables": names, "note": "Values are never output by this helper."})


def cmd_deploys(base, pat, args):
    data = api_get(base, pat, "/api/latest/deploy/project/all")
    dump(data)


def cmd_deploy_env(base, pat, args):
    items, total, truncated = fetch_paged(
        base, pat, f"/api/latest/deploy/environment/{args.environment_id}/results",
        "results", "result", max_pages=args.max_pages,
    )
    dump({"results": items, "size": total, "returned": len(items), "truncated": truncated})


def cmd_queue(base, pat, args):
    builds = api_get(base, pat, "/api/latest/queue")
    deploys = api_get(base, pat, "/api/latest/queue/deployment")
    dump({"buildQueue": builds, "deploymentQueue": deploys})


def fetch_specs(base, pat, plan_key):
    project, build = split_plan_key(plan_key)
    return api_get(
        base, pat,
        f"/api/latest/plan/{project}-{build}/specs",
        {"format": "YAML"},
        accept="text/plain",
    )


def cmd_specs(base, pat, args):
    text = fetch_specs(base, pat, args.plan_key)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote {args.out} ({len(text)} chars)")
    else:
        sys.stdout.write(text)


def cmd_specs_outline(base, pat, args):
    text = fetch_specs(base, pat, args.plan_key)
    dump(specs_outline(text))


def cmd_dossier(base, pat, args):
    os.makedirs(args.out, exist_ok=True)

    def save(name, obj):
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as f:
            if isinstance(obj, str):
                f.write(obj)
            else:
                json.dump(obj, f, ensure_ascii=False, indent=2)

    plan = api_get(base, pat, f"/api/latest/plan/{args.plan_key}",
                   {"expand": "stages,branches,actions,labels,variableContext"})
    save("plan.json", plan)

    specs_text, specs_note = None, ""
    try:
        specs_text = fetch_specs(base, pat, args.plan_key)
        save("specs.yaml", specs_text)
    except ApiError as e:
        specs_note = f"Specs export unavailable: {e.message}"

    branches, _, _ = fetch_paged(base, pat, f"/api/latest/plan/{args.plan_key}/branch",
                                  "branches", "branch", params={"expand": "branches.branch"})
    save("branches.json", branches)

    try:
        artifacts = api_get(base, pat, f"/api/latest/plan/{args.plan_key}/artifact")
        save("artifacts.json", artifacts)
    except ApiError as e:
        save("artifacts.json", {"error": e.message})

    variables = api_get(base, pat, f"/api/latest/plan/{args.plan_key}/variables")
    save("variables-raw.json", variables)

    deps = {}
    for side in ("parent", "child"):
        try:
            deps[side] = api_get(base, pat, f"/api/latest/dependency/search/{args.plan_key}/{side}")
        except ApiError as e:
            deps[side] = {"error": e.message}
    save("dependencies.json", deps)

    try:
        deploy = api_get(base, pat, "/api/latest/deploy/project/forPlan", {"planKey": args.plan_key})
        save("deploy-for-plan.json", deploy)
    except ApiError as e:
        save("deploy-for-plan.json", {"error": e.message})

    results, total, truncated = fetch_paged(base, pat, f"/api/latest/result/{args.plan_key}",
                                             "results", "result", params={"expand": "results.result"},
                                             max_pages=args.max_pages)
    stats = compute_history_stats(results, args.days)
    stats["totalAvailable"] = total
    stats["truncated"] = truncated
    save("history-stats.json", stats)

    outline = specs_outline(specs_text) if specs_text else None
    plan_name = plan.get("name") or plan.get("planName") or args.plan_key
    lines = []
    lines.append(f"# 移行・分析ドシエ: {plan_name}（{args.plan_key}）")
    lines.append("")
    lines.append(f"- 有効: {plan.get('enabled')} / 実行中: {plan.get('building')} / 平均ビルド時間(秒): {plan.get('averageBuildTimeInSeconds')}")
    lines.append(f"- 説明: {plan.get('description') or ''}")
    lines.append("")
    lines.append("## 履歴サマリ")
    lines.append("")
    lines.append(f"- 直近 {args.days} 日: 実行 {stats['runs']} 回、成功率 {stats['successRate']}、所要時間 中央値 {stats['durationSeconds']['median']} 秒 / p95 {stats['durationSeconds']['p95']} 秒")
    lines.append(f"- 現在の連続失敗: {stats['currentFailureStreak']} / 最終成功: {stats['lastSuccessAt']} / 最終実行: {stats['lastRunAt']}")
    lines.append(f"- 取得できた結果総数: {total}（打ち切り: {truncated}）")
    lines.append("")
    if specs_note:
        lines.append("## Specs")
        lines.append("")
        lines.append(f"- {specs_note}")
        lines.append("")
    if outline:
        lines.append("## トリガー（Specs より）")
        lines.append("")
        for t in outline["triggers"] or ["（記載なし）"]:
            lines.append(f"- {t}")
        lines.append("")
        lines.append("## 通知（Specs より）")
        lines.append("")
        for n in outline["notifications"] or ["（記載なし）"]:
            lines.append(f"- {n}")
        lines.append("")
        lines.append("## ジョブとタスク（Specs より、出現順）")
        lines.append("")
        for job, tasks in outline["jobTasks"].items():
            lines.append(f"- {job}: " + " → ".join(tasks))
        lines.append("")
        lines.append("詳細な条件・引数・スクリプト本文は specs.yaml を読むこと。このアウトラインはインデント走査による読み補助であり、完全な再現ではない。")
        lines.append("")
    lines.append("## 変数（名前のみ）")
    lines.append("")
    raw_vars = variables if isinstance(variables, list) else variables.get("variables", [])
    if isinstance(raw_vars, list):
        for v in raw_vars:
            if isinstance(v, dict):
                flag = "（パスワード）" if (v.get("isPassword") or v.get("password")) else ""
                lines.append(f"- {v.get('name') or v.get('key')}{flag}")
    lines.append("")
    lines.append(f"ブランチ数: {len(branches)}。成果物・依存・デプロイの詳細は同フォルダの JSON を参照。")
    save("dossier.md", "\n".join(lines) + "\n")
    print(f"Dossier written to {args.out}")


def build_parser():
    parser = argparse.ArgumentParser(description="Bamboo Data Center REST helper (read-only, GET only)")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_paging(p):
        p.add_argument("--max-pages", type=int, default=20)

    p = sub.add_parser("check", help="GET /info and /currentUser")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("projects", help="List projects")
    add_paging(p)
    p.set_defaults(func=cmd_projects)

    p = sub.add_parser("plans", help="List plans")
    add_paging(p)
    p.set_defaults(func=cmd_plans)

    p = sub.add_parser("plan", help="Plan detail")
    p.add_argument("plan_key")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("latest", help="Latest results across plans")
    p.add_argument("--state", choices=["Successful", "Failed", "Unknown"])
    p.add_argument("--in-progress", action="store_true")
    add_paging(p)
    p.set_defaults(func=cmd_latest)

    p = sub.add_parser("results", help="Result history for a plan")
    p.add_argument("plan_key")
    add_paging(p)
    p.set_defaults(func=cmd_results)

    p = sub.add_parser("result", help="One result detail")
    p.add_argument("result_key")
    p.set_defaults(func=cmd_result)

    p = sub.add_parser("history", help="Aggregated history stats for a plan")
    p.add_argument("plan_key")
    p.add_argument("--days", type=int, default=90)
    add_paging(p)
    p.set_defaults(func=cmd_history)

    p = sub.add_parser("branches", help="Plan branches")
    p.add_argument("plan_key")
    add_paging(p)
    p.set_defaults(func=cmd_branches)

    p = sub.add_parser("variables", help="Plan variable names only (values never output)")
    p.add_argument("plan_key")
    p.set_defaults(func=cmd_variables)

    p = sub.add_parser("deploys", help="Deployment projects")
    p.set_defaults(func=cmd_deploys)

    p = sub.add_parser("deploy-env", help="Deployment results for an environment")
    p.add_argument("environment_id")
    add_paging(p)
    p.set_defaults(func=cmd_deploy_env)

    p = sub.add_parser("queue", help="Build and deployment queues")
    p.set_defaults(func=cmd_queue)

    p = sub.add_parser("specs", help="Export plan Specs (YAML by default format param)")
    p.add_argument("plan_key")
    p.add_argument("--out")
    p.set_defaults(func=cmd_specs)

    p = sub.add_parser("specs-outline", help="Outline triggers, notifications and job tasks from Specs YAML")
    p.add_argument("plan_key")
    p.set_defaults(func=cmd_specs_outline)

    p = sub.add_parser("dossier", help="Write a per-plan dossier folder (plan, specs, branches, artifacts, variables, dependencies, deploys, history)")
    p.add_argument("plan_key")
    p.add_argument("--out", required=True)
    p.add_argument("--days", type=int, default=90)
    add_paging(p)
    p.set_defaults(func=cmd_dossier)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        base, pat = load_config()
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 3
    try:
        args.func(base, pat, args)
    except ApiError as e:
        print(f"API error: {e.message}", file=sys.stderr)
        return 2
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
