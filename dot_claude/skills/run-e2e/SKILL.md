---
name: run-e2e
description: Run and follow connections-checker end-to-end (E2E) evaluation runs on the genai-eval AllSpice Hub, then compare them against main baselines. Use when asked to run E2Es, kick off eval runs, follow an E2E round, or check a branch for review regressions.
disable-model-invocation: true
---

# Run and follow connections-checker E2Es

End-to-end (E2E) runs review real designs on the genai-eval AllSpice Hub and
grade the result. One round costs real money and 15 to 25 minutes per repo, so
read this whole file before dispatching.

Helper scripts live in `scripts/` next to this file. They are read-only except
where noted. Copy them to a scratch directory and run them with
`uv run --no-project <script>`.

## Preconditions

1. **Push the ref to GitHub first.** The injected workflow pins the action to
   `connections-checker@<ref>`. An unpushed commit cannot resolve.
2. **Use the full 40-character SHA**, from `git rev-parse HEAD`. An abbreviated
   SHA makes every run fail in about 30 seconds. A branch name also works.
3. Run local checks first: `uv run pyright --warnings` and the offline test
   suite. Do not spend a round on a type error.
4. Validate the rendered workflow without touching the Hub:
   `uv run --no-project scripts/run_e2e_manual.py --ref <sha> --dry-run`.
   The Hub silently ignores unparseable workflow files, so this matters.

## Dispatch

```sh
gh workflow run e2e_manual.yml -R AllSpiceIO/connections-checker \
  -f ref=<full-40-char-sha> -f filter='' -f cache=true
```

- `filter=''` runs all four repos. `-f filter='Archimajor'` runs one.
- Keep `cache=true`. Turning the datasheet cache off adds cost and variance.
- Dispatch on GitHub, not locally: the eval-server token stays a repo secret.
- Read the design review URLs from the dispatch log:
  `gh run view <run-id> -R AllSpiceIO/connections-checker --log | grep -A6 "Kickoff results"`.

## The four test repos

| Repo | Format | Pages reviewed | Notes |
|---|---|---|---|
| E2E-Archimajor | Altium | 4 | Ports and no-connects carry net IDs |
| E2E-Mikoto | KiCad | 1 | `preferred_part_number_attribute: LCSC Part` |
| E2E-Parallella | SDAX | 5 | |
| E2E-Turbot | DxDesigner | 3 | Page selection pins pages 20, 22, 25 |

Design files, if you need to probe the generated JSON: `Archimajor.PrjPcb`,
`mikoto.kicad_sch`, `parallella.sdax`, `Turbot.prj`.

## Following the runs

The Hub needs a token. `ALLSPICE_AUTH_TOKEN` sits in the main clone's `.env`
(`/Users/shrik450/Developer/connections-checker/.env`). Load it with
python-dotenv. Never print it.

```sh
uv run --no-project scripts/hub.py tasks E2E-Archimajor   # run status per repo
uv run --no-project scripts/hub.py drs 14                 # recent E2E reviews
uv run --no-project scripts/hub.py comments E2E-Mikoto 43 # full comment bodies
```

Match a run to its design review by the `branch=#<dr-number>` field. Poll every
90 to 120 seconds in a background shell; do not block the session.

**There is no log API.** Gitea 1.24 on this Hub exposes no job-log endpoint,
and the web log route needs a session cookie, not a token. When a run fails
early, ask the user to paste the failing step from the run page.

## Reading results

Each design review self-reports. Do not build new tooling.

1. **Rubric judge comment** — per-item `Caught ✅` or `Missed ❌`, unmatched
   findings split into "possibly real", "subjective", "likely false positives",
   and "unverified", plus a Run metrics table (tokens, runtime, peak memory,
   pages reviewed, components analyzed, findings reported, datasheets attached).
2. **Metrics index comment** — target against that repo's recent history with a
   P10 to P90 band and an `inside` or `OUTSIDE` verdict per metric.
3. **Verifier confidence** — per-claim verdicts, uploaded as its own artifact.

`scripts/summarize.py E2E-Archimajor 29 E2E-Mikoto 40 ...` prints one compact
block per run: caught and missed counts, bucket counts, run metrics, and every
banded metric. Use it instead of reading comment bodies.

## Baselines

Do not trigger main runs. Every push to `main` already fires a full round, so
recent baselines exist. Find them with `hub.py drs` and read the ref out of the
title (`E2E @ <ref8> - push to main`). Take four, including the branch's merge
base.

Run-to-run variance is large. Recent Archimajor main runs caught 7, 7, 7, and 6
of 8 rubric items, reported 26, 26, 19, and 17 findings, and used 6.7M to 11.0M
input tokens. Judge a single run against that spread, not against one baseline.
Turbot's band is polluted by pre-trim history, so its band verdicts mean little.

## Artifacts and reasoning traces

```sh
uv run --no-project scripts/pull_artifact.py E2E-Archimajor '#29' ./out
uv run --no-project scripts/pull_artifact.py E2E-Archimajor '#29' ./out verifier_confidence
```

Two traps this script already handles: the artifacts listing keys runs by
`head_sha`, not by the task id from `actions/tasks`; and the zip download
redirects to storage, which rejects the token header.

Layout of `eval_output`:

```
output.json                  final findings
metrics.jsonl                every telemetry metrics event
debug_dump/<timestamp>/
  pages/<PageName>/
    input.txt                exact rendered page text the model saw
    page.json                full page JSON, includes ports and no_connects
    selection.md             which components the director picked
    error_grouping.md
    groups/                  per-group reviews, including model reasoning
    postdoc/
  datasheets/                extracted specs, plus index.md
  README.md, metadata.md
```

`input.txt` is the highest-value file. Diffing it between a baseline run and a
new run shows exactly what the change fed the model.

**Delegate the reasoning review.** The `pages/` tree runs to about 13 MB per
run. Send a subagent at it with a precise question, and keep the conclusion, not
the file dumps. Sonnet handles the grep-and-cross-reference work.

## Judging the round

State up front what should change. For a change that only affects one format,
three repos moving inside the noise band is the pass condition, not a
disappointment.

Gates worth checking:

- Every workflow finished, and the checker step succeeded.
- Caught rubric items sit inside the baseline spread per repo.
- The "likely false positives" bucket did not grow.
- Tokens and runtime sit inside the band. Note that added page content raises
  tokens by design.
- The feature actually engaged: grep the new `input.txt` for the new content. If
  it never appears, the round only proves no regression. Say so plainly.

## Known failure modes

| Symptom | Cause | Action |
|---|---|---|
| All repos fail in about 30s | Abbreviated ref | Re-dispatch with the full SHA |
| One repo fails in under 60s, `Set up uv` step | Corrupted `act` cache on that runner: `lstat /root/.cache/act/.../__tests__/helpers` | Runner-side. Re-dispatch that repo alone |
| Design review created, no task appears | Runners are busy | Wait. Do not re-dispatch; you only lengthen the queue |
| No artifacts and no comments | The job died before the `always()` steps | Read the step log from the run page |

## Cleanup

Runs auto-close after 7 days, and the next kickoff closes stale reviews. Close
anything you created by mistake yourself: `PATCH /pulls/<n> {"state":"closed"}`,
then `DELETE /branches/<head-ref>`. Delete scratch scripts and downloaded
artifacts when the task ends.
