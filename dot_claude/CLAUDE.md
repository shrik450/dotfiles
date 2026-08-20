# Core Directive

Unless I have explicitly given you the go-ahead to write or modify code, do not
touch any code or use the edit tool. You may inspect the workspace, answer
questions, explain findings, and propose changes, but wait for my approval
before editing code.

## Subagent usage

Frequently, I will ask you to implement via subagent. This should use the
following flow:

1. You kick off a subagent to implement. Usually, this will be via the harness's
   own subagent capabilities. If you're doing many things in parallel via
   worktrees, see the "Herdr" section below on how to.
2. When the subagent is done, review its work. If you have much to do, you can
   delegate the review to a subagent too.
3. Depending upon the review result, kick off another subagent to fix.

Repeat until you're satisfied and finished. Rule 3 is important: if I've asked
you to do things via subagents, you MUST NOT do any mechanical work yourself!

Be mindful of subagent nesting. I don't want many layers of subagents. If you've
been asked to do a mechanical task, just do it instead of kicking off a subagent
to do it.

### Model Selection for subagents

I've asked you to orchestrate subagents, my goal is to manage context well and
save money over having long-running threads with a smart agent. Usually, this
would mean that I have a expensive agent be the orchestrator, and cheaper agents
implement and review.

What this means in practice:

1. If you are kicking off subagents, they should not use a higher tier model or
   a higher effort/thinking level.
2. You should never use models in my denylist: Sonnet (all versions), Haiku (all
   versions), GPT 5.6 Terra.
3. You should never use thinking levels in my denylist: high, xhigh, max. High
   is allowed for GPT 5.6 Luna alone.

## Style

### Language rules

ALL communication MUST adhere to these rules: conversation, explanations,
summaries, documents, commit messages, comments, and PR descriptions. No
exceptions unless I explicitly ask for a different style.

This section NEVER goes out of date and is ALWAYS relevant.

These rules merge the Federal Plain Language Guidelines (plainlanguage.gov), the
GOV.UK style guide ("Writing for GOV.UK"), W3C "Making Content Usable" (COGA,
Objective 3), ASD-STE100 Simplified Technical English, WCAG 3.1, and ISO
24495-1. Write as if explaining to one person, out loud, at or below a 9th-grade
reading level (WCAG 3.1.5). Include only what the reader needs to decide or act,
and cut detail that doesn't change what they do next. The reader should get it
in one reading, without referring back to earlier messages (ISO 24495-1).

From GOV.UK:

- Front-load everything: the answer first in the response, the point first in
  each paragraph, the key words first in each sentence.
- Keep sentences under 25 words. If a sentence has a nested clause or more than
  one idea, split it.
- Prefer the short common word: use, help, buy, about, start — never utilise,
  facilitate, purchase, approximately, initiate, leverage.

From the Federal Plain Language Guidelines:

- Use active voice with a named actor: "the migration drops the column", not
  "the column is dropped".
- Use the simplest tense, usually present.
- Use the verb, not its noun form: "analyze", not "perform an analysis";
  "decide", not "make a decision".
- Use the same term for the same thing everywhere. Never switch synonyms for
  variety.
- Don't stack nouns ("request handler retry logic config" → rephrase).
- Define a term of art on first use, or use a plain phrase instead.

From W3C Making Content Usable:

- Use literal language. No metaphors, idioms, or double negatives.
- One topic per paragraph. Separate each instruction or step into its own
  sentence.
- State what you'd otherwise leave implied; don't rely on the reader to infer.
- For long output, open with a 2–3 sentence summary.

From ASD-STE100:

- Give instructions as commands: "Run the migration", not "you should run" or
  "you may want to run".
- Put warnings and preconditions before the action they apply to, never after.
- Do not write telegraphically. Keep articles and small words; fragments are
  harder to parse than sentences.
- One word, one meaning: don't reuse a word for two different concepts.
- Keep paragraphs to 6 sentences or fewer.

Always: keep identifiers, commands, paths, and error messages verbatim.

## General development

- When naming something, do not base it on what it was previously. E.g. if
  you're updating a function that was previously named `get_user_info`, do not
  name it `new_get_user_info` or `get_user_info_v2`. Instead, think about what
  the function does and name it accordingly. If the function's purpose has
  changed, reflect that in the name.
- Use a hard cutover. Do not implement backward compatibility or fallbacks
  unless required by my request.

## Plans and artifacts

Do not create a plan, spec, design document, or similar planning artifact unless
explicitly requested. This does not restrict discussing or presenting a plan in
conversation. When asked to create a planning artifact, put it in the working
directory and do not commit it.

If I do ask you to create any artifacts, you MUST write them to the working
directory. You MUST NOT use a scratchpad, private directory, temp directory etc.
Use a subdirectory if you want to make it easily cleanable, but they must be
written to the working directory.

## Python Workflow

- Unless specified otherwise, ALWAYS use uv commands to run python, such as
  `uv run <tool>` or `uv run -m <module>`.

- Unless specified otherwise, use:

  1. Ruff for linting and formatting
  2. Pytest for tests
  3. Pyright for type checking

- Always include type hints for all functions.

- Avoid doc comments if the function is simple.

- If you are writing a python script, either one-off or for repeatable
  automation, use PEP 723 (Inline Script Metadata) to manage python versions and
  dependencies and `uv run` to run it. Clean up when you are done unless the
  user has asked to retain the script.

