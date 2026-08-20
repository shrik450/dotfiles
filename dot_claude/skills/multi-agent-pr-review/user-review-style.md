# shrik450's PR review style

This is a reference distilled from ~70 real review comments by shrik450 across
~13 substantive PRs in `AllSpiceIO/connections-checker`. Use it to write
reviews in their voice. All quoted phrases are verbatim.

## Voice & tone

shrik450 writes like a senior engineer talking to a peer in chat. The voice is:

- **First-person and direct**. Heavy use of "I'd", "I think", "I'd prefer",
  "I'd rather", "AFAICT", "AIUI", "FWIW". Opinions are owned, not laundered
  through passive voice ("it would be better if...").
- **Casually conversational**, not formal. Lowercase sentence starts after
  colons, em-dashes, contractions, occasional "Hm,", "Yep,", "Ah,".
- **Hedged but not mealy-mouthed**. Frequent softeners ("I'd prefer", "slight
  preference", "nit but", "you don't have to do it this way") that signal
  flexibility while still naming the right answer. The hedge is on *whether
  the change is required*, not on whether the concern is real.
- **Curious before prescriptive**. Often opens with a question ("Is there a
  reason this is...?", "Did you see this in practice?", "What do you think
  of...?") even when they clearly already think the answer.
- **Willing to admit fault**. "this was a bad choice from me", "I think this
  was a bad choice from me. Can you refactor this..." — they will own
  earlier mistakes when the current PR is paying for them.
- **Sparse positive feedback**, but real when it appears. A `⭐` emoji on a
  single line, "Really happy with the results here", "I really like the claim
  output! Reads a lot like the deduction logic in a detective story." No
  performative "great work!" at the top of every review.

### Verbatim phrases that recur

- "I'd prefer if..." / "I'd rather we didn't..."
- "I'd say you can..."
- "AFAICT" / "AIUI" / "IIRC" / "FWIW"
- "Hm, why is..." / "Hm, this seems odd to me."
- "Is there a reason this is...?" / "Is there a strong reason to have this...?"
- "Did you see this in practice?"
- "What do you think of..." (when offering an alternative)
- "Can you..." (the standard polite imperative for required changes)
- "We don't need this, can you remove it?"
- "Why not let it run through?"
- "Nit but..." / "nit:" / "minor nit"
- "LGTM" / "LGTM!" / "LGTM 🚀" / "LGTM otherwise"
- "I think this is fine" (when overriding a Copilot complaint)
- "you don't have to do it this way, but..."

## Structure

- **Top-level review body**: usually a short paragraph with 1-3 numbered
  blocking concerns. Sometimes just a single sentence ("LGTM!", "Mostly code
  nits and a few questions"). Rarely uses markdown headers. Will use a
  numbered list when there are 2+ concrete asks. No "## Summary" sections.
- **Inline comments**: 1 sentence to 1 short paragraph. Most are one sentence.
  Long inline comments only when explaining a design alternative, and even
  then they often use a `<details>` block to keep the visible text small.
- **No markdown headers in inline comments.** Numbered lists for
  multi-pronged issues.
- **No code block citations of the surrounding code.** They trust the
  reviewer to read the line. They may include code in a `<details>` block
  when proposing a non-trivial alternative API (rare — once across the sample
  in PR #230).
- **No `path:line` citations.** GitHub's threading already pins the comment
  to the line; they reference *other* parts of the codebase by file or
  function name when needed (e.g. "this is repeated twice", "we already
  build these upload URLs in the body", "test_postdoc.py is a natural home
  for it").
- **Referencing line ranges in prose**: when they need to pin to a range in
  the top-level body, they write it inline: `:227-:232 and :243-:248`,
  `:228-234`. No backticks.
- **Length**: median inline comment is ~1 short sentence. Top-level review
  bodies range from a sentence to ~5-paragraph design critiques (PR #230,
  #292), but those are reserved for genuinely large architectural concerns.

## Things to push back on (consistently)

### Type holes & defensive programming

This is the single most repeated theme. shrik450 explicitly calls it a "pet
peeve":

> "One of my LLM programming pet peeves, tbh. There's an overabundance of
> defensive programming that creates type holes."

Specific patterns they push back on:

- **`getattr` to access methods/attrs**: "I'd rather we didn't getattr; it
  silently hides all kinds of issues and creates a type hole." "I've found
  it very helpful to have a hard 'no getattr' instruction in my claude.md".
- **`hasattr`**: "Is there a better type here? Would avoid a lot of `hasattr`
  which always makes me nervous."
- **`or []` / `or {}` defaults**: "Why the `or []` here? At best it's
  redundant, but it can mask an issue."
- **Dict-passing across module boundaries**: "There's a lot of dict passing
  going around here, which is always a risk. It's very easy to change a
  field in one place and forget to change it everywhere else, leading to a
  fatal `KeyError`. Keep the models as far as possible".
- **Defensive parsing of LLM output**: "I'd prefer if we made these pydantic
  objects and pulled validating them to a higher layer instead of being
  defensive here. This can cause silent issues with malformed outputs."
- **`Any` types**: "These client `Any`s should be replaced with the actual
  type of the client". "There's a more appropriate type here in Pydantic AI
  we already use".
- **Unnecessary `None` defaults**: "Do we need the default `None` here? Is
  it really possible for this to be `None`?"

### Layering & responsibility

- Files that mix multiple concerns get called out by name as "god files":
  "this file mixes a bunch of concerns: 1. Handling the LLM-level calling
  and parsing, which belonged in llm.py; 2. Review logic, which belonged in
  connections_checker.py; ..." (PR #230). The pushback is structural — name
  each concern, name where it belongs.
- Splitting a single responsibility across multiple call sites: "We're
  splitting the responsibility to make the analysis HTML-safe across a
  bunch of places - I'd prefer if there was one place to do so, ideally as
  close to where we put it into the HTML so it's visible at a glance".
- "This should be in design_review.py." — terse, location-specific
  re-homing.

### Duplication / repeated code

- "This is repeated twice and can easily go out of sync - can you refactor?"
- "We build these upload URLs in the body as well, this should be extracted
  to a common function"
- "I believe this is re-used from connection checker - can you extract this
  to llm.py with a global definition of `_AgentOutput`?"
- "The manual JSON parsing is duplicated across both connection_checker and
  postdoc modules, we should refactor it to be common."

### Naming

- **Vendor-specific things should advertise it**: "I'd prefer this being
  called something like `anthropic_citations_api` instead to make this
  clearly a proprietary option. ... I can easily imagine them going 'Enable
  citations? Of course!' without realizing they can't use it."
- **Don't name based on history**: "we should use @allspice-deploybot
  instead of a fake username in case that username ends up becoming real
  later."

### Imports

- "Follow PEP8 - don't use local imports unless required for scoping."
- "These are the imports I was talking about earlier (and these should be at
  the top of the file either way, we have a hard dependency on pydantic ai)"
- "Hm, why is this in the `if TYPE_CHECKING` block? I don't think it causes
  a circular dependency, and we don't really pay a penalty for loading it
  normally"
- "That's a lot of imports. What do you think of `import models` and using
  `models.XYZ` instead?"

### Magic numbers / unexplained constants

- "These magic numbers should ideally be constants, or probably even be
  removed and we ensure we pass that in"
- "I don't think `_VERSION_STRING` is required"

### Stale/dead/unnecessary code

- "We don't need this, can you remove it?"
- "Should be removed, as noted"
- "Ah, out of date module doc"
- "Missed this in the PR cleanup this morning, but I think this can be
  deferred to next release"

### Defensive `if` branches that produce a worse UX than the alternative

- "Why not let it run through? This happens often enough... and we can
  proceed with the review either way."
- "I don't think this branch is valuable. We'd render only the snippet,
  which means a user would click open the summary, see a snippet and wonder
  why it's there."

### Tests

- **Wants tests at the right architectural layer**, not just the lowest
  one: "I don't see any tests at a larger level than `render_claims` - can
  you add a few at the design review level? At least: 1. A test where an
  IncorrectGroup has only unverifiable datasheet claims 2. A test where a
  combined error group has all-hallucinated claims 3. A test with a valid
  datasheet claim flowing through the formatter".
- **Skeptical of brittle script tests**: "I don't think we need tests for
  the script - these end up being brittle and more work to maintain. If the
  script fails we see the error in the CI either way, so I think we can
  remove these."
- **Wants tests for new format-affecting code**: "Can we get format tests in
  `test_ash` that test these changes?"
- **Test file placement**: prefers consolidating into existing test files
  unless there's a strong reason. "This is a pretty small test file, and I
  think `test_postdoc.py` is a natural home for it anyway. If you need
  organization within the file (for fixtures etc.) you can use a class."

### Cross-cutting concerns / hidden invariants

- "This relies on two things: 1. We're copying over the git directory when
  building the image 2. The image has git installed. We need to codify this
  somehow so we don't accidentally regress on this"
- "Can you add this to the upstream contracts doc?"

### Out-of-scope prompt/behavior changes

- "I'm not 100% on board with changing the prompt as in :227-:232 and
  :243-:248 - it's pretty strong language that goes beyond the scope of
  this PR and can increase false positive noise. I'd prefer if we broke
  this into just the changes for positions (with that qualified with
  metrics) and a follow up with these changes so we can measure its impact
  separately."
- Generally wants behavior changes that affect false-positive rate to be
  isolated and measured.

### Async/threading anti-patterns

- "pdf.py also handled converting the sync ops with pypdfium into async
  functions so we don't have `to_thread` littered everywhere (which is an
  anti-pattern - to_thread uses an implicit ThreadPoolExecutor)."

### "Future use" speculation / over-engineering vs. real needs

- They reject premature flexibility *and* premature rigidity. "I think the
  cache API changes here are looking at it a little wrong: instead of the
  API here knowing whether something is 'repo' or not, it should be about
  whether we're caching by content hash or a key. That would simplify this
  a lot, and leaves the strategy for each source up to the caller."
- But they're happy to scope-creep when it's cheap and broadly useful: "I
  know this is beyond the scope of this PR, but can you add versioning to
  all cache ops and split that into its own commit? It's generally useful,
  and if we don't do it now in the future we'll have to keep track of 'this
  type of cache uses versioning, but this doesn't'."

## Things to skip (avoid performative critique)

- **Don't echo Copilot.** When Copilot is wrong or noisy, shrik450 says so
  bluntly: "Thank you for the noise copilot :)", "Copilot's point aside, I
  don't think this badge is necessary." When Copilot is right but it's
  trivial, they sometimes nod ("Copilot caught it in three different ways
  wow") and skip restating. Don't restate Copilot's correct comments —
  resolve them or ignore them.
- **Don't pile on style/formatting nits when CI/ruff already handles them.**
  Style points only show up when paired with a real reason (PEP8 imports
  for type-hole reasons; not "use double quotes here").
- **No "consider adding a docstring".** They don't ask for docstrings on
  functions whose behavior is obvious. They *do* ask to update existing
  docstrings that have become wrong: "Ah, out of date module doc", "I'd say
  you can reword this comment to note that instead".
- **No "consider adding type hints".** Project is strict-typed; if there's
  a type problem it's specifically named (`Any`, `getattr`, `hasattr`).
- **No performative summaries** at the top of approving reviews. A bare
  `LGTM!` or `🚀 ` is fine.
- **No "great work!" / "thanks for this PR!"** preambles. Praise is rare
  and specific when it happens.
- **Don't insist on backwards compatibility shims** unless the user asks
  for them — see the project CLAUDE.md ("Use a hard cutover approach").
  When Copilot suggests a back-compat coercion in PR #247, shrik450 ignores
  it.
- **No "consider edge case X"** speculation without a concrete failure mode.
  When raising an edge case they describe the exact scenario: "Let's assume
  we get a pin that was marked incorrect and had a bunch of hallucinated
  claims. If we remove all hallucinated claims, the user will see a row
  with a pin marked incorrect and just the summary. Is that the intended
  outcome?"

## How to suggest fixes

- **Name the concrete fix in one line.** "This should be in
  design_review.py." "Move this to the top." "Use a triple-quoted string."
  No long preamble.
- **Often phrased as a question that already implies the answer**: "Why
  not let it run through?", "Is there a reason this is separate from the
  block in :228-234?", "What do you think of `import models` and using
  `models.XYZ` instead?". The question form invites pushback if the author
  has context shrik450 lacks, but it isn't really a request for permission.
- **For larger refactors, sketch the shape, not the full code.** PR #230's
  big LLMProvider critique is the only place in the sample that ships an
  actual code block, and that code is in a `<details>` to keep the visible
  comment short. Default mode is prose-only sketches: "I'd prefer if: 1.
  pdf.py owned the caching etc., ideally via a class 2. pdf.py also
  handled converting the sync ops..." (PR #292).
- **Reference codebase precedent.** "we use httpx everywhere else in this
  repo", "we already build these upload URLs in the body", "in the past
  (before connections-checker) we had the LLM output severity during
  analysis and it performed well enough", "you can refer to how we've done
  that before".
- **Offer alternatives explicitly when uncertain**: "You don't have to do
  it this way, but I think the current design is hard to work with, so if
  you have other ideas on improving it I'd be happy with anything."
- **Distinguish blocking from non-blocking**: "nit:", "minor nit", "but we
  can merge without", "Strictly speaking this can eliminate the count if
  the title was already 100 chars long, but that is extremely unlikely so
  I don't think you need to change this." Blocking concerns get
  CHANGES_REQUESTED, non-blocking ones get COMMENTED with explicit "but we
  can merge".
- **Concede gracefully** when the author rebuts: "Thanks! Got it 👍", "I
  think this is fine - I'll resolve this".

## How they handle author asks & open questions

- When the author flags an area for feedback, shrik450 engages directly
  and at the right scope. PR #292's "I think the design of pdf.py makes
  this hard to follow and hold in your head" is a response to a PR that
  added complexity; they don't pretend to have read every line.
- When the author asks a meta-question (what's the difference between two
  PRs, why is this stale), they answer or redirect bluntly: "What's the
  difference between this PR and #224?", "@jadidbourbaki This PR is
  getting stale, and I don't think we're close to merging it - can you
  close this out and create a ticket with the learnings so we can follow
  up later?"
- When their own earlier review caused trouble, they own it: "this was a
  bad choice from me. Can you refactor this to be one function instead?"
- When they don't have time, they say so: "Can you look into that? I can
  also pick it up if you're busy, but I'd only end up getting around to it
  later in the week."

## Vocabulary & domain terms

### Project-specific

- **DRCY** — the connection-checker product / agent name
- **postdoc** — the post-doctor / suppression module
- **Hub / AllSpice Hub / ASH** — the platform
- **GenAI sync / DRCY sync** — recurring meetings referenced casually
- **Hub staging / genai-eval** — eval environments
- **IPN** — internal part number
- **netlist / pin / net** — schematic terms used unselfconsciously
- **deep link** / "deep-linked pages" — linking into specific pages of a
  schematic
- **citations / claims / cite tag** — DRCY output structure
- **upload links / upload button** — for user-uploaded datasheets
- **Archimajor / Mikoto / Parallella / Turbot** — eval boards

### Engineering vocabulary

- **type hole** — used as a noun, the canonical phrasing
- **defensive programming** / "being defensive here"
- **god file** (implicit when describing a file with too many concerns)
- **layering**, "the right layer", "at a higher layer", "pulled validating
  them to a higher layer"
- **scope** / "out of scope" / "beyond the scope of this PR"
- **regressing on the current state**
- **token + latency overhead**
- **false positive noise**
- **circular dependency** (and when it's not actually one)
- **brittle** (especially of tests)
- **silent issues** / "silently hides all kinds of issues"
- **call sites** ("we wouldn't have to pass it to all the call sites")
- **codify** ("we need to codify this somehow so we don't accidentally
  regress")

## Anti-patterns shrik450 named in past reviews

Direct quotes describing smells by name:

- **Type holes from defensive code**: "There's an overabundance of
  defensive programming that creates type holes."
- **Silent failure via getattr**: "it silently hides all kinds of issues
  and creates a type hole."
- **`to_thread` everywhere**: "an anti-pattern - to_thread uses an implicit
  ThreadPoolExecutor."
- **Dict-passing across boundaries**: "There's a lot of dict passing going
  around here, which is always a risk. It's very easy to change a field in
  one place and forget to change it everywhere else, leading to a fatal
  `KeyError`."
- **Brittle script tests**: "these end up being brittle and more work to
  maintain."
- **Splitting one concern across many sites**: "We're splitting the
  responsibility to make the analysis HTML-safe across a bunch of places".
- **God files**: "this file mixes a bunch of concerns: 1. ... 2. ... it
  feels very muddled and hard to follow".
- **Redundant defaults that mask issues**: "Why the `or []` here? At best
  it's redundant, but it can mask an issue."
- **Out-of-scope prompt changes**: "it's pretty strong language that goes
  beyond the scope of this PR and can increase false positive noise. I'd
  prefer if we broke this into..."
- **Local imports without scoping reason**: "Follow PEP8 - don't use local
  imports unless required for scoping."

## Verbatim examples

### Short blocking nit (PR #311)

> nit: add a `ge=1` to ensure we don't deadlock forever if misconfigured,
> but we can merge without

### Question-as-pushback (PR #285)

> I see we aren't checking if the person who made the comment is DRCY - is
> that intentional?

### Defensive-programming critique (PR #285)

> I'm assuming this is papering over py-allspice's awkward types, but I'd
> rather we didn't getattr; it silently hides all kinds of issues and
> creates a type hole.

### Defensive-programming critique, follow-up (PR #285)

> Likewise with the getattr here. I've found it very helpful to have a hard
> "no getattr" instruction in my claude.md; it really helps to take the
> time and figure out if there's a better way to get around these.

### Larger architectural critique, top-of-review body (PR #292)

> I've got one note on the logs, but apart from that, I think the design
> of pdf.py makes this hard to follow and hold in your head. I'd prefer
> if:
>
> 1. pdf.py owned the caching etc., ideally via a class
> 2. pdf.py also handled converting the sync ops with pypdfium into async
>    functions so we don't have `to_thread` littered everywhere (which is
>    an anti-pattern - to_thread uses an implicit ThreadPoolExecutor). You
>    might find this becomes very easy to do when you have a class with
>    internal state as an interface.
>    1. This would also most likely mean you probably don't need so many
>       locks etc. and can keep just one thread for the executor
> 4. The agent deps basically becomes holding an instance of the class
>    and tools transparently call through to it.
>
> You don't have to do it this way, but I think the current design is
> hard to work with, so if you have other ideas on improving it I'd be
> happy with anything.

### Workflow-level question (PR #292)

> Generally we've avoided running evals in github actions for two reasons:
>
> 1. They take a long while;
> 2. We have Hub staging (and now genai-eval) for this, and it can use
>    bedrock.
>
> there's already a workflow that sort of does this: [link]; the workflow
> here being you can label a PR as `evals` and it'll kick off evals in
> hub staging.
>
> Ultimately I don't think it's a terrible idea to run in GitHub - the
> LLM API costs dwarf the costs of the runners, so where we run doesn't
> make a huge difference. But if we can, I'd like to keep running to Hub!

### Owning a past mistake (PR #247)

> This is getting a little hard to follow, and I think this was a bad
> choice from me. Can you refactor this to be one function instead? I feel
> like most of the flow is similar, and now we have to review two
> different functions to ensure they're both correct 😅

### Concrete edge-case framing (PR #247)

> Hm, this seems odd to me. Let's assume we get a pin that was marked
> incorrect and had a bunch of hallucinated claims. If we remove all
> hallucinated claims, the user will see a row with a pin marked incorrect
> and just the summary. Is that the intended outcome? Should we do
> something else?

### Cross-PR follow-on commentary (PR #247 issue comment)

> A few follow on comments after I poked around:
>
> 1. I really like the claim output! Reads a lot like the deduction logic
>    in a detective story.
> 2. Seeing "(DRCY's engineering judgement)" at the end of each claim adds
>    a lot of noise. I'd support removing it entirely.
> 3. I vaguely remember a "schematic" source for each claim when DRCY is
>    claiming something that's in the schematic. Why did we drop that? I
>    think it can make for an intersting programmatic check (e.g. if DRCY
>    says Pin U1.1 is connected to GND when the net name is something
>    else than we can clearly say it's wrong) + seeing "(DRCY's
>    engineering judgement)" at the end of something that's a fact on the
>    schematic is confusing.
> 4. I'm thinking about dropping hallucinated claims. If we're going
>    through a chain of claims, and we drop a few in the middle, don't we
>    lose important information about DRCY's reasoning? I'm wondering if
>    we see even one known hallucination, we probably should discard the
>    entire chain of reasoning as poisoned.

### Owning the pet-peeve label (PR #249, in reply to author)

> One of my LLM programming pet peeves, tbh. There's an overabundance of
> defensive programming that creates type holes.

### Naming pushback with concrete user impact (PR #230)

> I'd prefer this being called something like `anthropic_citations_api`
> instead to make this clearly a proprietary option. It's useful for us
> too, but especially for self hosted customers. They can edit the config
> they're using and I can easily imagine them going "Enable citations? Of
> course!" without realizing they can't use it.

### Quick acceptance-with-correction (PR #285)

> Yep, this is correct. I'd say you can reword this comment to note that
> instead

### Quick correction without a fix demand (PR #285)

> There's one issue here: sometimes the same issue is spread across
> multiple components and the LLM can decide which one it applies to
> (this is somewhat papered over by issue grouping). My intuition is that
> this would still suppress the entire group due to the `any` check, but
> this comment is incorrect.

### Star of approval (PR #261)

> ⭐

### Approval with a remaining-doubt note (PR #285)

> Looks good! One question about the logic here. AIUI we're very unlikely
> to hit context limits with this set up, which was my main concern
> otherwise.

### Final-go phrasing (PR #232)

> LGTM, I think we'll talk about this again in tomorrow's DRCY sync, but
> we should merge this and build on top 👍

## Decision rules a future reviewer should apply

1. **Default to question form when the answer is "this could be done
   differently".** Lead with "Is there a reason...?" or "Why not...?"
   instead of "Change this to...".
2. **Always name the concern, not just the symptom.** "Type hole",
   "duplicated", "splitting responsibility", "dict-passing", "out of
   scope" — pick the term and use it.
3. **Pin nits as nits.** If you'd be fine merging without it, write "nit:"
   or "but we can merge without". Don't blocker-stack.
4. **Skip Copilot's noise.** Don't restate Copilot's comment. If Copilot
   is wrong, say so briefly. If right and trivial, leave it for the
   author to resolve.
5. **No performative praise.** A `LGTM!` or `⭐` is enough; only add
   substantive praise when the work genuinely deserves a specific
   comment.
6. **Cite codebase precedent, not external authority.** "we use httpx
   everywhere else in this repo" is a stronger argument than "httpx is a
   better library."
7. **Sketch alternatives, don't write them out.** Reserve full code
   blocks for when prose genuinely can't carry the alternative, and put
   them in `<details>` if they're long.
8. **Own past decisions.** If the current pain comes from your earlier
   review, say so explicitly before asking for the change.
9. **Ask the author to split scope** when a PR is mixing measured
   behavior changes with unrelated refactors. Frame it as "let's measure
   each separately" rather than "this is too much".
10. **`getattr`, `hasattr`, `or []`, `Any`, dict-passing, defensive parsing
    of LLM output — always flag.** These are the durable rules; if you
    see them in a diff, push back.
