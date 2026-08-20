---
name: multi-agent-pr-review
description: Build a review GUIDE for a PR by dispatching parallel subagents across distinct review concerns (style, correctness, testing, design), then synthesizing into a pre-read brief. Use when the user wants the up-front investigation done so they can review faster — NOT to substitute for their review. Output is a guide for the user, never a ready-to-post review.
disable-model-invocation: true
---

# Multi-agent PR review

Used when the user wants a deep, structured pre-read of a PR or branch and wants
the workload divided across parallel subagents. The orchestrator (you) does
**none** of the review itself — it primes, dispatches, and produces a **review
guide** that helps the user write their own review faster.

## Default ground rules

- **The output is a review GUIDE, not a review.** The user will read the PR
  themselves and write their own comments. Your job is to surface the right
  places to look and the right questions to bring — not to pre-write verdicts.
- **No verdicts in the output.** Don't classify findings as "blocker / must-fix
  / nit" — that's the user's call. Frame things as "worth a look", "open
  question", "suspicion", "what's there + what could go wrong".
- **No posted comments.** Do NOT post review comments via `gh` or any other API
  unless the user explicitly says to. Output goes inline in the conversation.
- **No edits to the branch.** This is a read-only exercise.
- **Subagents are isolated.** Each downstream agent only sees its prompt — bake
  all required context into the prompt.
- **IMPORTANT: Verbosity is bad!** Since this is a guide, not a full review, you
  should make the output simple and direct. The output guide should be clear and
  easy to get through. If the output has more tokens than the original PR diff,
  it's a bad guide!

## Step 1 — Identify the target

If the user gave a PR number, use that. Otherwise:

```sh
gh pr list --head $(git branch --show-current) --json number,title,url,body,state
git log --oneline main..HEAD
git diff main...HEAD --stat
```

Record: PR number, branch, base, list of changed files, the two-or-more commits
if the PR has multiple revisions (so you can ask the primer to diff between them
and identify what the latest commits addressed).

## Step 2 — Run a single PRIMER agent

Spawn ONE general-purpose agent (sequential, not parallel) whose only job is to
write `/tmp/pr<NUM>_primer.md`. The downstream agents will all read this — it
must be factual, no opinions.

The primer prompt must require:

1. **Purpose & motivation** from the PR body
   (`gh pr view <NUM> --json body,title,url`). If the body links to Notion or a
   ticket, note it but don't try to fetch external systems.
1. **High-level narrative** of what changed (one paragraph, not a file list).
1. **File-by-file map** with `path:line` citations and a few sentences each on
   what & why.
1. **Key concepts** the reviewers must understand — pull definitions from the
   actual code, not from outside knowledge.
1. **Points of interest** — non-obvious bits, new patterns, places where a
   follow-up commit addressed earlier feedback (diff between commits
   explicitly).
1. **Test inventory** — list new/modified test functions, no critique.
1. **Existing review comments** —
   `gh api repos/<owner>/<repo>/pulls/<NUM>/comments` and
   `gh pr view <NUM> --comments`. Include what's already raised so reviewers
   don't repeat.

Tell the primer to be FACTUAL — no judgments. Aim for ~400-1000 lines.

When it returns, ask for a 5-bullet TL;DR so you can sanity-check the primer
captured the right things.

## Step 3 — Dispatch four parallel investigation agents

In a SINGLE message with four `Agent` tool calls (parallel), spawn:

### 3a. Style & CLAUDE.md adherence

A higher-level linter that catches what `ruff` / `pyright` cannot:

- Type holes (`Any` smuggled, `# type: ignore` without justification, `cast`
  papering over bugs, dicts where typed models belong)
- Comment policy violations (per global CLAUDE.md — comments only for
  non-obvious WHY)
- Naming smells (`_v2`, `_new`, generic names like `data`/`result`)
- Imports not at top of file (project rule)
- Hard-cutover violations (backwards-compat shims, fallbacks, feature flags not
  requested)
- Type hints missing on functions (including helpers and tests)
- Defensive coding violating "trust internal code" (validation at
  non-boundaries)
- Test ergonomics (`@pytest.mark.asyncio` if AUTO mode, no `check_*` helpers,
  missed `parametrize`)

Have it read both `~/.claude/CLAUDE.md` and the project `CLAUDE.md` first.

### 3b. Correctness

Reason DEEPLY about behavior. Look for:

