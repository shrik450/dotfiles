# Audit rules

These rules turn the [Google developer documentation style guide](https://developers.google.com/style/)
into an audit checklist. Apply them to every changed text surface.

The official guide remains the source of truth. Use its
[word list](https://developers.google.com/style/word-list) for specific terms,
spelling, capitalization, and hyphenation.

## 1. Write for the reader

### Use a conversational, respectful tone

Write like a knowledgeable person who wants to help. Use plain, direct
language. Stay friendly without slang, jokes, choppy fragments, forced humor,
or an overly formal tone.

- Use common words instead of formal alternatives.
- Remove filler such as "please note," "at this time," and "it should be noted."
- Do not use `please` in routine instructions.
- Avoid exclamation marks.
- Do not claim that a task is easy, simple, obvious, or trivial. Give the steps
  or facts instead.
- Avoid excessive claims such as "best," "fastest," "seamless," and
  "revolutionary" unless evidence and context support them.

Guide: [Voice and tone](https://developers.google.com/style/tone)

### Address the reader as "you"

Use `you` and `your` for the reader. In instructions, use the imperative form,
where `you` is implied.

- Use: "Select **Save**."
- Do not use: "The user should select **Save**."
- Use `user` only for a person who uses the software that the reader develops.
- Use `we`, `our`, or `us` only for the organization that authors the text.
  Make the organization clear.
- Use third person for software behavior: "The server returns an error."

Guide: [Second person and first person](https://developers.google.com/style/person)

### Prefer active voice and present tense

Name the actor and put the actor before the action when that information helps
the reader.

- Use: "The client sends the request."
- Avoid: "The request is sent by the client."
- Use passive voice only when the actor is unknown, irrelevant, or less
  important than the object.
- Describe current behavior in present tense.
- Use future tense only for an actual future event or a necessary result. Do
  not use `will` for routine product behavior.

Guides: [Active voice](https://developers.google.com/style/voice),
[Present tense](https://developers.google.com/style/tense), and
[Future tense](https://developers.google.com/style/future)

### Use common contractions

Use common contractions such as `you're`, `don't`, `isn't`, and `can't` when
they sound natural. Contractions make text less formal. Negation contractions
also make `not` harder to miss. Do not create nonstandard contractions.

Guide: [Contractions](https://developers.google.com/style/contractions)

## 2. Make the text clear and concise

### Put the main point first

Start each page, section, paragraph, message, and list item with the information
that helps the reader act. Keep one topic in each paragraph.

- Break up walls of text with headings, paragraphs, or lists.
- Keep sentences below 26 words when possible.
- Remove repeated context and words that do not change the meaning.
- Avoid double negatives and exceptions to exceptions.
- Do not start many consecutive sentences with the same phrase.
- Use parallel grammar for items that serve the same purpose.

Guides: [Write accessible documentation](https://developers.google.com/style/accessibility)
and [Paragraph structure](https://developers.google.com/style/paragraph-structure)

### Use precise, literal language

Use each term consistently. Prefer a precise verb over a vague verb and noun
combination.

- Avoid idioms, clichés, metaphors, analogies that depend on culture, and other
  figurative language.
- Avoid vague references such as "the above," "the following thing," and
  "this" without a clear noun.
- Avoid directional references such as "on the right" when structure or a
  label can identify the target.
- Do not anthropomorphize software. State what the system does, not what it
  thinks, wants, knows, or tries to do.
- Avoid jargon. If a necessary term might be unfamiliar, define it on first use
  or link to a trusted definition.

Guides: [Write inclusive documentation](https://developers.google.com/style/inclusive-documentation),
[Jargon](https://developers.google.com/style/jargon), and
[Anthropomorphism](https://developers.google.com/style/anthropomorphism)

### Write timeless text

Describe the product as it works. Avoid words that depend on when the reader
opens the text.

- Replace `currently`, `now`, `new`, and `latest` with a lasting fact.
- Do not pre-announce an unapproved feature or product.
- Use an exact version, date, or status when time matters.

Guides: [Timeless documentation](https://developers.google.com/style/timeless-documentation)
and [Future features](https://developers.google.com/style/future)

### Give direct requirements

Use terms with distinct meanings:

- `must` states a requirement.
- `can` states an ability or option.
- `might` states a possibility.
- An imperative states a required action.
- Avoid `should` when it could mean either a requirement or a recommendation.
- State a recommendation directly and explain why it helps when the reason is
  not clear.

Guide: [Prescriptive documentation](https://developers.google.com/style/prescriptive-documentation)

## 3. Write for a global and inclusive audience

### Use inclusive terms

Choose terms that describe the technical role or action without excluding or
stereotyping people.

- Use gender-neutral language. Use singular `they` when a pronoun is needed.
- Avoid unnecessary references to gender, age, culture, nationality, health,
  or ability.
- Avoid ableist terms such as `crazy`, `insane`, `dumb`, `crippled`, `blind to`,
  and `blind spot`. Name the actual state or problem.
- Avoid violent or graphic metaphors when a precise technical term works.
- Replace terms such as `blacklist` and `whitelist` with `blocklist` and
  `allowlist` when those terms are accurate.
- Replace `master` and `slave` with role-based terms such as `controller` and
  `replica` when those terms are accurate.
- Do not describe people without disabilities as `normal` or `healthy`.
- Use the terms that a community uses for itself. Do not guess when identity
  language matters.

If an established code name or keyword cannot change, format the exact name as
code. Explain it once with the preferred term, and then use the preferred term
in prose.

Guide: [Write inclusive documentation](https://developers.google.com/style/inclusive-documentation)

### Support translation and global readers

Use standard American English spelling and punctuation. Keep grammar and terms
consistent.

- Avoid culture-specific jokes, holidays, sports references, and wordplay.
- Do not use a season to identify a date. Use a month, quarter, or exact date.
- Define unfamiliar abbreviations on first use. Do not define an abbreviation
  that is better known than its expanded form.
- Avoid internet slang and unnecessary Latin abbreviations.

Guides: [Write for a global audience](https://developers.google.com/style/translation),
[Spelling](https://developers.google.com/style/spelling), and
[Abbreviations](https://developers.google.com/style/abbreviations)

## 4. Make content accessible

Meaning must not depend only on color, shape, position, sound, or a pointer.
Use semantic structure and text alternatives.

- Give each meaningful image concise alt text that explains its purpose. Use
  empty alt text for a decorative image.
- Put information from an image, video, or audio clip in equivalent text.
- Use captions, transcripts, or audio descriptions where needed.
- Use semantic headings, lists, tables, labels, notices, and controls.
- Give form controls visible, specific labels. Do not rely on placeholder text
  as the label.
- Make link text meaningful when read without surrounding text. Do not use
  "click here," "here," or "read more" as the link text.
- Explain unexpected link behavior, such as a download or a new tab.
- Avoid adjacent links when no text or punctuation separates them.
- Do not use an ampersand in prose or headings unless it is part of an exact UI
  label or a space-constrained table or diagram label.
- Do not use images of text, code, or terminal output when actual text works.
- Make instructions usable with a keyboard. Do not require pointer-only input.

Guide: [Write accessible documentation](https://developers.google.com/style/accessibility)

## 5. Organize the content

### Use clear headings

- Use sentence case. Capitalize the first word and proper nouns only.
- Do not put a period at the end.
- Make each heading unique and descriptive.
- Start a task heading with a bare infinitive: "Create a cluster"
- Use a noun phrase for a concept heading: "Cluster architecture"
- Avoid starting with an `-ing` form when a direct verb works.
- Keep punctuation simple.
- Avoid links and unnecessary code items in headings.
- Use one level-1 heading for each page.
- Do not skip heading levels or leave a heading without content.

Guide: [Headings and titles](https://developers.google.com/style/headings)

### Choose the correct list

- Use a numbered list for a sequence.
- Use a bulleted list for an unordered set.
- Use a description list for terms and their descriptions.
- Introduce a list with a complete sentence when the context needs one.
- Use sentence case and parallel grammar for all items.
- Use periods for complete sentences. Use no end punctuation for fragments.
  Apply one pattern throughout a list.

Guide: [Lists](https://developers.google.com/style/lists)

### Write procedures as actions

- Use a numbered list for a procedure with more than one step.
- Use an imperative verb at the start of each step.
- Put one main action in each step. Split long or unrelated actions.
- Use a bullet for a procedure with only one step.
- Add `Optional:` at the start of an optional step.
- Give prerequisites and warnings before the action they affect.
- State the location before the action when the reader must work in a specific
  tool or page.
- Prefer one accessible method. If several methods matter, separate them by
  page, heading, or tab.
- Do not repeat a procedure. Link to its source.

Guide: [Procedures](https://developers.google.com/style/procedures)

### Make links and references useful

Use descriptive link text that names the destination or purpose. Use `see` for
a cross-reference. Do not expose a raw URL when a descriptive label works.
Keep link text concise, but include enough context for a link list.

Guide: [Cross-references and linking](https://developers.google.com/style/cross-references)

## 6. Format technical text correctly

### Distinguish code from prose

Use code font for literal or code-related items such as commands, filenames,
paths, parameters, method names, class names, field names, data types,
database elements, environment variables, and text that the reader enters.

- Keep exact code capitalization and spelling.
- Add a descriptive noun when a code element alone reads poorly: "the
  `getUser` method."
- Do not use code font for product names, domain names, IP addresses, or a URL
  that the reader opens in a browser.
- Do not put quotation marks around text that is already in code font.
- Treat a code element as a grammatical unit. Do not add a possessive or plural
  ending directly to the code token when a descriptive noun is clearer.

Guide: [Code in text](https://developers.google.com/style/code-in-text)

### Refer to UI elements by their labels

Focus on the reader's goal. Include UI details only when they help the reader
complete the task.

- Copy the visible label exactly, including its capitalization.
- Bold the label. Do not put it in code font or quotation marks.
- Add the element type only when it prevents confusion: "the **File** menu."
- Use `select` for choices and menu items, `click` for pointer actions, `tap`
  for touch actions, `enter` for a value, and `press` for a keyboard key.
- Use `<kbd>` for keyboard keys. Use the key's standard capitalization.
- Do not identify an unlabeled icon only by its appearance or location. Give it
  an accessible name or tooltip.

Guide: [UI elements and interaction](https://developers.google.com/style/ui-elements)

### Preserve exact names

Use official product, API, and feature names. Check the owning source when the
capitalization or spelling is uncertain. Do not "correct" a fixed command,
field, protocol token, status code, or third-party quotation.

Guide: [Product names](https://developers.google.com/style/product-names)

## 7. Apply grammar and mechanics

### Capitalization

Use sentence case for headings, captions, labels, list items, table headings,
and table cells. Avoid all caps and internal capital letters unless an official
name, abbreviation, or code token requires them. Do not use capitalization as
the only way to convey meaning.

Guide: [Capitalization](https://developers.google.com/style/capitalization)

### Abbreviations

Spell out an unfamiliar abbreviation on first use, followed by the abbreviation
in parentheses. Use the abbreviation after that. Do not add periods to acronyms
or initialisms. Do not use an abbreviation as a verb.

Guide: [Abbreviations](https://developers.google.com/style/abbreviations)

### Numbers

- Spell out zero through nine. Use numerals for 10 and greater.
- Always use numerals for versions, technical quantities, measurements,
  percentages, dimensions, decimals, negative numbers, and numbers compared
  with a number greater than nine in the same sentence.
- Use a comma in numbers with four or more digits: `1,024`.
- Put a zero before a decimal value less than one: `0.5`.
- Use numerals and `%` with no space: `5%`.
- Write ordinal numbers as words: `first`, not `1st`.
- Use a hyphen for a numeric range: `5-10`. Do not mix `from` with a hyphen.
- Use `x` with no spaces for dimensions: `192x192`.

Guide: [Numbers](https://developers.google.com/style/numbers)

### Dates and times

- Write a prose date as `January 19, 2017`.
- Use `YYYY-MM-DD` when a date must contain numbers only.
- Use a 12-hour time with uppercase `AM` or `PM`: `3 PM` or `3:30 PM`.
- Add a time zone only when readers need it. Name the region and UTC offset.
- Do not use a season as a date.

Guide: [Dates and times](https://developers.google.com/style/dates-times)

### Punctuation

- Use the serial comma in a list of three or more items.
- Put a comma after an introductory word or phrase.
- Put a comma before a coordinating conjunction that joins two independent
  clauses, unless both clauses are very short.
- Use straight quotation marks and apostrophes.
- Put commas and periods inside quotation marks. For an exact literal string,
  keep punctuation outside the quotation marks.
- Avoid semicolons when two sentences or a list would read more clearly.
- Use a hyphen to prevent a compound modifier from being misread.
- Do not hyphenate an adverb ending in `-ly`.
- Do not put spaces around a hyphen.
- Avoid parentheses when the information can be a direct sentence.

Guides: [Commas](https://developers.google.com/style/commas),
[Quotation marks](https://developers.google.com/style/quotation-marks), and
[Hyphens](https://developers.google.com/style/hyphens)

## 8. Review text in code and metadata

Apply the same reader-focused rules to strings, comments, prompts, and metadata.
Use these adaptations:

- Errors: state what failed, why when known, and what the reader can do next.
  Do not blame the reader or use vague text such as "Something went wrong."
- Logs: name the actor and action. Keep stable technical values exact.
- CLI help: start command descriptions with a direct verb. Keep parallel forms
  across related commands and options.
- UI text: use sentence case, concise labels, and direct actions. Do not add a
  period to a short button or menu label.
- Comments and docstrings: explain facts in present tense. Remove filler and
  avoid repeating the code.
- Prompts and templates: use explicit, literal instructions. Define the output
  and avoid ambiguous pronouns.
- Tests and fixtures: audit reader-visible or instructional wording. Preserve
  malformed text when the test specifically tests malformed input.
- Identifiers and keys: check spelling, official capitalization, inclusive
  terminology, and domain meaning. Do not apply prose punctuation rules.
- API descriptions and schema text: state behavior in active voice and present
  tense. Keep required, optional, and possible behavior distinct.

Use the relevant rule above for each finding. These adaptations expand the
scope; they do not replace the official guide.
