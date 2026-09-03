---
name: pr-description
description: Write a PR title and body in the user's style. Use when the user asks to write a PR description, commit message, or prepare changes for review.
disable-model-invocation: true
---

# Write a PR description

Write a PR title and body for the current branch's changes. Follow these steps:

1. Run `git log main..HEAD --format="%s%n%n%b%n---"` to see all commits on this
   branch.
2. Run `git diff main --stat` for a summary, then `git diff main` for the full
   diff of production code (exclude test files on first pass to focus on what
   changed).
3. If there's a ticket ID in the commit messages (e.g. `[ID-XXXX]`), include it
   in the title.
4. If the branch already has a PR, run
   `gh pr view --json title,body,isDraft,url`. Treat its description and draft
   status as source material. Preserve useful context that the diff cannot show
   unless the user asks for a full rewrite.

## Style rules

- **Title**: `[ID-XXXX] Short imperative description` when there's a ticket,
  otherwise just a short imperative description. No `feat:` or conventional
  commit prefixes. Under 70 characters.
- **Body**: Casual, direct prose. No markdown headers or template sections.
  Lead with the problem or motivation in 1-2 sentences. Use a concrete example
  when it makes the failure mode easier to understand. When several causes
  produce the problem, explain each cause before describing the fixes.
- Use a short numbered or bullet list for several substantive fixes, reasons, or
  examples. Never use one to inventory files. Do not compress a multi-cause or
  multi-part change until its mechanism becomes unclear.
- Call out a pre-existing or incidental bug fix separately from the main change.
  State important limits and remaining failure cases. Do not present a
  mitigation as a complete fix.
- Write like you're explaining the change to a colleague, not filling out a
  form. Keep it concise, but use more than two paragraphs when the causes,
  distinct fixes, or limits need separate treatment. Mention testing links or
  reproduction steps only if relevant. Mention draft or review status when the
  user or an existing PR provides it.

## What to avoid

- No "## Summary" / "## Changes" / "## Test plan" headers
- No bullet point lists of files changed
- No verbose descriptions of obvious things
- No emojis
- Do not create the PR unless the user explicitly asks you to

## Examples

Use these real examples to match the user's voice and style.

### PR descriptions

**Title:** `[ID-3349] Add regular regression testing of Hub <-> DRCY interaction`
**Body:**
> This PR adds two main things:
>
> 1. A new `docs/upstream-expectations.md` document that covers what we expect from platform and parsing; and
> 2. A regularly running regression test to ensure we're not regressing on our format processing and review posting capabilities. This test runs automatically ever week and will run in every PR as well.
>
> While I was working on the upstream expectations docs, I ran into a few minor issues in the code that were easily fixable, so I've included them in this PR. Those include:
>
> 1. Remove AllSpice Tools format handling code
> 2. Standardize to using `proj-diff` as a schematic type as well
> 3. Use the project diff tree for commit ids to enable a review on closed DRs as well.
>
> Apologies for the grab bag PR :)
>
> Also closes ID-3290

**Title:** `Count Form XObject bytes when sniffing complex pages`
**Body:**
> The complexity sniff that routes heavy pages to image rendering only measured each page's own content stream. But dense vector drawings (e.g. performance-plot pages) often live in Form XObjects that the page stream merely invokes, so those pages slipped under the threshold and went to pdfplumber, which can exhaust memory materializing every path operator.
>
> The specific datasheets that triggered this were:
>
> - TPS7A2033
> - BUF802
>
> Now the sniff recursively walks referenced Form XObjects and counts their decoded bytes too, with a recursion-depth cap and cycle guard for pathological documents. Also release each page's pdfplumber cache in a finally as we iterate, so a multi-page request peaks at the largest single page rather than holding the whole batch.

**Title:** `Soft-revert #371`
**Body:**
> In the release process for v0.4.10, @NHerbertAllSpice found increased variance in the review quality between Archimajor and Parallella that was traced down to the selection changes in #371. Those selection changes were required to get consistent reviews with MD+CSV, so this commit reverts the prompts to how they were before #371 and sets the feature flag to off by default until we fix the prompts.

**Title:** `Drop exclude_none/exclude_unset on round-tripped Pydantic dumps`
**Body:**
> [The Parallella E2E run for 0.4.5](https://staging.allspice.dev/AI-Evals/parallella-sdax-demo/actions/runs/280/jobs/0) failed at finalization with
>
> ```
> pydantic_core.ValidationError: ProcessedSpec.cache_info.cached_at — Field required [type=missing].
> ```
>
> `AgenticDatasheetProvider`'s `FileBackedMapping` serializes via `model_dump_json(exclude_none=True)`, but `CacheInfo.cached_at: datetime | None` has no default and is a required field. Therefore `CacheInfo.miss()` writes a JSON blob without the key and `model_validate_json` rejects it on the bulk read at the end of the run.
>
> This commit fixes this by dropping the lossy serializer flags. I scanned the rest of the codebase for the same shape and found two siblings in connections_checker/models.py:
>
> 1. `PageAnalysisResult.to_json_dict`
> 2. `make_page_output_cache`
>
> They happen to round-trip cleanly today only because every nullable field in that tree has a default, but we can't rely on that with lossy serialization, so I dropped the flags there too for symmetry.

**Title:** `Combine only pins where group reviews disagree`
**Body:**
> Contributes to ID-4077.
>
> We run into context limits in the group combiner as it has the full page + datasheets + output for all group reviews. If we remove the output for all pins where all the reviewers agreed, we can reduce context usage by ~30% and get effectively the same output. This commit does basically that.
>
> Where this gets complicated is that different group reviewers may have grouped pins differently. The approach taken here is to pass the full group if any pin in that group is contented, and to request the LLM to produce entries for all pins even if only one reviewer mentions it.

### Commit messages

Short, no body needed:
```
[ID-3428] Remove Zebra E2E from code
```

With a brief reference link:
```
Pin upload-artifact to v3-node20

See https://github.com/actions/upload-artifact/issues/783
```

With reasoning for a judgement call:
```
Lower datasheet concurrency to 3

Out of an abundance of caution, lowers the datasheet concurrency cap to
3 datasheets at once so we stop failing on runs. Despite the spate of
memory fixes that land alongside this, my measured parent memory usage
per datasheet is around 300MB, and I see a few touch 500MB occasionally.
That means 4 concurrent would hit 2G, with firefox's 1G floor that's
uncomfortably close to 3.5G. 3 concurrent cannot hit that, so to keep
some degree of tolerance we set the concurrency to 3 while we figure out
better options.
```

Recording a design disagreement and its rationale:
```
Add mouser library and use it by default in litesheets

Adds a new library using Mouser's search API and sets that in the
default config list for litesheets. Also includes prioritization by
source order in litesheet's responses, so URLs from Mouser will appear
before URLs from DigiKey in the response.

This adapts @jadidbourbaki's work in 57aab1e, with one notable change.
Hayder had implemented a fallback system in Litesheets, which would only
try Digikey if Mouser fails to respond with a URL. I think this isn't a
good idea for two reasons:

1. If we fail to fetch the Mouser URL in CC, now we don't even know that
   the DigiKey URL exists to try it.
2. Litesheets should fetch all URLs and store them so we can have an
   archive of URLs to use in the future.

I've noted the rationale in the docstrings here.
```
