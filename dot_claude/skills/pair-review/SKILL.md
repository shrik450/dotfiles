---
name: pair-review
description: Sanity-check code you've been working on (often with agents) by dispatching parallel subagents across distinct review concerns (correctness, tests, design, agent-pathologies+style), then synthesizing into a terse, pairing-voice findings list. Use when the user wants a sanity pass on uncommitted work, a feature branch before opening a PR, or a custom commit range. Output is action-oriented for the user (the AUTHOR of the code) — NOT a neutral review guide.
disable-model-invocation: true
---

# Pair review

Used when the user wants the kind of feedback a good pair would give them on code they just wrote (often with agent help): "have you missed this", "maybe not this way", "this looks wrong". The user is the AUTHOR, not a reviewer of someone else's work — so output is terse, action-oriented, and uses pairing voice. The orchestrator (you) does **none** of the review itself — it primes, dispatches, and synthesizes specialist findings into a short, scannable output.

If the user wants a guide for reviewing someone else's PR, use `multi-agent-pr-review` instead. This skill is the author-side counterpart.

## Default ground rules

- **Read-only.** No edits to files in the repo. No `gh pr review`, no posted comments, no commits.
- **Citations required everywhere.** Every finding has a `path:line` reference. No exceptions.
- **Pairing voice.** Findings are framed as the question or push a good pair would offer: "drop?", "what about redirects?", "looks like the import can't fail." Not "must-fix" or "this is wrong." Not neutral guide-voice ("worth a careful look") either — direct, terse, peer-level.
- **No reams of text.** One sentence per finding where possible. Two if the cited line genuinely needs context. The output is meant to be scanned in under a minute.
- **Subagents are isolated.** Each downstream agent only sees its prompt — bake all required context into the prompt.

## Step 1 — Build the scope card

Determine scope from the user's invocation:

- `/pair-review` (no args) → **uncommitted scope**: `git diff` + `git diff --cached` + untracked files via `git ls-files --others --exclude-standard`.
- `/pair-review branch` → **branch scope**: detect the repo's actual default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`, fallback to parsing `git symbolic-ref refs/remotes/origin/HEAD`), then `git diff <default>...HEAD`.
- `/pair-review <range>` (e.g. `HEAD~3..HEAD`, `abc123..def456`) → **custom range**: `git diff <range>`.
- `--goal "..."` flag (any mode) → user-supplied goal text overrides derivation.

Then derive the goal context (layered, first hit wins):

1. `--goal` arg if passed.
2. Recent assistant/user turns in the current conversation describing what was being worked on.
3. Commit messages in scope (`git log` over the range) + branch name.

Record which source was used so the synthesis can report it transparently. If none of the three yield a goal, that's fine — note "no goal context derived" and proceed; the agent-pathologies agent will skip the goal-drift check.

Build a scope card containing:

- Scope mode (uncommitted / branch / custom range)
- Diff stat (`git diff --stat <scope>`)
- List of changed files
- Derived goal + source-of-goal
- Default branch name (for branch mode)

This card is plain text, no separate file needed — you'll paste it into each specialist's prompt.

**Bail conditions:**

- Empty diff → output one line ("nothing in scope, exiting") and stop.
- Custom range that crosses a merge commit → warn the user but proceed.

## Step 2 — Decide collapse vs. parallel

Count the diff size:

- **≤ 150 lines OR ≤ 3 files changed** → collapse mode (Step 3a).
- **Pure-doc diff** (only `.md` / `.txt` / `.rst` files) → doc mode (Step 3b).
- **Otherwise** → parallel mode (Step 3c).

## Step 3a — Collapse mode (small diffs)