- Logic bugs, off-by-ones, swapped args, wrong default
- Concurrency / async issues (missing `await`, sync in async)
- Error handling: silently swallowed, over-broad, partially-populated state
- API misuse: wrong call signature, untyped JSON indexed without shape check
- State / mutability: shared mutation, lost mutations, ref-vs-copy
- Data flow: trace new state end-to-end through every consumer
- Edge cases the code doesn't handle
- Regression risk vs. prior behavior — REQUIRE the agent to use `git log -p`,
  `git blame`, and `git diff <prev_commit>..<latest_commit>` to understand
  evolution, not just the current state
- Coupling between commits in the PR
- External invariants (what does the API actually return? Check docs / `.venv`
  source)

Each finding should walk through the suspicious execution path explicitly. The
agent's job is to surface things worth a closer look — not to issue verdicts.

### 3c. Tests, coverage, and edge cases

Think like a mutation tester:

- Coverage gaps: list specific lines/branches with no test
- Surviving mutations: name specific mutations and whether the suite catches
  them
- Edge cases not covered (enumerate every plausible one)
- Brittleness: tests over-coupled to internal calls, log-string assertions,
  ossifying snapshots
- Missing `parametrize` / `check_*` helper opportunities (4+ near-identical
  tests)
- Test feature, not implementation (Neural Network Test from matklad)
- Observable internal state that should be asserted
- Per-project rules (e.g. `pytest-asyncio` AUTO mode means no
  `@pytest.mark.asyncio`)

### 3d. Design & code quality (highest signal)

