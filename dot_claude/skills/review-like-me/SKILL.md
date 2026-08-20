---
name: review-like-me
description: Review a PR the way shrik450 would — form an independent design for the change, diff the PR against it, and draft the comments he'd leave in his voice and at his threshold. Grounded in his real review corpus, persona, and self-eval log. Use when he says "review like me", "review from my lens", "what would I flag here". Output is ALWAYS draft comment text for him to post himself — this skill never writes to or submits a review.
disable-model-invocation: true
---

# Review like me (shrik450's lens)

Simulate shrik450's own review of a PR. The output predicts the comments *he*
would leave — draft text in his voice, delivered as a review guide he reads
before writing his own review. You MUST NOT post anything; he writes his own
comments.

## Absolute guardrail

**He writes reviews. You draft.** Never call any API that creates, edits, or
submits a review, review comment, or review body (no `gh pr review`, no
`gh api .../reviews` writes, no GraphQL review mutations). Hand back text with
`file:line` anchors and let him post it. This rule is non-negotiable — it was
violated once and overwrote a live review. If he explicitly asks you to post,
stop and confirm the exact text and target first, then still prefer he posts.

## The method: design it yourself, then diff

He does not review by scanning a diff for defect patterns. He reads the
intent, forms his own view of how the change should be built given how
everything fits together, and comments where the PR diverges from that view.
His recurring comments — "this belongs in `ash`", "Enum over strings", "the
required parameter makes discarding visible", "reuse the existing fetch" —
are not separate lenses; each is a diff between the design in front of him
and the design he would have written. To review like him, run that process:

1. **Understand the intent.** Read the ticket (fetch Notion tickets via the
   Notion MCP tools), the PR body, and the author's own comments. What is the
   change trying to achieve, what did the author call out or promise, and —
   critically — what follow-up work does the ticket name? The named next
   change is the load the design must carry.

2. **Design it yourself, before reading how the author built it.** From the
   ticket and the repo's structure — the workspace dependency graph in
   CLAUDE.md, the existing modules and their contracts — sketch the design
   you'd write:
   - where each piece lives, and who owns which vocabulary (a shared package
     owns mechanism; the packages that depend on it own their domain types);
   - the contract at each seam — function signatures, types, names, the data
     shapes crossing it;
   - which files change when the ticket's named follow-up work lands, and who
     edits them.

   This step is what catches placement and ownership problems. An issue whose
   evidence is a whole package's relationship to the dependency graph has no
   single line to anchor to; it is only visible as a divergence from an
   independently formed design.

3. **Read the diff as a diff against your design.** Where the two match, move
   on. Where they diverge, exactly one of two things is true:
   - the author documented a reason — module docstring, `docs/` change in the
     diff, CLAUDE.md, PR body, ticket — that your design didn't account for.
     You learn: adopt their design and drop the divergence.
   - there is no such reason, or the diff itself demonstrates the consequence
     your design avoids. That's a comment.

   A divergence backed by a demonstrated consequence in the diff is not taste
   against taste: raise it even when the choice came from the ticket, framed
   as a question with the consequence as the evidence.

4. **Then sweep** for what the comparison doesn't surface:
   - **Correctness** — real bugs hit in practice, including fail-soft: every
     step of a best-effort feature should degrade instead of crash.
   - **Test quality** — framed as a consequence of the contract ("this isn't
     testable because the logic is in `__main__`, not behind the `ash`
     contract"), never a bare "add tests".
   - **Cost/benefit** — "does this really move the needle?" for tokens and
     latency.

5. **Consolidate by root cause before ranking.** Several findings that share a
   cause are one finding at the altitude of the decision that caused them,
   with the instances as evidence — not several parallel raises. If you find
   yourself writing the third symptom of the same decision, review the
   decision.

   **Merge for a shared cause; link for a shared failure.** Two findings that
   need each other to break anything are not one finding: they sit in
   different code, they have separate fixes, and either fix alone closes the
   failure. Merging them hides that. Keep both and state the link on both,
   naming which half each one is. The usual shape is opposite sides of one
   boundary: a value absent going out and unreadable coming back; a limit
   unstated up front and undiagnosable on failure. Test which case you have
   by asking whether fixing one leaves the other worth raising. If it does
   not, you have one cause and should merge.

**Judging any contract** — his or your proposed alternative — the test is a
pit of success: does it force the right thing, make the wrong thing visible,
and minimize papercuts and footguns? Never propose a fix that reopens a
footgun. An Optional that surfaces a bad value is good; an optional/defaulted
parameter that masks a forgotten choice is the anti-pattern, not the fix.

## Calibrate voice and threshold (not what to look for)

The corpus and persona set how findings are phrased and what clears the bar —
they are not the source of findings:

1. `~/.claude/review-corpus/self-eval.md` — per-PR comparisons of a simulated
   review against his real one. Each entry answers "did my independent design
   match his?"; read the standing lessons and recent entries before reviewing.
2. `~/.claude/review-corpus/corpus.json` — filter `kind == "inline"` and skim
   a sample to calibrate voice: casual, hedged-but-decisive ("I'd prefer",
   "Hm,", "AFAICT"); `nit:` for trivia; asks for evidence ("Did you test this
   with…?"); proposes follow-up tickets rather than blocking.
3. The connections-checker review-persona memory (recalled automatically) for
   threshold and density: ~3.5 comments/PR, bimodal; low bar for
   correctness/API/type-safety; rejects bikeshedding, anything a linter
   catches, and naming complaints unless the name causes real confusion.

The corpus and persona are specific to `AllSpiceIO/connections-checker`. On
other repos, lean on the persona patterns plus that repo's own history and say
you're extrapolating.

## Output — always an HTML artifact

**Always deliver as a single-file HTML artifact, never plain markdown** — he
reads HTML far faster. Use his established review-guide design (dark EDA-tool
palette, mono "net-label" section headers, severity dots/stripes, progressive
disclosure via `<details>` so the default view is scannable and reasoning
expands on click). Load the `artifact-design` skill before writing it. Prior
guides like `~/Developer/random-plans/pr-370-review.html` are the reference
style.

Structure the page top-to-bottom so he can sanity-check fast, *then* read the
verdict:

1. **How this change works** — a few sentences (and a small diagram if it
   helps) on what the change actually does, mechanically.
2. **The goal** — what it's trying to achieve, from the ticket, not the diff.
3. **How I'd have built it** — the independent design from step 2, compressed:
   ownership, seams, and what the named follow-up work touches. This is the
   frame the findings hang off, and it lets him check the reviewer's premise
   before trusting its conclusions.
4. **Where the PR diverges** — the findings, ordered by how much the
   divergence will cost as the system evolves. Each: `file:line` anchors, the
   contract you'd want (not just "move it"), the documented-reason check's
   outcome, confidence. Group block / raise / nit.
5. **What's well done** — genuine praise, specific lines. He does this in real
   reviews (⭐/👍).
6. **What's incorrect** — confirmed bugs / things that are simply wrong, from
   the sweeps.

Each finding is also draft comment text he can lift and paste himself.

After he posts his real review, offer to **add a self-eval entry** to
`~/.claude/review-corpus/self-eval.md` comparing your independent design and
findings against his — that comparison is how the lens keeps tightening. Nudge
him to run `uv run ~/.claude/review-corpus/refresh.py` if the corpus looks
stale (idempotent).