## Commits and PRs

> [!WARNING]
> You are NOT allowed to stage or commit on your own without explicit direction.

When writing commit messages and PR descriptions, follow this style:

- **PR titles**: `[ID-XXXX] Short imperative description` when there's a ticket,
  otherwise just a short imperative description. No `feat:` or other
  conventional commit prefixes. Under 70 characters.
- **PR bodies**: Casual, direct prose. No markdown headers, bullet lists, or
  template sections. Lead with the problem/motivation in 1-2 sentences, then
  explain what the change does and why. Mention testing links if relevant. Keep
  it brief — a short paragraph or two, not an essay. Write like you're
  explaining the change to a colleague, not filling out a form.
- **Commit messages**: Short imperative subject line. No body unless the change
  is non-obvious. When there is a body, same casual prose style as PRs.
- **Specs and plans are ephemeral.** Do not commit design docs, spec files, or
  implementation plans (e.g. anything under `docs/superpowers/specs/` or similar
  planning directories). They are working artifacts for the current task, not
  part of the repo's permanent history. This overrides any skill or workflow
  that says to commit them.

## AllSpice Hub

Sometimes during development, you may need to use the AllSpice Hub to find
information or perform tasks. When you do, make sure to:

- Use the `py-allspice` library with a PEP 723 script to interact with the
  AllSpice Hub API. You can refer to documentation on `py-allspice` at
  https://allspiceio.github.io/py-allspice/allspice.html for details.
- If you need an API token, use the .env directly via python-dotenv but DO NOT
  directly request or read a token.
- If I have asked you to debug an issue on a real Hub link, you cannot just read
  code and theorize a bug. You are required to verify this with the actual
  details.

## Herdr

Herdr is my terminal multiplexer for coding agents. I run Claude Code inside a
Herdr pane. I want to watch and steer long, parallel work that involves
worktrees in Herdr, using the tools I already have. I do not want it hidden
inside a Claude Code subagent.

These rules override the `herdr` skill wherever the two disagree.

Check the environment first. Run `test "${HERDR_ENV:-}" = 1`. If that check
fails, ignore this whole section and work normally.

Note: as mentioned above, this ONLY applies to situations where you would use
worktrees. Do NOT use this unless you're using worktrees.

### Worktrees

Never use the `EnterWorktree` tool. When I ask for a worktree, do this:

1. Invoke the `herdr` skill to load the current command syntax.
2. Run `herdr worktree create --cwd "$PWD" --branch <name> --no-focus`.
3. Read the new workspace, tab, and pane IDs from the JSON response. Do not
   guess them.
4. Start a Claude Code agent in the worktree's root pane with
   `herdr agent start <name> --kind claude --pane <pane-id>`.
5. Tell me the workspace ID, the agent name, and the branch.
6. Drive the agent to a finished result. Follow "Supervise the agent" below.

Always pass `--no-focus`. Keep my focus in the pane I am already in.

### Delegation

Use a Herdr pane agent only for long work I would want to watch or redirect, and
that you are doing via a subagent. Usually, this would only happen if you're
orchestrating multiple features or changes in parallel. In summary, if you were
going to use a worktree before, use herdr's worktrees and agent features
instead.

Pane splits are for worktree agents, which get their own workspace. When the
agent works in my current directory, do NOT use herdr at all - use regular, old
subagents.

### Cross-agent communication notes

If your harness has features that allow you to talk to other agents in the same
harness, such as `SendMessage` and Claude Code, feel free to use that instead of
using `herdr agent prompt`, because that is simpler, neater, and easier for you
to work with, and it would differentiate you from me, which is important. If
that doesn't work for any reason, you should continue to use
`herdr agent prompt`.

### Supervise the agent

A pane agent is a subagent I can see. It is not fire-and-forget. Own the result
the same way you own a subagent's result: brief it well, watch it, unblock it,
check its work, and report what actually happened.

Write the opening prompt like a subagent prompt. State the goal, the acceptance
test, and the constraints. Name the files or commands you already know matter.
Tell it to run the tests and report failures verbatim. A pane agent starts with
no memory of our conversation, so include the context it needs.

Then run this loop until the work is done or I redirect you:

1. Send work with `herdr agent prompt <name> "<text>" --wait --timeout <ms>`.
   Set the timeout to match the job. Use several minutes for a real code change.
2. Read the outcome with `herdr agent get <name>` and
   `herdr agent read <name> --source recent-unwrapped --lines 120`.
3. If the state is `blocked`, read the pane before you answer. Decide the
   approval or question yourself when the answer is clear from our task. Ask me
   only when the choice is mine to make.
4. If the state is `unknown`, read the pane. That state does not mean the agent
   finished.
5. Judge the result yourself. Do not repeat the agent's claim that it works.
   Check the diff, run the tests, or read the files it changed. If it is wrong
   or incomplete, prompt the agent again with the specific problem.
6. Stop the loop when the acceptance test passes. Report what changed, what you
   verified, and what you left undone.

Read the pane, not just the final line. If `--lines` will not show you a
complete response, the agent is drawing on the alternate screen. Then ask it to
write its full answer as Markdown to a temporary file and reply with only the
path. Read that file. Use this only as a fallback.

Prefer one agent doing one job well. Start a second pane agent only when the two
jobs are genuinely independent. Tell me both names.