Spawn ONE general-purpose agent that does all four passes inline. Its prompt includes the full scope card, the diff, paths to `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and `~/.claude/skills/multi-agent-pr-review/user-review-style.md`. It writes findings directly to a single file `/tmp/pair_review_<scope-hash>_combined.md`.

The agent must produce findings in the same format the parallel specialists use (see Step 3c) — `path:line — push`, pairing voice, citations required.

For very small diffs, also have this agent produce the "How this change works" narrative inline at the top of its output.

Skip Step 4's narrator dispatch in collapse mode.

## Step 3b — Doc mode (pure-doc diffs)

The four-way split is wrong here. Read the diff yourself. Produce a one-paragraph "what changed" summary plus any clarity, accuracy, or contradiction concerns. Use the same pairing voice and `path:line` citations. Output inline. Stop.

## Step 3c — Parallel mode (full pipeline)

In a SINGLE message with FIVE `Agent` tool calls (parallel), spawn:

### 3c.i. Narrator (only if diff is large)

Only dispatch a narrator subagent if the diff exceeds **~500 lines OR ~10 files changed**. For smaller-but-not-tiny diffs, you'll write the narrative yourself at synthesis time — it's cheaper and you already have the diff in context.

When dispatched, the narrator's only job is to write `/tmp/pair_review_<scope-hash>_narrative.md`. The prompt requires:

- Read the diff. Trace the change end-to-end through the codebase as it now stands.
- Output 2-5 sentences. Cite `path:line` for each load-bearing claim.
- No findings, no opinions. Just the story of what now happens — entry points, where new state flows, what the change replaces.
- If a flow is unclear, say so explicitly. Don't paper over.

The narrator does NOT block the specialists — it runs in parallel.

### 3c.ii. Correctness

Reason about behavior, not surface. Hunt for:

- Logic bugs, off-by-ones, swapped args, wrong default
- Async issues (missing `await`, sync-in-async, unawaited coroutines)
- Error handling: silently swallowed, over-broad, partially-populated state on failure
- API misuse: wrong call signature, untyped JSON indexed without shape check
- State / mutability: shared mutation, lost mutations, ref-vs-copy
- Data flow: trace new state end-to-end through every consumer
- Edge cases the code doesn't handle
- For `branch` mode: regression risk vs. prior behavior — use `git log -p` and `git blame` to understand evolution

Each finding walks through the suspicious execution path explicitly. Output to `/tmp/pair_review_<scope-hash>_correctness.md`.

### 3c.iii. Tests

Think like a mutation tester, weight specifically toward agent failure modes:

- **Tautological tests**: mocking the SUT, asserting the mock was called, trivially-true assertions, tests that pass without exercising the new code
- Coverage gaps on edge cases (enumerate plausible ones)
- Brittleness: tests over-coupled to internal calls, log-string assertions, ossifying snapshots
- Missed `parametrize` / `check_*` helper opportunities (4+ near-identical tests)
- Test feature, not implementation (Neural Network Test from matklad)
- Observable internal state that should be asserted
- Project rules (e.g. pytest-asyncio AUTO mode → no `@pytest.mark.asyncio`)

Output to `/tmp/pair_review_<scope-hash>_tests.md`.

### 3c.iv. Design & code quality

This agent must FIRST read `~/.claude/skills/multi-agent-pr-review/user-review-style.md` — a pre-mined reference distilled from the user's real review comments. Use it to learn what kinds of design concerns the user prioritizes. **Do not refetch reviews from GitHub.**

Then surface, with explicit attention to **clarity** and **elegance**:

- **Clarity**: a cold reader should grasp intent from names + structure without reading internals. Hidden state, surprise mutations, non-linear control flow, signatures that don't tell you what the function does.
- **Elegance**: the solution should fit the problem. Indirection that doesn't earn its keep, wrong-tool choices (explicit loop where a comprehension is clearer, dict where a dataclass belongs), missing symmetry between parallel cases, code that reads as fighting the problem rather than expressing it.
- Wrong abstraction level — state plumbed through layers it doesn't need
- Coupling — unrelated concerns mixed (e.g. business rules into a serializer)
- Symmetry with surrounding code (idioms, return shapes, logging patterns)
- Names — `selected_` vs `resolved_` vs `effective_`, generic vs purposeful
- Function decomposition — too much in one function vs. over-split
- Data shapes — typed models vs. dicts at boundaries
- Type holes (`Any` smuggled, `# type: ignore` papering over bugs, `cast` covering bugs)
- Configurability and observability gaps
- Prompt content (if LLM prompts touched) — ambiguity, internal contradiction, drift across multiple sites

The agent should ask "is the obvious solution here actually the right one?" and surface design pushback in pairing voice. Output to `/tmp/pair_review_<scope-hash>_design.md`.

### 3c.v. Agent-output pathologies + style/CLAUDE.md adherence

The new specialist — highest-leverage for self-review. Reads `~/.claude/CLAUDE.md` and the project `CLAUDE.md` first. Hunt for:

- **Sycophantic over-delivery**: unrequested fallbacks, defensive validation, error handling for impossible cases, abstraction layers nobody asked for, feature flags / backwards-compat shims not requested. The user's CLAUDE.md explicitly bans these — flag them on sight.
- **Half-implementations**: TODOs, stubs, dead branches, code paths that compile but are never reached, half-finished feature flags, unused imports left over from earlier iterations.
- **Goal drift**: built ≠ asked. Compare the diff against the goal from the scope card; flag major divergence (e.g. "goal said 'add toc extractor', also rewrote PDF cache layer"). Skip this check if no goal was derivable.
- **Plausible-but-wrong**: code that "looks like the rest of the file" but uses the wrong idiom for this codebase — agent pattern-matching gone wrong. Read enough surrounding code to verify the chosen idiom matches.
- **CLAUDE.md violations** specific to this project: imports not at top of file, comments explaining WHAT (vs WHY), naming with `_v2`/`_new`/`enhanced_`, missing type hints, local imports, `@pytest.mark.asyncio` in pytest-asyncio AUTO mode projects, etc. Read both global and project CLAUDE.md to know which apply.

