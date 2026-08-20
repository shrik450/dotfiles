# /// script
# requires-python = ">=3.13"
# dependencies = ["python-dotenv"]
# ///
"""Download an E2E run's eval_output artifact and unzip it.

Usage: pull_artifact.py <repo> <run_id> <dest_dir> [artifact_name]
"""

import io
import json
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

from dotenv import load_dotenv

# Prefer an already-exported token; otherwise read the main clone's .env.
if not os.environ.get("ALLSPICE_AUTH_TOKEN"):
    load_dotenv("/Users/shrik450/Developer/connections-checker/.env")

HUB = "https://genai-eval.allspice.dev"
ORG = "AI-Evals"


def api(path: str) -> bytes:
    request = urllib.request.Request(
        HUB + path,
        headers={"Authorization": f"token {os.environ['ALLSPICE_AUTH_TOKEN']}"},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop at the redirect so the token is not sent to the storage host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        raise _Redirected(newurl)


class _Redirected(Exception):
    def __init__(self, location: str) -> None:
        self.location = location


def download(path: str) -> bytes:
    """Fetch a Hub download URL, following one redirect without the token."""
    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(
        HUB + path,
        headers={"Authorization": f"token {os.environ['ALLSPICE_AUTH_TOKEN']}"},
    )
    try:
        with opener.open(request, timeout=600) as response:
            return response.read()
    except _Redirected as redirect:
        with urllib.request.urlopen(redirect.location, timeout=600) as response:
            return response.read()


def main() -> int:
    repo, branch, dest = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    wanted = sys.argv[4] if len(sys.argv) > 4 else "eval_output"

    tasks = json.loads(api(f"/api/v1/repos/{ORG}/{repo}/actions/tasks"))
    task = next(
        (run for run in tasks["workflow_runs"] if run["head_branch"] == branch), None
    )
    if task is None:
        print(f"no run for {repo} branch {branch}")
        return 1
    head_sha = task["head_sha"]
    print(f"{repo} {branch}: run#{task['run_number']} {task['status']} sha={head_sha[:10]}")

    listing = json.loads(api(f"/api/v1/repos/{ORG}/{repo}/actions/artifacts"))
    matches = [
        artifact
        for artifact in listing["artifacts"]
        if artifact["name"] == wanted
        and artifact["workflow_run"].get("head_sha") == head_sha
        and not artifact["expired"]
    ]
    if not matches:
        print(f"no {wanted} artifact for {repo} {branch}")
        return 1

    artifact = matches[0]
    print(f"downloading {artifact['name']} {artifact['size_in_bytes']:,} bytes")
    blob = download(f"/api/v1/repos/{ORG}/{repo}/actions/artifacts/{artifact["id"]}/zip")
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        archive.extractall(dest)
    print(f"extracted to {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
