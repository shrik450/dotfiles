# /// script
# requires-python = ">=3.13"
# dependencies = ["py-allspice>=4.0.0", "python-dotenv"]
# ///
"""Read-only helpers for following E2E runs on genai-eval.

Subcommands:
  exts <repo>                 list file extensions in the repo tree
  probe <repo> <path>         port/no-connect summary for one generated JSON
  drs [limit]                 recent E2E design reviews per repo
  tasks <repo> [limit]        recent action tasks for a repo
  comments <repo> <number>    all comments on a design review
"""

import os
import sys
from collections import Counter
from typing import Any

from allspice import AllSpice, Repository
from dotenv import load_dotenv

# Prefer an already-exported token; otherwise read the main clone's .env.
if not os.environ.get("ALLSPICE_AUTH_TOKEN"):
    load_dotenv("/Users/shrik450/Developer/connections-checker/.env")

HUB = "https://genai-eval.allspice.dev"
ORG = "AI-Evals"
REPOS = ["E2E-Archimajor", "E2E-Mikoto", "E2E-Parallella", "E2E-Turbot"]


def client() -> AllSpice:
    token = os.environ["ALLSPICE_AUTH_TOKEN"]
    return AllSpice(allspice_hub_url=HUB, token_text=token)


def get(api: AllSpice, url: str) -> Any:
    return api.requests_get(url)


def cmd_exts(api: AllSpice, repo_name: str) -> None:
    repo = Repository.request(api, ORG, repo_name)
    data = get(
        api,
        f"/repos/{ORG}/{repo_name}/git/trees/{repo.default_branch}?recursive=true&per_page=1000",
    )
    counter = Counter(
        "." + entry["path"].rsplit(".", 1)[-1].lower()
        for entry in data.get("tree", [])
        if entry["type"] == "blob" and "." in entry["path"]
    )
    print(f"{repo_name} ref={repo.default_branch} truncated={data.get('truncated')}")
    for ext, count in counter.most_common(25):
        print(f"  {ext}: {count}")


def cmd_files(api: AllSpice, repo_name: str, suffix: str) -> None:
    repo = Repository.request(api, ORG, repo_name)
    data = get(
        api,
        f"/repos/{ORG}/{repo_name}/git/trees/{repo.default_branch}?recursive=true&per_page=1000",
    )
    for entry in data.get("tree", []):
        if entry["type"] == "blob" and entry["path"].lower().endswith(suffix.lower()):
            print(entry["path"])


def cmd_probe(api: AllSpice, repo_name: str, path: str) -> None:
    repo = Repository.request(api, ORG, repo_name)
    schematic_json = repo.get_generated_json(path, ref=repo.default_branch)
    pages = schematic_json.get("pages", [])
    print(f"{repo_name}:{path} pages={len(pages)} keys={sorted(schematic_json.keys())}")
    for kind in ("ports", "no_connects"):
        total = with_net = 0
        sample = None
        for page in pages:
            collection = page.get(kind)
            values = (
                list(collection.values())
                if isinstance(collection, dict)
                else list(collection or [])
            )
            total += len(values)
            for element in values:
                if element.get("net_id") is not None:
                    with_net += 1
                    if sample is None:
                        sample = {
                            k: v
                            for k, v in element.items()
                            if k in ("name", "net_id", "position")
                        }
        print(f"  {kind}: {total} total, {with_net} with net_id, sample={sample}")


def cmd_drs(api: AllSpice, limit: str = "12") -> None:
    for repo_name in REPOS:
        print(f"\n=== {repo_name} ===")
        pulls = get(
            api,
            f"/repos/{ORG}/{repo_name}/pulls?state=all&sort=recentupdate&limit={limit}",
        )
        for pull in pulls:
            title = pull["title"]
            if not (title.startswith("E2E @") or title.startswith("Eval @")):
                continue
            print(
                f"  #{pull['number']:>4} {pull['state']:<6} {pull['created_at'][:16]} "
                f"head={pull['head']['ref']} :: {title}"
            )


def cmd_tasks(api: AllSpice, repo_name: str, limit: str = "12") -> None:
    data = get(api, f"/repos/{ORG}/{repo_name}/actions/tasks?limit={limit}")
    for run in data.get("workflow_runs", []):
        print(
            f"  run#{run.get('run_number')} id={run.get('id')} "
            f"{run.get('status'):<12} {run.get('conclusion') or '':<10} "
            f"branch={run.get('head_branch')} started={run.get('run_started_at') or run.get('created_at')}"
        )


def cmd_comments(api: AllSpice, repo_name: str, number: str) -> None:
    comments = get(api, f"/repos/{ORG}/{repo_name}/issues/{number}/comments")
    print(f"{repo_name}#{number}: {len(comments)} comments")
    for comment in comments:
        body = comment["body"]
        print(
            f"\n----- comment {comment['id']} by {comment['user']['login']} "
            f"at {comment['created_at'][:16]} ({len(body)} chars) -----"
        )
        print(body)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    api = client()
    command, *rest = args
    match command:
        case "exts":
            cmd_exts(api, *rest)
        case "files":
            cmd_files(api, *rest)
        case "probe":
            cmd_probe(api, *rest)
        case "drs":
            cmd_drs(api, *rest)
        case "tasks":
            cmd_tasks(api, *rest)
        case "comments":
            cmd_comments(api, *rest)
        case _:
            print(f"unknown command {command}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
