import json
import os
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

TOKEN = "TESTTOKEN-SECRET-12345"
SKILL_DIR = os.environ.get(
    "BAMBOO_SKILL_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
HELPER = os.path.join(SKILL_DIR, "scripts", "bamboo.py")

SPECS_YAML = """version: 2
plan:
  project-key: PROJ
  key: PLAN
  name: Sample Plan
repositories:
  - MainRepo:
      scope: global
variables:
  - releaseChannel: stable
  - dbPassword: '********'
triggers:
  - scheduled: '0 0 2 ? * MON-FRI'
  - remote:
      repository: MainRepo
notifications:
  - events:
      - plan-failed
    recipients:
      - watchers
stages:
  - Build:
      jobs:
        - Build Job
jobs:
  - Build Job:
      tasks:
        - checkout:
            force-clean-build: 'true'
        - script:
            interpreter: SHELL
            scripts:
              - echo building
              - make all
        - maven3:
            goal: verify
        - junit-parser:
            results: '**/surefire/*.xml'
      requirements:
        - linux
"""

NOW = datetime.now(timezone.utc)


def ts(dt):
    return dt.isoformat().replace("+00:00", "+09:00")


RESULTS = [
    {
        "key": "PROJ-PLAN-12",
        "lifeCycleState": "Finished",
        "buildState": "Failed",
        "buildStartedTime": ts(NOW - timedelta(days=1, minutes=30)),
        "buildCompletedTime": ts(NOW - timedelta(days=1)),
    },
    {
        "key": "PROJ-PLAN-11",
        "lifeCycleState": "Finished",
        "buildState": "Failed",
        "buildStartedTime": ts(NOW - timedelta(days=2, minutes=60)),
        "buildCompletedTime": ts(NOW - timedelta(days=2)),
    },
    {
        "key": "PROJ-PLAN-10",
        "lifeCycleState": "Finished",
        "buildState": "Successful",
        "buildStartedTime": ts(NOW - timedelta(days=3, minutes=10)),
        "buildCompletedTime": ts(NOW - timedelta(days=3)),
    },
    {
        "key": "PROJ-PLAN-9",
        "lifeCycleState": "Finished",
        "buildState": "Successful",
        "buildStartedTime": ts(NOW - timedelta(days=200, minutes=10)),
        "buildCompletedTime": ts(NOW - timedelta(days=200)),
    },
]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get("Authorization") != "Bearer " + TOKEN:
            self.send_json({"error": "unauthorized"}, 401)
            return
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path == "/rest/api/latest/info":
            self.send_json({"version": "12.1.0", "buildNumber": "120100"})
        elif path == "/rest/api/latest/currentUser":
            self.send_json({"name": "test-user", "fullName": "Test User"})
        elif path == "/rest/api/latest/result/PROJ-PLAN":
            start = int(qs.get("start-index", ["0"])[0])
            size = int(qs.get("max-results", ["100"])[0])
            page = RESULTS[start:start + size]
            self.send_json({
                "size": len(RESULTS),
                "max-result": size,
                "start-index": start,
                "results": {"result": page},
            })
        elif path == "/rest/api/latest/plan/PROJ-PLAN/specs":
            # Real Bamboo behaviour: the specs endpoint produces a JSON
            # envelope (YAML at spec.code) and rejects Accept: text/plain
            # with 406 and an empty body.
            accept = self.headers.get("Accept", "")
            if "application/json" not in accept and "*/*" not in accept:
                self.send_response(406)
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self.send_json({"spec": {"code": SPECS_YAML}})
        elif path == "/rest/api/latest/plan/PROJ-STRICT/specs":
            # Stricter variant: only */* is accepted, to exercise the
            # helper's 406 fallback retry.
            if self.headers.get("Accept", "") != "*/*":
                self.send_response(406)
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self.send_json({"spec": {"code": SPECS_YAML}})
        elif path == "/rest/api/latest/plan/PROJ-PLAN":
            self.send_json({
                "key": "PROJ-PLAN", "name": "Sample Plan", "enabled": True,
                "building": False, "averageBuildTimeInSeconds": 900,
                "description": "fixture",
            })
        elif path == "/rest/api/latest/plan/PROJ-PLAN/branch":
            self.send_json({"size": 1, "branches": {"branch": [{"key": "PROJ-PLAN1", "name": "feature/x"}]}})
        elif path == "/rest/api/latest/plan/PROJ-PLAN/artifact":
            self.send_json({"artifacts": {"artifact": [{"name": "dist", "shared": True}]}})
        elif path == "/rest/api/latest/plan/PROJ-PLAN/variables":
            # Real servers include the values; the helper must project
            # them away everywhere (stdout and dossier files alike).
            self.send_json({"variables": [
                {"name": "releaseChannel", "isPassword": False, "value": "stable"},
                {"name": "dbPassword", "isPassword": True, "value": "********"},
            ]})
        elif path.startswith("/rest/api/latest/dependency/search/"):
            self.send_json({"error": "forbidden"}, 403)
        elif path == "/rest/api/latest/deploy/project/forPlan":
            self.send_json({"deploymentProjects": []})
        else:
            self.send_json({"error": "not found: " + path}, 404)


def run_helper(env, *argv):
    proc = subprocess.run(
        [sys.executable, HELPER, *argv],
        capture_output=True, text=True, env=env, timeout=60,
    )
    assert TOKEN not in proc.stdout, "TOKEN LEAKED TO STDOUT"
    assert TOKEN not in proc.stderr, "TOKEN LEAKED TO STDERR"
    return proc


def redirect_tests():
    """The PAT follows a redirect only on the same host.

    Server A answers /info with a redirect to its own /info-real
    (same host: the token must be kept, or the hop fails with 401),
    which redirects on to server B on another port (a different
    host: B must see no Authorization header at all).
    """
    seen = {}

    class BHandler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            seen["b_authorization"] = self.headers.get("Authorization")
            body = json.dumps({"version": "12.1.0", "buildNumber": "120100"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server_b = HTTPServer(("127.0.0.1", 0), BHandler)
    port_b = server_b.server_address[1]
    threading.Thread(target=server_b.serve_forever, daemon=True).start()

    class AHandler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def redirect(self, location):
            self.send_response(302)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            port_a = self.server.server_address[1]
            if parsed.path == "/rest/api/latest/info":
                self.redirect(f"http://127.0.0.1:{port_a}/rest/api/latest/info-real")
            elif parsed.path == "/rest/api/latest/info-real":
                if self.headers.get("Authorization") != "Bearer " + TOKEN:
                    body = b'{"error": "unauthorized"}'
                    self.send_response(401)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                seen["a_real_authorization"] = self.headers.get("Authorization")
                self.redirect(f"http://127.0.0.1:{port_b}/rest/api/latest/info")
            elif parsed.path == "/rest/api/latest/currentUser":
                body = json.dumps({"name": "test-user", "fullName": "Test User"}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

    server_a = HTTPServer(("127.0.0.1", 0), AHandler)
    port_a = server_a.server_address[1]
    threading.Thread(target=server_a.serve_forever, daemon=True).start()

    env = dict(os.environ)
    env["BAMBOO_BASE_URL"] = f"http://127.0.0.1:{port_a}"
    env["BAMBOO_PAT"] = TOKEN
    p = run_helper(env, "check")
    assert p.returncode == 0, p.stderr
    assert seen.get("a_real_authorization") == "Bearer " + TOKEN, seen
    assert seen.get("b_authorization") is None, seen
    server_a.shutdown()
    server_b.shutdown()
    print("redirect credential rules OK")


def main():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    env = dict(os.environ)
    env["BAMBOO_BASE_URL"] = f"http://127.0.0.1:{port}"
    env["BAMBOO_PAT"] = TOKEN

    # check
    p = run_helper(env, "check")
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout)
    assert data["info"]["version"] == "12.1.0"
    assert data["currentUser"]["name"] == "test-user"
    print("check OK")

    # history: window 90 days -> 3 runs (the 200-day one excluded from window count but sampled)
    p = run_helper(env, "history", "PROJ-PLAN", "--days", "90")
    assert p.returncode == 0, p.stderr
    stats = json.loads(p.stdout)
    assert stats["runs"] == 3, stats
    assert stats["successful"] == 1 and stats["failed"] == 2, stats
    assert stats["currentFailureStreak"] == 2, stats
    assert stats["durationSeconds"]["count"] == 3, stats
    assert stats["durationSeconds"]["median"] == 1800.0, stats
    print("history OK", stats["successRate"], stats["durationSeconds"])

    # specs outline
    p = run_helper(env, "specs-outline", "PROJ-PLAN")
    assert p.returncode == 0, p.stderr
    outline = json.loads(p.stdout)
    assert any(t.startswith("scheduled") for t in outline["triggers"]), outline
    assert any(t.startswith("remote") for t in outline["triggers"]), outline
    tasks = outline["jobTasks"]["Build Job"]
    assert tasks == ["checkout", "script", "maven3", "junit-parser"], tasks
    print("specs-outline OK", tasks)

    # specs: the YAML must come out of the JSON envelope (spec.code),
    # not be the raw response body
    p = run_helper(env, "specs", "PROJ-PLAN")
    assert p.returncode == 0, p.stderr
    assert p.stdout == SPECS_YAML, p.stdout[:200]
    print("specs envelope OK")

    # specs fallback: first attempt (application/json) gets 406,
    # the */* retry must succeed
    p = run_helper(env, "specs-outline", "PROJ-STRICT")
    assert p.returncode == 0, p.stderr
    outline = json.loads(p.stdout)
    assert outline["jobTasks"]["Build Job"] == ["checkout", "script", "maven3", "junit-parser"], outline
    print("specs 406 fallback OK")

    # variables: names only
    p = run_helper(env, "variables", "PROJ-PLAN")
    assert p.returncode == 0, p.stderr
    v = json.loads(p.stdout)
    names = {x["name"]: x["isPassword"] for x in v["variables"]}
    assert names == {"releaseChannel": False, "dbPassword": True}, names
    print("variables OK")

    # dossier (dependency endpoints return 403 and must be tolerated)
    outdir = "/tmp/bamboo-dossier-test"
    subprocess.run(["rm", "-rf", outdir])
    p = run_helper(env, "dossier", "PROJ-PLAN", "--out", outdir, "--days", "90")
    assert p.returncode == 0, p.stderr
    for name in ("plan.json", "specs.yaml", "branches.json", "artifacts.json",
                 "variables.json", "dependencies.json", "deploy-for-plan.json",
                 "history-stats.json", "dossier.md"):
        assert os.path.exists(os.path.join(outdir, name)), name
    assert not os.path.exists(os.path.join(outdir, "variables-raw.json"))
    with open(os.path.join(outdir, "variables.json")) as f:
        variables_text = f.read()
    assert '"value"' not in variables_text and "stable" not in variables_text, variables_text
    saved_names = {x["name"]: x["isPassword"] for x in json.loads(variables_text)["variables"]}
    assert saved_names == {"releaseChannel": False, "dbPassword": True}, saved_names
    with open(os.path.join(outdir, "specs.yaml")) as f:
        assert f.read() == SPECS_YAML
    with open(os.path.join(outdir, "dossier.md")) as f:
        md = f.read()
    assert TOKEN not in md
    assert "scheduled" in md and "script" in md and "dbPassword" in md
    deps = json.load(open(os.path.join(outdir, "dependencies.json")))
    assert "error" in deps["parent"], deps
    print("dossier OK")

    # redirects: the token stays on the same host and stops there
    redirect_tests()

    # missing env -> exit 3
    env2 = dict(os.environ)
    env2.pop("BAMBOO_BASE_URL", None)
    env2.pop("BAMBOO_PAT", None)
    p = subprocess.run([sys.executable, HELPER, "check"], capture_output=True, text=True, env=env2)
    assert p.returncode == 3, p.returncode
    print("config error OK")

    server.shutdown()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
