---
name: google-style-audit
description: Audit any change set against the Google developer documentation style guide. Use for a pull request, branch, commit range, patch, working tree, or named files. Review every changed text surface, including docs, UI copy, errors, logs, comments, prompts, tests, configuration, API descriptions, and terminology in identifiers. The audit report must also follow the guide.
---

# Google developer documentation style audit

Audit the change set that `$ARGUMENTS` identifies. Report style findings only.
Do not edit files, post comments, stage changes, or commit changes.

Read [references/rules.md](references/rules.md) before starting. It contains the
rules for this audit. Use the live guide only to resolve a question that the
reference does not answer.

## Hard requirements

1. Audit every changed text surface, not only documentation files.
2. Apply the rules to your full report, including headings, summaries,
   explanations, and suggested text.
3. Cite each finding with `path:line`, or with the closest available patch
   location when a line number does not exist.
4. Review changed text only. Read unchanged text when you need context or must
   check local consistency.
5. Preserve exact product names, API names, protocol terms, commands, code
   symbols, and quoted third-party text.
6. Do not turn this into a code correctness, design, or formatting review.
7. Do not report a preference as a rule. If the guide permits both forms, do
   not create a finding.

## What counts as text

Inspect all changed text, including:

- Markdown, reStructuredText, HTML, tutorials, READMEs, and release notes.
- UI labels, tooltips, dialogs, notifications, and accessibility labels.
- Errors, warnings, logs, CLI help, command output, and validation messages.
- Code comments, docstrings, API reference comments, and annotations.
- Prompts, templates, emails, generated prose, and localization source text.
- Configuration descriptions, schema descriptions, examples, and sample data.
- Test names and expected strings when a reader sees or learns from them.
- Human-readable words in identifiers, enum members, branch labels, and keys.

Apply prose rules to prose. For identifiers and fixed syntax, apply terminology,
inclusion, capitalization, spelling, and clarity rules where they make sense.
Do not demand sentence punctuation or contractions inside an identifier.

Flag non-inclusive terms in new identifiers. If compatibility requires an
existing fixed term, suggest preferred wording around the exact code term.
Format the exact term as code in the suggested text.

Skip binary content, lockfiles, hashes, and machine-only generated data. State
any skipped text surface in the scope summary. If a changed source template
produces repeated text, report the source once and list the affected outputs.

## Resolve the scope

Interpret `$ARGUMENTS` by its form:

- No argument or `working-tree`: inspect tracked staged and unstaged changes.
  Also inspect every untracked file from
  `git ls-files --others --exclude-standard`.
- A pull request number or URL: use `gh pr view` and `gh pr diff`.
- `branch`: compare `HEAD` with the repository's default branch by using a
  three-dot diff.
- A commit, tag, or commit range: inspect the corresponding `git diff`.
- A path or list of paths: inspect those files or their changes, as requested.
- A patch or user-provided set: inspect exactly that set.

If the input could name more than one scope, ask one short question before the
audit. Do not silently choose a scope.

For a working tree, combine these sources without losing staged changes:

```bash
git diff
git diff --cached
git ls-files --others --exclude-standard
```

For a pull request, read its title and description as context. Audit them only
when the user includes PR metadata in the requested scope.

## Audit process

### 1. Build a text inventory

List every changed file and identify each text surface in it. Do not infer that
a source file contains no prose. Search its comments, strings, help text,
errors, logs, prompts, labels, fixture text, and test expectations.

For deleted text, report a finding only when the deletion makes the remaining
or replacement text violate the guide.

### 2. Check meaning before mechanics

Use the rule order in `references/rules.md`:

1. Inclusive, accessible, and global language.
2. Clear meaning, audience, voice, and tone.
3. Structure, navigation, procedures, and links.
4. Technical terms, UI text, and code formatting.
5. Grammar, spelling, capitalization, numbers, and punctuation.

Check the Google word list for a disputed term:
<https://developers.google.com/style/word-list>.

### 3. Validate each candidate

Before reporting a candidate, confirm all of the following:

- The relevant text changed in this scope.
- A rule in the reference or live guide supports the finding.
- The suggested text keeps the original technical meaning.
- The suggestion does not rename a fixed API, product, command, or quoted term.
- The finding is not only a code style or personal taste concern.

Combine repeated instances when one source change fixes them all. List every
location in the combined finding.

### 4. Audit your report

Before sending the report, apply the same rules to every sentence you wrote.
Use sentence case, active voice, second person where needed, direct language,
serial commas, descriptive links, and straight quotation marks. Remove jargon,
idioms, filler, unnecessary future tense, and non-inclusive terms.

## Output

Use this structure:

```markdown
## Scope

Reviewed <exact scope>. Checked <text surfaces>. Skipped <items and reason>, if
anything was skipped.

## Findings

1. `path:line` - Short finding in sentence case
   - Current: "<exact changed text>"
   - Use: "<suggested text>"
   - Rule: <rule name and direct guide URL>
   - Reason: <one short explanation tied to the reader>

## Result

Found N style issues across N changed text surfaces.
```

Order findings by reader impact. Put harmful or exclusionary language first,
then unclear meaning, accessibility barriers, structural issues, terminology,
and mechanics.

When a term or product name needs verification, use `Check` instead of `Use`.
State the exact fact that the author must verify. Do not invent a replacement.

If there are no findings, write:

```markdown
## Result

No Google developer documentation style issues found in the changed text.
```

Still include the scope and the text surfaces you checked. Do not add praise,
a score, a general code review, or a list of unchanged text that follows the
guide.
