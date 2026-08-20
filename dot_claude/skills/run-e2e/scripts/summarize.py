# /// script
# requires-python = ">=3.13"
# dependencies = ["py-allspice>=4.0.0", "python-dotenv"]
# ///
"""Compact per-run summary of an E2E design review on genai-eval.

Parses the rubric judge comment and the metrics-index comment into a few
lines so many runs can be compared without reading full comment bodies.

Usage: summarize.py <repo> <dr_number> [<repo> <dr_number> ...]
"""

import os
import re
import sys

from allspice import AllSpice
from dotenv import load_dotenv

# Prefer an already-exported token; otherwise read the main clone's .env.
if not os.environ.get("ALLSPICE_AUTH_TOKEN"):
    load_dotenv("/Users/shrik450/Developer/connections-checker/.env")

HUB = "https://genai-eval.allspice.dev"
ORG = "AI-Evals"

METRIC_KEYS = (
    "Tokens",
    "Runtime",
    "Peak memory",
    "Pages reviewed",
    "Components analyzed",
    "Findings reported",
    "Datasheets attached",
)
BUCKETS = {
    "possibly real": "possibly_real",
    "subjective": "subjective",
    "likely false positives": "false_positive",
    "unverified": "unverified",
}
BAND_ROWS = (
    "Total tokens",
    "Output tokens",
    "Error groups",
    "Runtime (s)",
    "Datasheets used",
    "Component count",
    "Components w/ issues",
)


def bucket_counts(body: str) -> dict[str, int]:
    counts = {name: 0 for name in BUCKETS.values()}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("### "):
            current = None
            for label, key in BUCKETS.items():
                if label in line:
                    current = key
            continue
        if current and line.startswith("- "):
            counts[current] += 1
    return counts


def run_metrics(body: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for match in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$", body, re.M):
        key, value = match.group(1).strip(), match.group(2).strip()
        if key in METRIC_KEYS:
            metrics[key] = value
    return metrics


def band_table(body: str) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for line in body.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            continue
        name = cells[0]
        stem = name.split("†")[0].strip()
        if stem not in BAND_ROWS:
            continue
        rows.append((stem, cells[1], cells[4], cells[5]))
    return rows


def summarize(api: AllSpice, repo: str, number: str) -> None:
    pull = api.requests_get(f"/repos/{ORG}/{repo}/pulls/{number}")
    comments = api.requests_get(f"/repos/{ORG}/{repo}/issues/{number}/comments")
    print(f"\n##### {repo}#{number} :: {pull['title']}")
    print(f"      created={pull['created_at'][:16]} comments={len(comments)}")

    judge = next((c for c in comments if "## Rubric judge review" in c["body"]), None)
    metrics_comment = next(
        (c for c in comments if "| Metric | Target | Band median" in c["body"]), None
    )
    review_comments = [
        c
        for c in comments
        if c is not judge and c is not metrics_comment and len(c["body"]) > 200
    ]
    print(f"      other long comments={len(review_comments)}")

    if judge is None:
        print("      NO JUDGE COMMENT")
    else:
        body = judge["body"]
        caught = body.count("Caught ✅")
        missed = body.count("Missed ❌")
        print(f"      rubric: caught={caught} missed={missed}")
        print(f"      unmatched: {bucket_counts(body)}")
        metrics = run_metrics(body)
        print(
            "      run: "
            + ", ".join(f"{key}={metrics.get(key, '?')}" for key in METRIC_KEYS)
        )

    if metrics_comment is None:
        print("      NO METRICS COMMENT")
    else:
        for name, target, delta, verdict in band_table(metrics_comment["body"]):
            flag = "OUTSIDE" if "OUTSIDE" in verdict else "inside"
            print(f"      band {name:<22} target={target:<12} delta={delta:<14} {flag}")


def main() -> int:
    token = os.environ["ALLSPICE_AUTH_TOKEN"]
    api = AllSpice(allspice_hub_url=HUB, token_text=token)
    args = sys.argv[1:]
    for repo, number in zip(args[::2], args[1::2]):
        try:
            summarize(api, repo, number)
        except Exception as exc:
            print(f"\n##### {repo}#{number} FAILED: {type(exc).__name__} {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