Output to `/tmp/pair_review_<scope-hash>_pathologies.md`.

## Step 4 — Synthesis

Read all five (or four, if no narrator dispatched) files. Produce the user-facing output inline.

### Output format

```
## How this change works
2-5 sentences tracing the change end-to-end. Cite path:line for load-bearing
claims. The point: if reading this doesn't match what you thought you built,
that's itself a finding — call that out as the first item in Top picks.

## Top picks
1. `path:line` — one-or-two-sentence push, pairing voice. Suggested fix
   inline ONLY when the suggestion IS the finding (e.g. "drop this branch",
   "rename to X").
2. ...
(1-5 items total, ranked by leverage)

## btw
- `path:line` — single-line push.
- ...
(up to ~10 items; spillover beyond 10 is silently dropped)

## Goal context
Reviewed against goal: <goal>. Source: <arg | conversation | commits>.
```

If no narrator was dispatched, write the "How this change works" section yourself from the diff before listing findings.

If no goal was derived, omit the "Goal context" line entirely.

### Ranking rule for top picks

Rank by **leverage** (how much it changes if you act on it), not severity.

- A design pushback on layering / abstraction beats a `_v2` naming nit.
- A missed test for the actual failure mode beats a coverage-by-line gap.
- A sycophantic unrequested fallback beats a nice-to-have observability suggestion.
- "Built ≠ asked" goes to the top whenever it fires.

### De-dupe rule

If multiple agents flag the same line, keep one finding with the highest-signal phrasing. Owner conventions:

- Correctness owns logic bugs and async/state issues
- Design owns abstraction / layering / naming / type-shape
- Tests owns coverage / brittleness / tautology
- Pathologies owns sycophancy / half-impl / goal-drift / CLAUDE.md violations

When in doubt, pick the framing that gives the user the clearest action.

### What to drop

- Severity verdicts ("must-fix", "should-fix", "nit") — pre-classifying steals the user's judgment.
- Long boilerplate fields ("What's there / Why this matters / Suggested fix") — terse pairing voice instead.
- Performative positives ("Worth keeping" applause sections).
- A "verified fine" section by default — only include if a specialist genuinely traced something non-obvious and confirmed it works, and even then one line.

### What to keep

- Concrete `path:line` everywhere
- Pairing voice — "drop?", "what about X?", "looks like Y"
- Suggested fixes ONLY when the suggestion IS the finding
- The narrative at the top — orientation matters
- Goal context line — so the user can immediately tell if agents aimed at the right target

## Step 5 — Stop

Output the synthesis inline. Do NOT:

- Edit any files in the repo
- Post anything to GitHub
- Apply suggested fixes automatically
- Ask the user "want me to fix #2?" — that's a separate request and they can make it themselves

The user reviews their own code. The skill exists to surface things they missed.

## Tone calibration

What "pairing voice" sounds like:

- ✅ "`pdf.py:142` — bare `except Exception: pass`. Caller can't tell 'no TOC' from 'parse threw'."
- ✅ "`toc.py:34-58` — ImportError fallback, but the dep is pinned. Drop?"
- ✅ "`test_toc.py` — only happy path covered. Malformed PDFs?"
- ❌ "**MUST-FIX**: silent error swallow at pdf.py:142" (severity verdict)
- ❌ "Worth a careful look at the exception handling in pdf.py" (parent skill's neutral voice)
- ❌ "I noticed that pdf.py:142 has a bare except clause which could potentially mask important errors and lead to debugging difficulties down the line. You may want to consider..." (reams of text)

Direct. Terse. Push not pronouncement. Suggested fix only when the fix IS the finding.

## When to deviate

- **Empty diff**: bail with one line. Don't dispatch agents.
- **Pure-doc diff**: doc mode (Step 3b). No specialists.
- **Tiny diff** (≤ 150 lines or ≤ 3 files): collapse mode (Step 3a). One agent, no btw section.
- **No tests in scope**: drop the test agent. The pathologies agent should note "no tests added" — that becomes a finding the synthesis can promote if the change deserved tests.
- **User explicitly asks for fixes to be applied**: confirm scope, then do it as a separate, post-skill action. The skill itself remains read-only.
- **User asks for a posted PR review**: wrong skill. Redirect them to `multi-agent-pr-review`.

## Refresh policy

`user-review-style.md` is shared with `multi-agent-pr-review`. Same file, same refresh policy — see that skill's "Refreshing the style guide" section. Don't refetch live during a pair-review run.