This agent must FIRST read
`~/.claude/skills/multi-agent-pr-review/user-review-style.md` — a pre-mined
reference distilled from ~70 of the user's real review comments. **Use it to
learn WHAT KINDS of design concerns the user prioritizes** (type holes,
over-plumbing, layering, dead state, dict boundaries, etc.) — NOT to mimic their
voice. Findings will be re-framed as a guide, not posted in the user's voice.
**Do not refetch reviews from GitHub** — the reference exists exactly so this
work is done once. (If the file is ever missing or looks stale, see "Refreshing
the style guide" below.)

Then surface design concerns the user might want to raise:

- Right abstraction level — is state plumbed through layers it doesn't need?
- Clarity of intent — does a cold reader understand the new function from names
  \+ structure?
- Coupling — do unrelated concerns get mixed (e.g., business rules into a
  serializer)?
- Symmetry with surrounding code (idioms, return shapes, logging patterns)
- Names — `selected_` vs `resolved_` vs `effective_`, generic vs purposeful
- Function decomposition — too much in one function vs. over-split
- Data shapes — typed models vs. dicts at boundaries
- API design — return type, exception type, log level
- Configurability — defaults, CLI consistency, where precedence is documented
- Missing observability hooks
- Prompt content (if the PR touches LLM prompts) — ambiguity, internal
  contradiction, drift across multiple sites

The agent should describe each finding as **what's there + why it might be a
problem + an alternative worth considering**, not as a polished comment.
Citations (`path:line`, quoted snippets) are required because the user will use
them to drill in.

## Step 4 — Synthesize as a review guide

Read all four `/tmp/pr<NUM>_review_*.md` files. Produce a REVIEW GUIDE —
material that helps the user form their own review, not a substitute for it.

### What a review guide IS vs IS NOT

**IS:**

- A 2-minute orientation so the user knows the PR's shape and what kind of
  attention it needs
- A top of the line "how this works" that walks through the PR's purpose, data
  flow, architectural changes and key concepts — the substrate for understanding
  the details. This helps the user "sanity check" and quickly know the approach
  taken before they dig into details.
- A map of hotspots (specific places worth attention) framed as **what's there +
  what to check + open questions**
- Cross-cutting observations the user might want to raise as design conversation
- A "verified fine" section so the user can skip what's already been traced
- A dossier with full per-area details for drill-down — same depth as the raw
  findings, just organized for consumption

**IS NOT:**

- A consolidated review the user could copy-paste
- A list of "must-fix / should-fix / nit" verdicts (those are the user's calls —
  pre-classifying steals their judgment)
- A polished sequence of comments in the user's voice
- A list of suggested rewrites (unless the suggestion IS the finding, e.g. a
  prompt edit)

### Tone for the guide

Frame findings neutrally:

- "Worth a careful look at X" / "X has the following moving parts and a
  non-obvious interaction" / "Open question: …"
- NOT "X is wrong" / "Must fix" / "This should be Y"

Facts ("this branch has no test", "this kwarg is forwarded but never read") are
fine — they don't need softening. Verdicts ("this is a blocker", "the design is
wrong") aren't.

### Suggested structure

```
## At a glance
1-2 sentences on purpose and scope, then 1 sentence on the PR's shape (small/large,
surgical/sprawling, single-concern/multi-concern), then 1 sentence on the kind of
attention this needs ("design-heavy with one bug-suspicious area", "mostly mechanical
plumbing", "prompt changes deserve the most thought", etc.).

## Author asked for feedback on
- Verbatim asks from the PR body or commits, with file/line pointers.
- Don't answer the asks here — they're flagged so the user knows to focus there.

## Hotspots
For each (3-7 of them, ordered by where the highest-leverage discussion is likely):

### N. [hotspot title — what's at issue, neutrally]
**Where**: path:line (and related sites if it spans files)
**What's there**: 1-3 sentences describing the change at this site
**Worth checking**: 1-3 specific things to verify or think about
**Open questions for the author** (if any): 0-2 questions, framed as questions
**If this is wrong**: 1 line on the cost / blast radius

## Cross-cutting observations
Patterns visible across the diff that don't live in one place — layering choices,
plumbing decisions, prompt drift across sites, naming consistency. These usually
become design conversations, not single comments.

## Verified fine (skip these)
- One-liners on things the agents traced and confirmed work correctly. Give the
  user permission to NOT re-verify.

## Dossier
Per-area deep-dive details, organized by hotspot or by file. Same depth as the
raw findings — citations, quoted snippets, full reasoning — but structured so the
user only reads the section they're drilling into.
```

### What to drop from the agents' raw findings when synthesizing

- Severity verdicts ("blocker", "must-fix", "important")
- Long lists of nits — pull the 2-3 with real signal into a hotspot or
  cross-cutting note, fold the rest into the dossier
- Pre-written suggested rewrites (unless the suggestion IS the entire finding,
  e.g. a prompt edit the author asked for feedback on)
- Performative positives ("Worth keeping" applause sections) — the "Verified
  fine" section serves the actual goal

### What to keep

- Concrete `path:line` citations everywhere
- The technical reasoning behind each hotspot — that's what helps the user form
  a view
- Author asks at the top, prominently
- Cross-cutting design observations as their own section
- The dossier's full depth — when the user drills in, they want the details

## Step 5 — Stop

Output the review guide inline. Do NOT:

- Post anything to GitHub
- Edit any files in the repo
- Pre-write the user's review comments

The user will read the PR themselves. The guide exists to make that work easier,
not replace it.

## What the user actually flags

From mining real reviews, the user typically writes **5-10 short comments** on a
meaningful PR, mostly inline. Their actual top-level review is often two
sentences. They classify in their *own* head as they go (a `nit:` prefix here, a
"blocking question" there, a 👍 elsewhere). The guide should give them the
substrate to make those calls — not pre-make them.

Concrete pattern from past reviews:

- 1 top-level concern stated in 1-2 sentences (often a design pushback or a
  single bug)
- 4-6 inline comments, each 1-3 sentences, mostly questions or specific
  suggestions
- 1-2 explicit nits with a `nit:` prefix
- Occasionally a 👍 on something they liked
- They skip: most testing-coverage-by-line, most style nits, performative
  positives

So the guide should let them scan in 2 minutes, drill into 3-5 hotspots, and
walk into the PR with questions rather than verdicts pre-loaded.

## Refreshing the style guide

`user-review-style.md` is a snapshot. Refresh it when:

- The user's review style has visibly shifted (they tell you, or the synthesis
  feels off).
- It's been ~6 months and many new PRs have accumulated.
- The user explicitly asks to refresh it.

To refresh: dispatch a single subagent with the original mining prompt (PRs
authored by *others* in the user's primary repo, fetch
reviews+comments+issue-comments by the user via `gh api`, aim for ~70 distinct
comments across ~10+ PRs, output structured guide with verbatim quotes).
Overwrite the file in place.

DO NOT refetch live during a normal review run — the cached guide is the whole
point.

## When to deviate

- **Small PR (< 5 files, single concern):** Skip the four-way split. One
  general-purpose agent doing all four passes is enough. The split's overhead
  exceeds its value below ~200 lines of diff. Output is still a guide, not a
  review.
- **PR with no tests:** Drop the testing agent and have the design agent flag
  the lack-of-tests in its findings instead.
- **Pure-doc PR:** The four-way split is wrong. Just read it yourself and tell
  the user what's there.
- **User explicitly wants a posted review (not a guide):** This is a strong
  deviation — the default is guide-only. Confirm what they want explicitly
  before reshaping the synthesis. If they confirm, the synthesis can become a
  draft review in their voice (consult `user-review-style.md`); even then, show
  the draft and confirm before any `gh pr review` call.
